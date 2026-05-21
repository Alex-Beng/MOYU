package com.moyu.controller

import android.content.Context
import android.graphics.Bitmap
import com.moyu.common.DetectionResult
import com.moyu.common.Frame
import com.moyu.device.CubeApi
import com.moyu.device.MockCubeApi
import com.moyu.ocr.BubbleSegmentor
import com.moyu.ocr.MoveClassifier
import com.moyu.ocr.MoveParser
import com.moyu.recipe.RecipeConfig
import com.moyu.recipe.RecipeLoader
import com.moyu.service.FloatLogService
import com.moyu.service.ScreenCaptureService
import com.moyu.solve.CfopSolver
import com.moyu.vision.Detector
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class Controller(private val context: Context) {
    internal val recipe: RecipeConfig = RecipeLoader.load(context)
    private val cubeApi = CubeApi()
    private val mockCubeApi = MockCubeApi()
    internal val classifier = MoveClassifier(context)
    internal val detector = Detector(context, recipe)
    internal val cfopSolver = CfopSolver()

    var state: String = "init"
    var mode: String = recipe.mode

    var scrambleSeenMove = false
    var noScrambleCnt = 0

    private var running = false
    private var useMockApi = false
    private val moveChannel = kotlinx.coroutines.channels.Channel<String>(kotlinx.coroutines.channels.Channel.UNLIMITED)

    suspend fun run() {
        running = true

        cfopSolver.init()
        log("CFOP 求解器初始化完成")

        log("启动状态机: mode=$mode")
        val handlers = getHandlers(mode)

        coroutineScope {
            launch { stateMachine(handlers) }
            launch { moveDispatchLoop() }
        }
    }

    fun stop() {
        running = false
    }

    private suspend fun stateMachine(handlers: Map<String, StateHandler>) {
        while (running) {
            val handler = handlers[state]
            if (handler != null) {
                val next = handler(this)
                if (next != null && next != state) {
                    log("状态: $state → $next")
                    state = next
                    applyDelay()
                }
            } else {
                delay(1000)
            }
        }
    }

    private suspend fun moveDispatchLoop() {
        for (moves in moveChannel) {
            val api = if (useMockApi) mockCubeApi else cubeApi
            val ok = api.sendMoves(moves)
            if (!ok) {
                log("发送失败，重试...")
                delay(1000)
                api.sendMoves(moves)
            }
            if (useMockApi) {
                log("Mock: $moves")
            }
        }
    }

    fun log(msg: String) {
        FloatLogService.instance?.appendLog(msg)
    }

    suspend fun waitForUi(featureName: String, timeoutMs: Long = 30_000L): DetectionResult? {
        val start = System.currentTimeMillis()
        while (running && System.currentTimeMillis() - start < timeoutMs) {
            val frame = lastFrame()?.bitmap ?: run { delay(500); continue }
            val result = detector.detect(frame, featureName)
            if (result.matched) return result
            delay(500)
        }
        return null
    }

    suspend fun clickFeature(featureName: String): Boolean {
        val result = detector.detect(lastFrame()?.bitmap ?: return false, featureName)
        if (!result.matched) return false
        com.moyu.service.MoyuAccessibilityService.instance?.tap(result.centerX, result.centerY)
        log("点击: $featureName")
        delay(500)
        return true
    }

    fun lastFrame(): Frame? = ScreenCaptureService.instance?.lastFrame()

    suspend fun queueMoves(notation: String) {
        if (notation.isNotBlank()) moveChannel.send(notation)
    }

    suspend fun getFacelets(): String = if (useMockApi) mockCubeApi.getFacelets() else cubeApi.getFacelets()

    suspend fun applyDelay() {
        val delayMs = when (state) {
            "scramble" -> recipe.scrambleDelay
            "solve" -> recipe.solveDelay
            else -> null
        }
        if (delayMs != null) delay(delayMs.toLong())
    }

    internal val solver: CfopSolver get() = cfopSolver
    internal fun lastFrameBitmap(): Bitmap? = lastFrame()?.bitmap
}

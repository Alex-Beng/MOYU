package com.moyu.controller

import android.content.Context
import android.graphics.Bitmap
import com.moyu.common.CubeCommand
import com.moyu.common.CubeDelay
import com.moyu.common.CubeMove
import com.moyu.common.CubeMoveStr
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

class Controller(private val context: Context, recipePath: String = "rank.json") {
    internal val recipe: RecipeConfig = run {
        val cfg = RecipeLoader.load(context, recipePath)
        log("食谱加载完成: ${cfg.name} mode=${cfg.mode} ${cfg.ui.size} 个UI特征")
        cfg
    }
    private val cubeApi = CubeApi()
    private val mockCubeApi = MockCubeApi()
    internal val classifier: MoveClassifier = run {
        val clf = MoveClassifier(context)
        log("TFLite 模型加载完成")
        clf
    }
    internal val detector = run {
        val det = Detector(context, recipe)
        log("模板匹配检测器就绪 (${recipe.ui.size} 个模板)")
        det
    }
    internal val cfopSolver = CfopSolver()

    var state: String = "init"
    var mode: String = recipe.mode

    var scrambleSeenMove = false
    var noScrambleCnt = 0

    var running = false
        private set
    private var useMockApi = false
    @Volatile var paused = false
    var pendingRestart: String? = null
    private val moveChannel = kotlinx.coroutines.channels.Channel<Any>(kotlinx.coroutines.channels.Channel.UNLIMITED)

    suspend fun run() {
        running = true
        log("Controller.run() 启动")

        CfopSolver.DEBUG = true
        CfopSolver.logFn = { msg -> log(msg) }
        detector.logFn = { msg -> log(msg) }
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

    fun pause() {
        paused = true
        log("⏸ 已暂停")
    }

    fun resume() {
        paused = false
        log("▶ 已继续")
    }

    fun restartAt(stateName: String) {
        pendingRestart = stateName
        stop()
    }

    fun isPaused(): Boolean = paused

    private suspend fun stateMachine(handlers: Map<String, StateHandler>) {
        while (running) {
            while (paused && running) delay(200)
            if (!running) break
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

    @Suppress("UNCHECKED_CAST")
    private suspend fun moveDispatchLoop() {
        for (item in moveChannel) {
            val api = if (useMockApi) mockCubeApi else cubeApi
            val ok = when (item) {
                is String -> api.sendMoves(item)
                is List<*> -> api.sendMovesRaw(item as List<CubeCommand>)
                else -> false
            }
            if (!ok) {
                log("发送失败，重试...")
                delay(1000)
                when (item) {
                    is String -> api.sendMoves(item)
                    is List<*> -> api.sendMovesRaw(item as List<CubeCommand>)
                }
            }
            if (useMockApi) {
                log("Mock: $item")
            }
        }
    }

    fun log(msg: String) {
        FloatLogService.instance?.appendLog(msg)
    }

    suspend fun waitForUi(featureName: String, timeoutMs: Long = 30_000L): DetectionResult? {
        val start = System.currentTimeMillis()
        var noFrameCount = 0
        while (running && System.currentTimeMillis() - start < timeoutMs) {
            val frame = lastFrame()?.bitmap ?: run {
                noFrameCount++
                if (noFrameCount % 5 == 1) log("waitForUi $featureName: 无帧 ×$noFrameCount")
                delay(500); continue
            }
            noFrameCount = 0
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

    suspend fun queueCommands(commands: List<CubeCommand>) {
        if (commands.isNotEmpty()) moveChannel.send(commands)
    }

    fun buildPhasedMoves(result: CfopSolver.SolveResult): List<CubeCommand> {
        val steps = mutableListOf<CubeCommand>()

        val useStr = recipe.moveFormat == "str"

        fun parseToCommands(notation: String): List<CubeCommand> {
            if (notation.isBlank()) return emptyList()
            return if (useStr) {
                notation.split(" ").filter { it.isNotBlank() }.map { CubeMoveStr(it) }
            } else {
                parseNotationToList(notation)
            }
        }

        if (result.cross.isNotEmpty()) {
            if (recipe.crossDelay != null && recipe.crossDelay > 0) steps.add(CubeDelay(recipe.crossDelay))
            steps.addAll(parseToCommands(result.cross))
        }

        if (result.f2l.isNotEmpty()) {
            if (recipe.f2lDelay != null && recipe.f2lDelay > 0) steps.add(CubeDelay(recipe.f2lDelay))
            steps.addAll(parseToCommands(result.f2l))
        }

        if (result.alll != null && result.alll.isNotEmpty()) {
            steps.addAll(parseToCommands(result.alll))
        } else {
            if (result.oll != null && result.oll.isNotEmpty()) {
                if (recipe.ollDelay != null && recipe.ollDelay > 0) steps.add(CubeDelay(recipe.ollDelay))
                steps.addAll(parseToCommands(result.oll))
            }
            if (result.pll != null && result.pll.isNotEmpty()) {
                steps.addAll(parseToCommands(result.pll))
            }
        }

        return steps
    }

    private fun parseNotationToList(notation: String): List<CubeMove> {
        return CubeApi().parseMoveNotation(notation)
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

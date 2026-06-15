package com.moyu.service

import android.content.Intent
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.moyu.controller.Controller
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class ControllerService : LifecycleService() {
    private var controller: Controller? = null
    private var controllerJob: kotlinx.coroutines.Job? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)

        val recipePath = intent?.getStringExtra("recipe") ?: "rank.json"

        controllerJob?.cancel()
        controller?.stop()
        controller = null

        FloatLogService.instance?.appendLog("ControllerService 启动")
        FloatLogService.instance?.appendLog("recipe: $recipePath")
        FloatLogService.instance?.appendLog("开始初始化 Controller...")
        val c = Controller(applicationContext, recipePath)
        controller = c
        FloatLogService.instance?.appendLog("Controller 构造完成")
        FloatLogService.instance?.bindController(c)
        controllerJob = lifecycleScope.launch(Dispatchers.Default) { c.run() }
        lifecycleScope.launch(Dispatchers.Default) {
            while (controller === c) {
                delay(600)
                val restartState = c.pendingRestart
                if (restartState != null && !c.running) {
                    FloatLogService.instance?.appendLog("重启 → $restartState")
                    val newController = Controller(applicationContext, recipePath)
                    newController.state = restartState
                    controller = newController
                    FloatLogService.instance?.bindController(newController)
                    controllerJob?.cancel()
                    controllerJob = launch(Dispatchers.Default) { newController.run() }
                }
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        controllerJob?.cancel()
        controller?.stop()
        super.onDestroy()
    }
}

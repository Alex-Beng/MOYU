package com.moyu.service

import android.content.Intent
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.lifecycleScope
import com.moyu.controller.Controller
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class ControllerService : LifecycleService() {
    private var controller: Controller? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        if (controller == null) {
            controller = Controller(applicationContext)
            lifecycleScope.launch(Dispatchers.Default) {
                controller!!.run()
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        controller?.stop()
        super.onDestroy()
    }
}

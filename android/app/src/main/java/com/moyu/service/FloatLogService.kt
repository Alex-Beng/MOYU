package com.moyu.service

import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.MotionEvent
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.TextView

class FloatLogService : Service() {
    companion object {
        @Volatile var instance: FloatLogService? = null
    }

    private lateinit var wm: WindowManager
    private lateinit var overlayView: FrameLayout
    private lateinit var logView: TextView
    private var isExpanded = false
    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    private val handler = Handler(Looper.getMainLooper())

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        instance = this
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        showOverlay()
    }

    override fun onDestroy() {
        instance = null
        wm.removeView(overlayView)
        super.onDestroy()
    }

    fun appendLog(msg: String) {
        handler.post {
            val lines = logView.text.split("\n").takeLast(19)
            logView.text = (lines + msg).joinToString("\n")
        }
    }

    private fun showOverlay() {
        overlayView = FrameLayout(this)
        overlayView.setBackgroundColor(0xCC000000.toInt())

        logView = TextView(this).apply {
            text = "MOYU 启动完成"
            setTextColor(0xFF00FF00.toInt())
            textSize = 12f
            setPadding(8, 8, 8, 8)
        }
        overlayView.addView(logView, FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT,
            FrameLayout.LayoutParams.WRAP_CONTENT
        ))

        overlayView.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    val params = overlayView.layoutParams as WindowManager.LayoutParams
                    initialX = params.x
                    initialY = params.y
                    initialTouchX = event.rawX
                    initialTouchY = event.rawY
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val params = overlayView.layoutParams as WindowManager.LayoutParams
                    params.x = initialX + (event.rawX - initialTouchX).toInt()
                    params.y = initialY + (event.rawY - initialTouchY).toInt()
                    wm.updateViewLayout(overlayView, params)
                    true
                }
                MotionEvent.ACTION_UP -> {
                    val dx = event.rawX - initialTouchX
                    val dy = event.rawY - initialTouchY
                    if (dx * dx + dy * dy < 100) toggleExpand()
                    true
                }
                else -> false
            }
        }

        val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            flags,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 0
            y = 200
        }

        wm.addView(overlayView, params)
    }

    private fun toggleExpand() {
        isExpanded = !isExpanded
        val params = overlayView.layoutParams as WindowManager.LayoutParams
        if (isExpanded) {
            params.width = 600
            params.height = 800
            logView.textSize = 12f
        } else {
            params.width = WindowManager.LayoutParams.WRAP_CONTENT
            params.height = WindowManager.LayoutParams.WRAP_CONTENT
            logView.text = "MOYU 运行中"
        }
        wm.updateViewLayout(overlayView, params)
    }
}

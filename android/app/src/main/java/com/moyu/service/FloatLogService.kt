package com.moyu.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.text.SpannableString
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.view.Gravity
import android.view.MotionEvent
import android.view.WindowManager
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import com.moyu.controller.Controller
import java.text.SimpleDateFormat
import java.util.Date

class FloatLogService : Service() {

    companion object {
        var instance: FloatLogService? = null
            private set
        private const val NOTIFICATION_ID = 1000
    }

    private lateinit var wm: WindowManager
    private lateinit var overlayView: LinearLayout
    private lateinit var scrollView: ScrollView
    private lateinit var logView: TextView
    private lateinit var btnPause: TextView
    private lateinit var btnStop: TextView
    private lateinit var btnRestart: TextView
    private lateinit var lblRestartState: TextView
    private lateinit var frameThumb: ImageView
    private lateinit var lastLogView: TextView
    private val thumbHandler = Handler(Looper.getMainLooper())
    private var thumbRunnable: Runnable? = null
    private var isExpanded = false
    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    var controller: Controller? = null
    private var restartStateIdx = 0
    private val restartStates = listOf("init", "scramble", "solve")
    private val restartHandler = Handler(Looper.getMainLooper())
    private var restartConfirmRunnable: Runnable? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        instance = this
        startForeground(NOTIFICATION_ID, createNotification())
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        showOverlay()
    }

    override fun onDestroy() {
        instance = null
        thumbRunnable?.let { thumbHandler.removeCallbacks(it) }
        if (::overlayView.isInitialized) wm.removeView(overlayView)
        super.onDestroy()
    }

    fun bindController(c: Controller) {
        controller = c
    }

    private fun createNotification(): Notification {
        val channelId = "moyu_float"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "MOYU", NotificationManager.IMPORTANCE_LOW)
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
        return Notification.Builder(this, channelId)
            .setContentTitle("MOYU").setContentText("运行中")
            .setSmallIcon(android.R.drawable.ic_menu_info_details).setOngoing(true).build()
    }

    fun appendLog(msg: String) {
        android.util.Log.d("FloatLog", msg)
        logView.post {
            val ts = SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault()).format(Date())
            val line = "$ts $msg"
            val current = logView.text.toString()
            val lines = current.split("\n").takeLast(200)
            val newText = (lines + line).joinToString("\n")
            logView.text = ""
            val ss = SpannableString(newText)
            ss.setSpan(ForegroundColorSpan(Color.GREEN), 0, ss.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            logView.setText(ss)
            scrollView.post { scrollView.fullScroll(ScrollView.FOCUS_DOWN) }
            lastLogView.text = msg
        }
    }

    private fun makeBtn(label: String, bgColor: Int): TextView {
        return TextView(this).apply {
            text = label
            setTextColor(Color.WHITE)
            setBackgroundColor(bgColor)
            textSize = 11f
            setPadding(12, 4, 12, 4)
            gravity = Gravity.CENTER
        }
    }

    private fun showOverlay() {
        overlayView = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(0xCC000000.toInt())
        }

        // ── Control bar ──
        val controlBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(4, 4, 4, 4)
        }

        btnPause = makeBtn("暂停", 0xFF444444.toInt()).apply {
            setOnClickListener {
                val c = controller
                if (c != null) {
                    if (c.isPaused()) {
                        c.resume()
                        post { btnPause.text = "暂停" }
                    } else {
                        c.pause()
                        post { btnPause.text = "继续" }
                    }
                }
            }
        }
        controlBar.addView(btnPause, LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { rightMargin = 6 })

        btnStop = makeBtn("停止", 0xFFAA3333.toInt()).apply {
            setOnClickListener {
                controller?.stop()
                appendLog("控制器已停止")
            }
        }
        controlBar.addView(btnStop, LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { rightMargin = 6 })

        lblRestartState = TextView(this).apply {
            text = "init"
            setTextColor(Color.YELLOW)
            textSize = 10f
            setPadding(4, 0, 4, 0)
        }
        controlBar.addView(lblRestartState)

        btnRestart = makeBtn("重启", 0xFF3366AA.toInt()).apply {
            setOnClickListener {
                restartStateIdx = (restartStateIdx + 1) % restartStates.size
                val s = restartStates[restartStateIdx]
                post { lblRestartState.text = s }
                restartConfirmRunnable?.let { restartHandler.removeCallbacks(it) }
                restartConfirmRunnable = Runnable {
                    val c = controller
                    if (c != null) {
                        post { appendLog("重启 → $s") }
                        c.restartAt(s)
                    }
                }
                restartHandler.postDelayed(restartConfirmRunnable!!, 1500)
            }
        }
        controlBar.addView(btnRestart, LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT).apply { leftMargin = 6 })

        overlayView.addView(controlBar, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        // ── Last log line ──
        lastLogView = TextView(this).apply {
            setTextColor(Color.CYAN)
            textSize = 10f
            setPadding(8, 2, 8, 2)
            maxLines = 1
            ellipsize = android.text.TextUtils.TruncateAt.START
            text = ""
        }
        overlayView.addView(lastLogView, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        // ── Frame thumbnail ──
        frameThumb = ImageView(this).apply {
            scaleType = ImageView.ScaleType.FIT_CENTER
            setBackgroundColor(0xFF111111.toInt())
            contentDescription = "screen"
        }
        overlayView.addView(frameThumb, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 120
        ))

        // ── Log area ──
        logView = TextView(this).apply {
            text = "MOYU 启动完成"
            setTextColor(Color.GREEN)
            textSize = 12f
            setPadding(8, 8, 8, 8)
        }
        scrollView = ScrollView(this).apply {
            addView(logView, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        }
        overlayView.addView(scrollView, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 400))

        scrollView.visibility = android.view.View.GONE

        // Drag-to-move on control bar only (not on log area)
        controlBar.setOnTouchListener { _, event ->
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

        val dpW = (300 * resources.displayMetrics.density).toInt()
        val params = WindowManager.LayoutParams(
            dpW, WindowManager.LayoutParams.WRAP_CONTENT, flags,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 0; y = 0
        }
        wm.addView(overlayView, params)
        startThumbUpdater()
    }

    private fun startThumbUpdater() {
        val r = object : Runnable {
            override fun run() {
                val raw = ScreenCaptureService.instance?.lastFrame()?.bitmap
                val bmp = if (raw != null && !raw.isRecycled) raw else null
                if (bmp != null && !bmp.isRecycled) {
                    val targetW = overlayView.width.takeIf { it > 0 } ?: 300
                    val targetH = targetW * bmp.height / bmp.width
                    val thumb = android.graphics.Bitmap.createScaledBitmap(bmp, targetW, targetH, false)
                    frameThumb.setImageBitmap(thumb)
                }
                thumbHandler.postDelayed(this, 500)
            }
        }
        thumbRunnable = r
        thumbHandler.post(r)
    }

    private fun toggleExpand() {
        isExpanded = !isExpanded
        val params = overlayView.layoutParams as WindowManager.LayoutParams
        if (isExpanded) {
            scrollView.visibility = android.view.View.VISIBLE
            params.height = WindowManager.LayoutParams.WRAP_CONTENT
        } else {
            scrollView.visibility = android.view.View.GONE
            params.height = WindowManager.LayoutParams.WRAP_CONTENT
        }
        wm.updateViewLayout(overlayView, params)
    }
}

package com.moyu.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import com.moyu.common.Frame

class ScreenCaptureService : Service() {

    companion object {
        var instance: ScreenCaptureService? = null
            private set
        const val EXTRA_RESULT_CODE = "result_code"
        const val EXTRA_RESULT_DATA = "result_data"
        private const val NOTIFICATION_ID = 1002
    }

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private var captureThread: HandlerThread? = null
    private var captureHandler: Handler? = null
    @Volatile private var capturing = false
    private var recentFrame: Frame? = null
    private val frameLock = Any()
    private var recipeExtra: String? = null
    var screenW = 0
        private set
    var screenH = 0
        private set
    private var screenDpi = 0

    private val imageListener = ImageReader.OnImageAvailableListener { reader ->
        if (!capturing) return@OnImageAvailableListener
        try {
            val image = reader.acquireLatestImage() ?: return@OnImageAvailableListener
            val imgW = image.width
            val imgH = image.height
            val planes = image.planes
            val buffer = planes[0].buffer
            val pixelStride = planes[0].pixelStride
            val rowStride = planes[0].rowStride
            val rowPadding = rowStride - pixelStride * imgW
            val bmp = Bitmap.createBitmap(imgW + rowPadding / pixelStride, imgH, Bitmap.Config.ARGB_8888)
            bmp.copyPixelsFromBuffer(buffer)
            image.close()
            val newFrame = Frame(bmp, System.currentTimeMillis())
            val old = synchronized(frameLock) {
                val prev = recentFrame?.bitmap
                recentFrame = newFrame
                prev
            }
            if (old != null && !old.isRecycled) old.recycle()
        } catch (_: Throwable) {}
    }

    private val mediaProjectionCallback = object : MediaProjection.Callback() {
        override fun onCapturedContentResize(width: Int, height: Int) {
            if (capturing && (width != screenW || height != screenH)) {
                FloatLogService.instance?.appendLog("截屏内容尺寸变化: ${screenW}x${screenH} → ${width}x${height}，调整截屏")
                resizeCapture(width, height)
            }
        }
        override fun onStop() {
            FloatLogService.instance?.appendLog("MediaProjection 已停止")
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        instance = this
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onDestroy() {
        instance = null
        teardownCapture()
        captureThread?.quitSafely()
        mediaProjection?.stop()
        super.onDestroy()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        FloatLogService.instance?.appendLog("ScreenCapture onStartCommand intent=${intent != null}")
        recipeExtra = intent?.getStringExtra("recipe")
        if (intent != null && mediaProjection == null) {
            val resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0)
            val data = intent.getParcelableExtra(EXTRA_RESULT_DATA, Intent::class.java)
            FloatLogService.instance?.appendLog("ScreenCapture resultCode=$resultCode data=${data != null}")
            if (resultCode == -1 && data != null) {
                val mpm = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
                mediaProjection = mpm.getMediaProjection(resultCode, data)
                captureThread = HandlerThread("capture").also { it.start() }
                captureHandler = Handler(captureThread!!.looper)
                mediaProjection!!.registerCallback(mediaProjectionCallback, captureHandler)
                setupCapture()
                startController()
            }
        }
        return START_STICKY
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        if (mediaProjection != null) {
            val (w, h) = getScreenSize()
            if (w != screenW || h != screenH) {
                FloatLogService.instance?.appendLog("屏幕旋转: ${screenW}x${screenH} → ${w}x${h}，调整截屏")
                resizeCapture(w, h)
            }
        }
    }

    private fun getScreenSize(): Pair<Int, Int> {
        screenDpi = resources.displayMetrics.densityDpi
        val wm = getSystemService(WINDOW_SERVICE) as android.view.WindowManager
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val metrics = wm.currentWindowMetrics
            Pair(metrics.bounds.width(), metrics.bounds.height())
        } else {
            @Suppress("DEPRECATION")
            val outSize = android.graphics.Point()
            wm.defaultDisplay.getRealSize(outSize)
            Pair(outSize.x, outSize.y)
        }
    }

    private var captureStartTime = 0L
    val captureStartTimeMs get() = captureStartTime

    private fun setupCapture() {
        val mp = mediaProjection ?: return
        val handler = captureHandler ?: return
        try {
            val (w, h) = getScreenSize()
            screenW = w
            screenH = h
            screenDpi = resources.displayMetrics.densityDpi
            captureStartTime = System.currentTimeMillis()

            val reader = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2)
            val vd = mp.createVirtualDisplay(
                "moyu", w, h, screenDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                reader.surface, null, null
            )
            reader.setOnImageAvailableListener(imageListener, handler)

            imageReader = reader
            virtualDisplay = vd
            capturing = true
            FloatLogService.instance?.appendLog("截屏服务已启动 (${w}x${h})")
        } catch (e: Exception) {
            FloatLogService.instance?.appendLog("截屏启动失败: ${e.message}")
        }
    }

    private fun resizeCapture(w: Int, h: Int) {
        screenDpi = resources.displayMetrics.densityDpi
        try {
            val newReader = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2)
            newReader.setOnImageAvailableListener(imageListener, captureHandler)
            virtualDisplay?.resize(w, h, screenDpi)
            virtualDisplay?.setSurface(newReader.surface)
            imageReader?.close()
            imageReader = newReader
            screenW = w
            screenH = h
            captureStartTime = System.currentTimeMillis()
            FloatLogService.instance?.appendLog("截屏尺寸已调整为 ${w}x${h}")
        } catch (e: Exception) {
            FloatLogService.instance?.appendLog("截屏调整失败: ${e.message}")
        }
    }

    private fun teardownCapture() {
        capturing = false
        Thread.sleep(50)
        virtualDisplay?.release()
        virtualDisplay = null
        imageReader?.close()
        imageReader = null
        synchronized(frameLock) { recentFrame = null }
    }

    fun lastFrame(): Frame? = synchronized(frameLock) {
        val f = recentFrame ?: return null
        if (f.bitmap.isRecycled) return null
        try {
            Frame(f.bitmap.copy(f.bitmap.config ?: Bitmap.Config.ARGB_8888, false), f.timestampMs)
        } catch (_: Exception) { null }
    }

    private fun startController() {
        FloatLogService.instance?.appendLog("正在启动控制器...")
        val intent = Intent(this, ControllerService::class.java)
        recipeExtra?.let { intent.putExtra("recipe", it) }
        startService(intent)
    }

    private fun createNotification(): Notification {
        val channelId = "moyu_capture"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "MOYU 截屏",
                NotificationManager.IMPORTANCE_LOW
            )
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
        return Notification.Builder(this, channelId)
            .setContentTitle("MOYU")
            .setContentText("屏幕捕获中")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setOngoing(true)
            .build()
    }
}

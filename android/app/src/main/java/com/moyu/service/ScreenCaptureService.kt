package com.moyu.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.PixelFormat
import java.nio.ByteBuffer
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
    @Volatile private var projectionStopped = false
    private var recentFrame: Frame? = null
    private val frameLock = Any()
    private var recipeExtra: String? = null
    var screenW = 0
        private set
    var screenH = 0
        private set
    private var screenDpi = 0
    private var contiguousBuf: ByteBuffer? = null

    private val imageListener = ImageReader.OnImageAvailableListener { reader ->
        if (!capturing) return@OnImageAvailableListener
        val image = reader.acquireLatestImage() ?: return@OnImageAvailableListener
        if (!capturing) { image.close(); return@OnImageAvailableListener }
        try {
            val imgW = image.width
            val imgH = image.height
            val planes = image.planes
            if (planes.isEmpty()) return@OnImageAvailableListener
            val buffer = planes[0].buffer
            val pixelStride = planes[0].pixelStride
            val rowStride = planes[0].rowStride
            val bmp = Bitmap.createBitmap(imgW, imgH, Bitmap.Config.ARGB_8888)
            val rowBytes = imgW * pixelStride
            val totalBytes = rowBytes * imgH
            val cont = contiguousBuf
            if (cont == null || cont.capacity() < totalBytes) {
                contiguousBuf = ByteBuffer.allocateDirect(totalBytes)
            }
            val buf = contiguousBuf!!
            buf.rewind()
            buffer.rewind()
            for (y in 0 until imgH) {
                buffer.position(y * rowStride)
                val row = buffer.slice()
                row.limit(rowBytes)
                buf.put(row)
            }
            buf.rewind()
            bmp.copyPixelsFromBuffer(buf)
            val newFrame = Frame(bmp, System.currentTimeMillis())
            val old = synchronized(frameLock) {
                val prev = recentFrame?.bitmap
                recentFrame = newFrame
                prev
            }
            if (old != null && !old.isRecycled) old.recycle()
        } catch (_: Throwable) {
        } finally {
            image.close()
        }
    }

    private val mediaProjectionCallback = object : MediaProjection.Callback() {
        override fun onCapturedContentResize(width: Int, height: Int) {
            if (capturing && (width != screenW || height != screenH)) {
                FloatLogService.instance?.appendLog("截屏内容尺寸变化: ${screenW}x${screenH} → ${width}x${height}，调整截屏")
                resizeCapture(width, height)
            }
        }
        override fun onStop() {
            FloatLogService.instance?.appendLog("MediaProjection 已停止，截屏终止")
            projectionStopped = true
            teardownCapture()
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
        captureHandler?.post {
            virtualDisplay?.release()
            virtualDisplay = null
            imageReader?.close()
            imageReader = null
            contiguousBuf = null
            synchronized(frameLock) { recentFrame = null }
        }
        captureThread?.quitSafely()
        captureThread?.join(500)
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
                // Clean up old thread if restarting after MediaProjection stop
                captureThread?.quitSafely()
                captureThread = null
                captureHandler = null

                val mpm = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
                mediaProjection = mpm.getMediaProjection(resultCode, data)
                captureThread = HandlerThread("capture").also { it.start() }
                captureHandler = Handler(captureThread!!.looper)
                mediaProjection!!.registerCallback(mediaProjectionCallback, captureHandler)
                projectionStopped = false
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
        val handler = captureHandler ?: return
        handler.post {
            try {
                val oldReader = imageReader
                val newReader = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2)
                newReader.setOnImageAvailableListener(imageListener, handler)
                virtualDisplay?.resize(w, h, screenDpi)
                virtualDisplay?.setSurface(newReader.surface)
                imageReader = newReader
                contiguousBuf = null
                oldReader?.close()
                screenW = w
                screenH = h
                captureStartTime = System.currentTimeMillis()
                FloatLogService.instance?.appendLog("截屏尺寸已调整为 ${w}x${h}")
            } catch (e: Exception) {
                FloatLogService.instance?.appendLog("截屏调整失败: ${e.message}")
            }
        }
    }

    private fun teardownCapture() {
        capturing = false
    }

    fun lastFrame(): Frame? = synchronized(frameLock) {
        val f = recentFrame ?: return null
        if (f.bitmap.isRecycled) return null
        try {
            Frame(f.bitmap.copy(f.bitmap.config ?: Bitmap.Config.ARGB_8888, false), f.timestampMs)
                                                                                                                                                                           } catch (_: Exception) { null }
    }

    fun <T> useFrame(action: (Bitmap) -> T): T? {
        val copy = synchronized(frameLock) {
            val f = recentFrame ?: return@useFrame null
            if (f.bitmap.isRecycled) return@useFrame null
            try {
                f.bitmap.copy(f.bitmap.config ?: Bitmap.Config.ARGB_8888, false)
            } catch (_: Exception) { null }
        } ?: return null
        return try {
            action(copy)
        } finally {
            if (!copy.isRecycled) copy.recycle()
        }
    }

    fun isProjectionRunning(): Boolean = capturing && !projectionStopped

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

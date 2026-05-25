package com.moyu.service

import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
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
import java.util.concurrent.atomic.AtomicReference

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
    private var recentFrame: Frame? = null
    private var recipeExtra: String? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        instance = this
        startForeground(NOTIFICATION_ID, createNotification())
    }

    override fun onDestroy() {
        instance = null
        virtualDisplay?.release()
        imageReader?.close()
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
                try {
                    val wm = getSystemService(WINDOW_SERVICE) as android.view.WindowManager
                    val w = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        val bounds = wm.currentWindowMetrics.bounds; bounds.width()
                    } else {
                        wm.defaultDisplay.width
                    }
                    val h = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        val bounds = wm.currentWindowMetrics.bounds; bounds.height()
                    } else {
                        wm.defaultDisplay.height
                    }
                    imageReader = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2)
                    virtualDisplay = mediaProjection!!.createVirtualDisplay("moyu", w, h, resources.displayMetrics.densityDpi,
                        DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, imageReader!!.surface, null, null)
                    captureThread = HandlerThread("capture").also { it.start() }
                    captureHandler = Handler(captureThread!!.looper)
                    imageReader!!.setOnImageAvailableListener({ reader ->
                        val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
                        val planes = image.planes
                        val buffer = planes[0].buffer
                        val pixelStride = planes[0].pixelStride
                        val rowStride = planes[0].rowStride
                        val rowPadding = rowStride - pixelStride * w
                        val bmp = Bitmap.createBitmap(w + rowPadding / pixelStride, h, Bitmap.Config.ARGB_8888)
                        bmp.copyPixelsFromBuffer(buffer)
                        image.close()
                        recentFrame = Frame(bmp, System.currentTimeMillis())
                    }, captureHandler)
                    FloatLogService.instance?.appendLog("截屏服务已启动")
                } catch (e: Exception) {
                    FloatLogService.instance?.appendLog("截屏启动失败: ${e.message}")
                }
                startController()
            }
        }
        return START_STICKY
    }

    fun lastFrame(): Frame? = recentFrame

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

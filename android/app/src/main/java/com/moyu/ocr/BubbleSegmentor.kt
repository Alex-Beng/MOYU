package com.moyu.ocr

import android.graphics.Bitmap
import com.moyu.common.CharBubble
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc

object BubbleSegmentor {
    const val CHAR_SIZE = 64

    private const val HOUGH_DP = 1.0
    private const val HOUGH_MIN_DIST = 123.0
    private const val HOUGH_PARAM1 = 30.0
    private const val HOUGH_PARAM2 = 22.0
    private const val HOUGH_MIN_RADIUS = 51
    private const val HOUGH_MAX_RADIUS = 60

    @Volatile private var opencvLoaded = false

    private fun ensureOpenCV() {
        if (opencvLoaded) return
        System.loadLibrary("opencv_java4")
        opencvLoaded = true
    }

    fun segment(frame: Bitmap): List<CharBubble> {
        ensureOpenCV()
        val src = Mat()
        Utils.bitmapToMat(frame, src)

        val gray = Mat()
        Imgproc.cvtColor(src, gray, Imgproc.COLOR_RGBA2GRAY)

        val blurred = Mat()
        Imgproc.GaussianBlur(gray, blurred, Size(5.0, 5.0), 0.0)

        val circlesMat = Mat()
        Imgproc.HoughCircles(
            blurred, circlesMat, Imgproc.HOUGH_GRADIENT,
            HOUGH_DP, HOUGH_MIN_DIST,
            HOUGH_PARAM1, HOUGH_PARAM2,
            HOUGH_MIN_RADIUS, HOUGH_MAX_RADIUS
        )

        src.release()
        gray.release()
        blurred.release()

        val bubbles = mutableListOf<CharBubble>()
        for (i in 0 until circlesMat.cols()) {
            val data = circlesMat.get(0, i) ?: continue
            val cx = data[0].toInt()
            val cy = data[1].toInt()
            val r = data[2].toInt()

            val crop = cropCircle(frame, cx, cy, r)
            bubbles.add(CharBubble(crop, cx, cy, r))

            for (j in 0..3) {
                val nx = (cx + 2.345 * r * (j + 1)).toInt()
                if (nx + r < frame.width) {
                    val extraCrop = cropCircle(frame, nx, cy, r)
                    bubbles.add(CharBubble(extraCrop, nx, cy, r))
                }
            }
        }

        bubbles.sortWith(compareBy({ it.cy / (HOUGH_MIN_DIST.toInt() / 2) }, { it.cx }))
        circlesMat.release()
        return bubbles
    }

    private fun cropCircle(frame: Bitmap, cx: Int, cy: Int, r: Int): Bitmap {
        val padding = 4
        val size = (r + padding) * 2
        val x = (cx - r - padding).coerceIn(0, frame.width - 1)
        val y = (cy - r - padding).coerceIn(0, frame.height - 1)
        val w = size.coerceAtMost(frame.width - x)
        val h = size.coerceAtMost(frame.height - y)
        val cropped = Bitmap.createBitmap(frame, x, y, w, h)
        return Bitmap.createScaledBitmap(cropped, CHAR_SIZE, CHAR_SIZE, true)
    }
}

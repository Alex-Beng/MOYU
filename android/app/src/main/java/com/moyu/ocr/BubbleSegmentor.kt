package com.moyu.ocr

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.moyu.common.CharBubble
import com.moyu.vision.HoughCircles
import com.moyu.vision.ImageOps

object BubbleSegmentor {
    const val CHAR_SIZE = 64
    private val HOUGH_PARAMS = HoughCirclesParams(
        dp = 1.0f,
        minDist = 123,
        param1 = 30,
        param2 = 22,
        minRadius = 51,
        maxRadius = 60
    )

    fun segment(frame: Bitmap): List<CharBubble> {
        val gray = ImageOps.toGrayscale(frame)
        val circles = HoughCircles.detect(
            gray, frame.width, frame.height,
            dp = HOUGH_PARAMS.dp,
            minDist = HOUGH_PARAMS.minDist,
            param1 = HOUGH_PARAMS.param1,
            param2 = HOUGH_PARAMS.param2,
            minRadius = HOUGH_PARAMS.minRadius,
            maxRadius = HOUGH_PARAMS.maxRadius
        )

        val bubbles = mutableListOf<CharBubble>()
        for (circle in circles) {
            val crop = cropCircle(frame, circle.cx, circle.cy, circle.r)
            bubbles.add(CharBubble(crop, circle.cx, circle.cy, circle.r))

            for (i in 0..3) {
                val nx = (circle.cx + 2.345 * circle.r * (i + 1)).toInt()
                if (nx + circle.r < frame.width) {
                    val extraCrop = cropCircle(frame, nx, circle.cy, circle.r)
                    bubbles.add(CharBubble(extraCrop, nx, circle.cy, circle.r))
                }
            }
        }
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

    private data class HoughCirclesParams(
        val dp: Float,
        val minDist: Int,
        val param1: Int,
        val param2: Int,
        val minRadius: Int,
        val maxRadius: Int
    )
}

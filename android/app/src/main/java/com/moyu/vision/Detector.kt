package com.moyu.vision

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.moyu.common.DetectionResult
import com.moyu.recipe.RecipeConfig
import org.opencv.android.Utils
import org.opencv.core.Core
import org.opencv.core.Mat
import org.opencv.imgproc.Imgproc

class Detector(private val context: Context, private val recipe: RecipeConfig) {
    private val templateCache = mutableMapOf<String, Bitmap?>()
    var logFn: ((String) -> Unit)? = null
    private var opencvLoaded = false

    private fun dbg(msg: String) { logFn?.invoke(msg) }

    private fun ensureOpenCV(): Boolean {
        if (opencvLoaded) return true
        return try {
            System.loadLibrary("opencv_java4")
            opencvLoaded = true
            dbg("OpenCV 加载成功")
            true
        } catch (e: Throwable) {
            dbg("OpenCV 加载失败: ${e.message}")
            false
        }
    }

    fun detect(frame: Bitmap, featureName: String): DetectionResult {
        try {
            return detectInternal(frame, featureName)
        } catch (e: Exception) {
            dbg("detect $featureName: exception: ${e.message}")
            return DetectionResult(false, 0, 0)
        }
    }

    private fun detectInternal(frame: Bitmap, featureName: String): DetectionResult {
        if (!ensureOpenCV()) return DetectionResult(false, 0, 0)

        val feature = recipe.feature(featureName) ?: return DetectionResult(false, 0, 0)
        val template = templateCache.getOrPut(featureName) {
            try {
                context.assets.open(feature.templateAsset).use { stream ->
                    BitmapFactory.decodeStream(stream)
                }
            } catch (e: Exception) {
                dbg("detect $featureName: template load FAILED: ${e.message}")
                null
            }
        } ?: run { return DetectionResult(false, 0, 0) }

        val roi = feature.roi
        val cropFrame = if (roi != null) {
            Bitmap.createBitmap(frame, roi.x, roi.y, roi.w, roi.h)
        } else {
            frame
        }

        val searchMat = Mat()
        val templateMat = Mat()
        val resultMat = Mat()
        Utils.bitmapToMat(cropFrame, searchMat)
        Utils.bitmapToMat(template, templateMat)

        Imgproc.matchTemplate(searchMat, templateMat, resultMat, Imgproc.TM_CCOEFF_NORMED)

        val minMax = Core.minMaxLoc(resultMat)
        val score = minMax.maxVal
        val loc = minMax.maxLoc

        searchMat.release()
        templateMat.release()
        resultMat.release()

        if (score < feature.threshold) {
            dbg("detect $featureName: score=%.3f < threshold=%.2f".format(score, feature.threshold))
            return DetectionResult(false, 0, 0)
        }

        val cx = (if (roi != null) loc.x.toInt() + roi.x else loc.x.toInt()) + template.width / 2
        val cy = (if (roi != null) loc.y.toInt() + roi.y else loc.y.toInt()) + template.height / 2
        dbg("detect $featureName: MATCH score=%.3f @ ($cx,$cy)".format(score))

        return DetectionResult(true, cx, cy)
    }

    fun detectAny(frame: Bitmap, featureNames: List<String>): Pair<String?, DetectionResult?> {
        for (name in featureNames) {
            val result = detect(frame, name)
            if (result.matched) return Pair(name, result)
        }
        return Pair(null, null)
    }

    fun clearCache() {
        for ((_, bmp) in templateCache) bmp?.recycle()
        templateCache.clear()
    }
}

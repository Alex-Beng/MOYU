package com.moyu.vision

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import com.moyu.common.DetectionResult
import com.moyu.recipe.RecipeConfig

class Detector(private val context: Context, private val recipe: RecipeConfig) {
    private val templateCache = mutableMapOf<String, Bitmap?>()
    var logFn: ((String) -> Unit)? = null

    private fun dbg(msg: String) { logFn?.invoke(msg) }

    fun detect(frame: Bitmap, featureName: String): DetectionResult {
        try {
            return detectInternal(frame, featureName)
        } catch (e: Exception) {
            dbg("detect $featureName: exception: ${e.message}")
            return DetectionResult(false, 0, 0)
        }
    }

    private fun detectInternal(frame: Bitmap, featureName: String): DetectionResult {
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

        val result = TemplateMatcher.match(cropFrame, template)
            ?: run { dbg("detect $featureName: match returned null"); return DetectionResult(false, 0, 0) }

        if (result.score < feature.threshold) {
            dbg("detect $featureName: score=${"%.3f".format(result.score)} < ${feature.threshold}")
            return DetectionResult(false, 0, 0)
        }

        val cx = (if (roi != null) result.x + roi.x else result.x) + template.width / 2
        val cy = (if (roi != null) result.y + roi.y else result.y) + template.height / 2
        dbg("detect $featureName: MATCH score=${"%.3f".format(result.score)} @ ($cx,$cy)")

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

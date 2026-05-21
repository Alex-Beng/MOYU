package com.moyu.vision

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.moyu.common.DetectionResult
import com.moyu.common.Roi
import com.moyu.recipe.RecipeConfig

class Detector(private val context: Context, private val recipe: RecipeConfig) {
    private val templateCache = mutableMapOf<String, Bitmap>()

    fun detect(frame: Bitmap, featureName: String): DetectionResult {
        val feature = recipe.feature(featureName) ?: return DetectionResult(false, 0, 0)
        val template = templateCache.getOrPut(featureName) {
            context.assets.open(feature.templateAsset).use { stream ->
                BitmapFactory.decodeStream(stream)
            }
        } ?: return DetectionResult(false, 0, 0)

        val roi = feature.roi
        val cropFrame = if (roi != null) {
            Bitmap.createBitmap(frame, roi.x, roi.y, roi.w, roi.h)
        } else {
            frame
        }

        val result = TemplateMatcher.match(cropFrame, template)
            ?: return DetectionResult(false, 0, 0)

        if (result.score < feature.threshold) {
            return DetectionResult(false, 0, 0)
        }

        val cx = (if (roi != null) result.x + roi.x else result.x) + template.width / 2
        val cy = (if (roi != null) result.y + roi.y else result.y) + template.height / 2

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
        for ((_, bmp) in templateCache) bmp.recycle()
        templateCache.clear()
    }
}

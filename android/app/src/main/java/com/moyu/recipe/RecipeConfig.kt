package com.moyu.recipe

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.moyu.common.Roi
import org.json.JSONObject

data class UiFeature(
    val templateAsset: String,
    val roi: Roi?,
    val threshold: Float = 0.85f,
    val desc: String = ""
)

data class RecipeConfig(
    val name: String,
    val mode: String,
    val deviceWidth: Int,
    val deviceHeight: Int,
    val scrambleDelay: Int?,
    val solveDelay: Int?,
    val ui: Map<String, UiFeature>
) {
    fun feature(name: String): UiFeature? = ui[name]

    fun loadTemplate(context: Context, feature: UiFeature): Bitmap {
        return context.assets.open(feature.templateAsset).use { stream ->
            BitmapFactory.decodeStream(stream)
        }
    }
}

object RecipeLoader {
    private fun parseRoi(arr: JSONObject?): Roi? {
        if (arr == null) return null
        val x = arr.optInt("x", 0)
        val y = arr.optInt("y", 0)
        val w = arr.optInt("w", 0)
        val h = arr.optInt("h", 0)
        if (w <= 0 || h <= 0) return null
        return Roi(x, y, w, h)
    }

    fun load(context: Context, assetPath: String = "recipes/rank.json"): RecipeConfig {
        val recipeDir = context.filesDir.resolve("recipes")
        val targetFile = recipeDir.resolve(assetPath)
        if (!targetFile.exists()) {
            recipeDir.mkdirs()
            val entries = context.assets.list("recipes") ?: emptyArray()
            for (name in entries) {
                context.assets.open("recipes/$name").use { src ->
                    context.filesDir.resolve("recipes/$name").outputStream().use { dst ->
                        src.copyTo(dst)
                    }
                }
            }
        }
        val jsonString = targetFile.bufferedReader().readText()
        val root = JSONObject(jsonString)
        val device = root.getJSONObject("device")
        val uiJson = root.getJSONObject("ui")
        val ui = mutableMapOf<String, UiFeature>()
        for (key in uiJson.keys()) {
            val feat = uiJson.getJSONObject(key)
            ui[key] = UiFeature(
                templateAsset = feat.getString("template"),
                roi = parseRoi(feat.optJSONObject("roi")),
                threshold = feat.optDouble("threshold", 0.85).toFloat(),
                desc = feat.optString("desc", "")
            )
        }
        return RecipeConfig(
            name = root.getString("name"),
            mode = root.optString("mode", "semi"),
            deviceWidth = device.getInt("width"),
            deviceHeight = device.getInt("height"),
            scrambleDelay = root.optInt("scramble_delay", 0).takeIf { it > 0 },
            solveDelay = root.optInt("solve_delay", 0).takeIf { it > 0 },
            ui = ui
        )
    }
}

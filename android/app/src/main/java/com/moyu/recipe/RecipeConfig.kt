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
    val crossDelay: Int?,
    val f2lDelay: Int?,
    val ollDelay: Int?,
    val pllDelay: Int?,
    val alllDelay: Int?,
    val crossTime: Int?,
    val f2lTime: Int?,
    val ollTime: Int?,
    val pllTime: Int?,
    val alllTime: Int?,
    val rotation: String?,
    val moveFormat: String,
    val alllProb: Float,
    val initialState: String?,
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

    fun syncAssets(context: Context) {
        val recipeDir = context.filesDir.resolve("recipes")
        recipeDir.mkdirs()
        val entries = context.assets.list("recipes") ?: emptyArray()
        for (name in entries) {
            context.assets.open("recipes/$name").use { src ->
                recipeDir.resolve(name).outputStream().use { dst -> src.copyTo(dst) }
            }
        }
    }

    fun load(context: Context, assetPath: String = "rank.json"): RecipeConfig {
        syncAssets(context)
        val recipeDir = context.filesDir.resolve("recipes")
        val targetFile = recipeDir.resolve(assetPath)
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
            crossDelay = root.optInt("cross_delay", 0).takeIf { it > 0 },
            f2lDelay = root.optInt("f2l_delay", 0).takeIf { it > 0 },
            ollDelay = root.optInt("oll_delay", 0).takeIf { it > 0 },
            pllDelay = root.optInt("pll_delay", 0).takeIf { it > 0 },
            alllDelay = root.optInt("alll_delay", 0).takeIf { it > 0 },
            crossTime = root.optInt("cross_time", 0).takeIf { it > 0 },
            f2lTime = root.optInt("f2l_time", 0).takeIf { it > 0 },
            ollTime = root.optInt("oll_time", 0).takeIf { it > 0 },
            pllTime = root.optInt("pll_time", 0).takeIf { it > 0 },
            alllTime = root.optInt("alll_time", 0).takeIf { it > 0 },
            rotation = root.optString("rotation", null).takeIf { !it.isNullOrBlank() },
            moveFormat = root.optString("move_format", "dir"),
            alllProb = root.optDouble("alll_prob", 0.1).toFloat(),
            initialState = root.optString("initial_state", null).takeIf { !it.isNullOrBlank() },
            ui = ui
        )
    }
}

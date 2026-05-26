package com.moyu.common

import android.content.Context

object AppPrefs {
    private const val PREFS_NAME = "moyu"
    private const val KEY_LAST_RECIPE = "last_recipe"
    private const val KEY_ESP_HOST = "esp_host"
    private const val DEFAULT_ESP_HOST = "192.168.4.1"

    fun lastRecipe(context: Context): String =
        prefs(context).getString(KEY_LAST_RECIPE, "rank.json") ?: "rank.json"

    fun saveRecipe(context: Context, name: String) =
        prefs(context).edit().putString(KEY_LAST_RECIPE, name).apply()

    fun espHost(context: Context): String =
        prefs(context).getString(KEY_ESP_HOST, DEFAULT_ESP_HOST) ?: DEFAULT_ESP_HOST

    fun saveEspHost(context: Context, host: String) =
        prefs(context).edit().putString(KEY_ESP_HOST, host).apply()

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
}

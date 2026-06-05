package com.moyu.common

import android.graphics.Bitmap

data class Frame(val bitmap: Bitmap, val timestampMs: Long)

data class Roi(val x: Int, val y: Int, val w: Int, val h: Int)

data class DetectionResult(val matched: Boolean, val centerX: Int, val centerY: Int)

data class CharBubble(val bitmap: Bitmap, val cx: Int, val cy: Int, val r: Int)

data class CubeMove(val face: Int, val dir: Int) : CubeCommand
data class CubeMoveStr(val move: String) : CubeCommand
data class CubeDelay(val ms: Int) : CubeCommand
data class CubeTime(val ms: Int) : CubeCommand

sealed interface CubeCommand

interface FrameSource {
    fun lastFrame(): Frame?
}

interface TouchInjector {
    fun tap(x: Int, y: Int)
    fun swipe(x1: Int, y1: Int, x2: Int, y2: Int, durationMs: Long = 200)
}

interface CubeClient {
    suspend fun getFacelets(): String
    suspend fun sendMoves(notation: String): Boolean
    suspend fun sendMovesRaw(moves: List<CubeCommand>): Boolean
    suspend fun setDelay(ms: Int): Boolean
    suspend fun getState(): Map<String, Any>
}

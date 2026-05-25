package com.moyu.ocr

import android.content.Context
import android.graphics.Bitmap
import java.nio.ByteBuffer
import java.nio.ByteOrder

class MoveClassifier(context: Context) : AutoCloseable {
    companion object {
        val LABELS = listOf(
            "R", "R'", "R2", "R2'",
            "L", "L'", "L2", "L2'",
            "U", "U'", "U2", "U2'",
            "D", "D'", "D2", "D2'",
            "F", "F'", "F2", "F2'",
            "B", "B'", "B2", "B2'",
            "EMPTY"
        )
    }

    private val interpreter: org.tensorflow.lite.Interpreter?
    private val inputSize = 64

    init {
        interpreter = try {
            val model = loadModelFile(context)
            val options = org.tensorflow.lite.Interpreter.Options().apply { numThreads = 2 }
            org.tensorflow.lite.Interpreter(model, options)
        } catch (e: Exception) {
            android.util.Log.e("MoveClassifier", "模型加载失败: ${e.message}")
            null
        }
    }

    fun predict(bubble: Bitmap): String {
        val interp = interpreter ?: return "?"
        val inputBuffer = preprocessBitmap(bubble)
        val output = Array(1) { FloatArray(25) }
        interp.run(inputBuffer, output)
        val argmax = output[0].indices.maxByOrNull { output[0][it] } ?: 24
        return LABELS[argmax]
    }

    fun predictBatch(bubbles: List<Bitmap>): List<String> {
        if (bubbles.isEmpty()) return emptyList()
        return bubbles.map { predict(it) }
    }

    private fun preprocessBitmap(bmp: Bitmap): ByteBuffer {
        val resized = Bitmap.createScaledBitmap(bmp, inputSize, inputSize, true)
        val gray = FloatArray(inputSize * inputSize)
        val pixels = IntArray(inputSize * inputSize)
        resized.getPixels(pixels, 0, inputSize, 0, 0, inputSize, inputSize)
        for (i in pixels.indices) {
            val p = pixels[i]
            val r = (p shr 16) and 0xFF
            val g = (p shr 8) and 0xFF
            val b = p and 0xFF
            gray[i] = (0.299f * r + 0.587f * g + 0.114f * b) / 255.0f
        }
        val buffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize)
        buffer.order(ByteOrder.nativeOrder())
        for (v in gray) buffer.putFloat(v)
        buffer.rewind()
        return buffer
    }

    private fun loadModelFile(context: Context): java.nio.MappedByteBuffer {
        val afd = context.assets.openFd("cnn_model.tflite")
        val inputStream = afd.createInputStream()
        val fileChannel = inputStream.channel as java.nio.channels.FileChannel
        return fileChannel.map(java.nio.channels.FileChannel.MapMode.READ_ONLY, afd.startOffset, afd.declaredLength)
    }

    override fun close() { interpreter ?.close() }
}

package com.moyu.vision

object ImageOps {
    fun toGrayscale(bmp: android.graphics.Bitmap): IntArray {
        val w = bmp.width
        val h = bmp.height
        val pixels = IntArray(w * h)
        bmp.getPixels(pixels, 0, w, 0, 0, w, h)
        val gray = IntArray(w * h)
        for (i in pixels.indices) {
            val p = pixels[i]
            val r = (p shr 16) and 0xFF
            val g = (p shr 8) and 0xFF
            val b = p and 0xFF
            gray[i] = ((0.299 * r + 0.587 * g + 0.114 * b).toInt()).coerceIn(0, 255)
        }
        return gray
    }

    fun gaussianBlur5(gray: IntArray, width: Int, height: Int): IntArray {
        val kernel = intArrayOf(1, 4, 6, 4, 1)
        val kernelSum = 16
        val temp = IntArray(gray.size)

        for (y in 0 until height) {
            for (x in 0 until width) {
                var sum = 0
                for (ky in 0..4) {
                    val yy = (y + ky - 2).coerceIn(0, height - 1)
                    sum += gray[yy * width + x] * kernel[ky]
                }
                temp[y * width + x] = (sum / kernelSum).coerceIn(0, 255)
            }
        }

        val result = IntArray(gray.size)
        for (y in 0 until height) {
            for (x in 0 until width) {
                var sum = 0
                for (kx in 0..4) {
                    val xx = (x + kx - 2).coerceIn(0, width - 1)
                    sum += temp[y * width + xx] * kernel[kx]
                }
                result[y * width + x] = (sum / kernelSum).coerceIn(0, 255)
            }
        }
        return result
    }

    fun canny(gray: IntArray, width: Int, height: Int, low: Int = 50, high: Int = 150): IntArray {
        val blurred = gaussianBlur5(gray, width, height)
        val (mag, angle) = sobelMagnitudeAngle(blurred, width, height)
        val nms = nonMaxSuppression(mag, angle, width, height)
        return hysteresis(nms, width, height, low, high)
    }

    internal fun sobelMagnitudeAngle(gray: IntArray, w: Int, h: Int): Pair<IntArray, IntArray> {
        val gxK = intArrayOf(-1, 0, 1, -2, 0, 2, -1, 0, 1)
        val gyK = intArrayOf(-1, -2, -1, 0, 0, 0, 1, 2, 1)
        val mag = IntArray(gray.size)
        val angle = IntArray(gray.size)
        for (y in 1 until h - 1) {
            for (x in 1 until w - 1) {
                var gx = 0
                var gy = 0
                for (ky in -1..1) {
                    for (kx in -1..1) {
                        val p = gray[(y + ky) * w + (x + kx)]
                        val ki = (ky + 1) * 3 + (kx + 1)
                        gx += p * gxK[ki]
                        gy += p * gyK[ki]
                    }
                }
                val m = kotlin.math.sqrt((gx * gx + gy * gy).toDouble()).toInt()
                mag[y * w + x] = m.coerceIn(0, 255)
                val a = kotlin.math.atan2(gy.toDouble(), gx.toDouble())
                val deg = ((a * 180.0 / Math.PI) + 180.0) % 180.0
                angle[y * w + x] = when {
                    deg < 22.5 || deg >= 157.5 -> 0
                    deg < 67.5 -> 45
                    deg < 112.5 -> 90
                    else -> 135
                }
            }
        }
        return Pair(mag, angle)
    }

    internal fun nonMaxSuppression(mag: IntArray, angle: IntArray, w: Int, h: Int): IntArray {
        val result = IntArray(mag.size)
        for (y in 1 until h - 1) {
            for (x in 1 until w - 1) {
                val idx = y * w + x
                val a = angle[idx]
                val m = mag[idx]
                val (n1, n2) = when (a) {
                    0 -> Pair(mag[idx - 1], mag[idx + 1])
                    45 -> Pair(mag[(y - 1) * w + (x + 1)], mag[(y + 1) * w + (x - 1)])
                    90 -> Pair(mag[(y - 1) * w + x], mag[(y + 1) * w + x])
                    135 -> Pair(mag[(y - 1) * w + (x - 1)], mag[(y + 1) * w + (x + 1)])
                    else -> Pair(0, 0)
                }
                result[idx] = if (m >= n1 && m >= n2) m else 0
            }
        }
        return result
    }

    internal fun hysteresis(nms: IntArray, w: Int, h: Int, low: Int, high: Int): IntArray {
        val result = IntArray(nms.size)
        val visited = BooleanArray(nms.size)

        fun dfs(x: Int, y: Int) {
            if (x < 0 || x >= w || y < 0 || y >= h) return
            val idx = y * w + x
            if (visited[idx] || result[idx] != 0) return
            if (nms[idx] >= low) {
                visited[idx] = true
                result[idx] = 255
                for (dy in -1..1) for (dx in -1..1) {
                    if (dx != 0 || dy != 0) dfs(x + dx, y + dy)
                }
            }
        }

        for (y in 0 until h) for (x in 0 until w) {
            val idx = y * w + x
            if (!visited[idx] && nms[idx] >= high) {
                dfs(x, y)
            }
        }
        return result
    }
}

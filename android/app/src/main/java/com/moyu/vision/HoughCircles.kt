package com.moyu.vision

import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

data class Circle(val cx: Int, val cy: Int, val r: Int)

object HoughCircles {
    fun detect(
        gray: IntArray,
        width: Int,
        height: Int,
        dp: Float = 1.0f,
        minDist: Int = 123,
        param1: Int = 30,
        param2: Int = 22,
        minRadius: Int = 51,
        maxRadius: Int = 60,
    ): List<Circle> {
        val edges = ImageOps.canny(gray, width, height, param1 / 2, param1)

        val accW = (width / dp).toInt()
        val accH = (height / dp).toInt()
        val accumulator = IntArray(accW * accH)

        val sinCache = IntArray(360)
        val cosCache = IntArray(360)
        for (i in 0 until 360) {
            val rad = Math.toRadians(i.toDouble())
            sinCache[i] = (sin(rad) * 1000).toInt()
            cosCache[i] = (cos(rad) * 1000).toInt()
        }

        for (y in 1 until height - 1) {
            for (x in 1 until width - 1) {
                if (edges[y * width + x] == 0) continue

                val gx = gradientX(edges, width, height, x, y)
                val gy = gradientY(edges, width, height, x, y)
                val magSq = gx * gx + gy * gy
                if (magSq < 100) continue

                val angle = (Math.toDegrees(kotlin.math.atan2(gy.toDouble(), gx.toDouble())) + 360.0) % 360.0
                val aIdx = angle.toInt() % 360

                for (r in minRadius..maxRadius) {
                    val cx1 = (x + r * cosCache[aIdx] / 1000) / dp.toInt()
                    val cy1 = (y + r * sinCache[aIdx] / 1000) / dp.toInt()
                    val cx2 = (x - r * cosCache[aIdx] / 1000) / dp.toInt()
                    val cy2 = (y - r * sinCache[aIdx] / 1000) / dp.toInt()

                    if (cx1 in 0 until accW && cy1 in 0 until accH) {
                        accumulator[cy1 * accW + cx1]++
                    }
                    if (cx2 in 0 until accW && cy2 in 0 until accH) {
                        accumulator[cy2 * accW + cx2]++
                    }
                }
            }
        }

        val peaks = findPeaks(accumulator, accW, accH, minDist, param2)

        val circles = mutableListOf<Circle>()
        for ((pcx, pcy) in peaks) {
            val cx = (pcx * dp).toInt()
            val cy = (pcy * dp).toInt()

            var bestR = minRadius
            var maxEdgeCount = -1
            for (r in minRadius..maxRadius) {
                var count = 0
                var total = 0
                for (t in 0 until 360 step 10) {
                    val rad = Math.toRadians(t.toDouble())
                    val px = (cx + r * cos(rad)).toInt()
                    val py = (cy + r * sin(rad)).toInt()
                    if (px in 0 until width && py in 0 until height) {
                        total++
                        if (edges[py * width + px] != 0) count++
                    }
                }
                if (total > 0 && count * 100 / total > maxEdgeCount) {
                    maxEdgeCount = count * 100 / total
                    bestR = r
                }
            }

            if (maxEdgeCount > 20) {
                circles.add(Circle(cx, cy, bestR))
            }
        }

        circles.sortWith(compareBy({ it.cy / (minDist / 2) }, { it.cx }))
        return circles
    }

    private fun gradientX(gray: IntArray, w: Int, h: Int, x: Int, y: Int): Int {
        if (x <= 0 || x >= w - 1) return 0
        return (gray[y * w + x + 1] - gray[y * w + x - 1])
    }

    private fun gradientY(gray: IntArray, w: Int, h: Int, x: Int, y: Int): Int {
        if (y <= 0 || y >= h - 1) return 0
        return (gray[(y + 1) * w + x] - gray[(y - 1) * w + x])
    }

    private fun findPeaks(
        acc: IntArray, accW: Int, accH: Int,
        minDist: Int, threshold: Int
    ): List<Pair<Int, Int>> {
        val candidates = mutableListOf<Pair<Int, Pair<Int, Int>>>()
        for (y in 0 until accH) {
            for (x in 0 until accW) {
                val v = acc[y * accW + x]
                if (v >= threshold) {
                    candidates.add(v to Pair(x, y))
                }
            }
        }
        candidates.sortByDescending { it.first }

        val peaks = mutableListOf<Pair<Int, Int>>()
        for ((_, pos) in candidates) {
            var tooClose = false
            for (existing in peaks) {
                val dx = pos.first - existing.first
                val dy = pos.second - existing.second
                if (sqrt((dx * dx + dy * dy).toDouble()) < minDist) {
                    tooClose = true
                    break
                }
            }
            if (!tooClose) {
                peaks.add(pos)
            }
        }
        return peaks
    }
}

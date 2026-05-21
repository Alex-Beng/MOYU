package com.moyu.vision

import android.graphics.Bitmap

data class MatchResult(val score: Float, val x: Int, val y: Int)

object TemplateMatcher {
    fun matchGrayscale(
        frame: IntArray, fw: Int, fh: Int,
        template: IntArray, tw: Int, th: Int,
    ): MatchResult? {
        if (tw > fw || th > fh) return null

        val sumTable = LongArray((fw + 1) * (fh + 1))
        val sumSqTable = LongArray((fw + 1) * (fh + 1))
        for (y in 0 until fh) {
            for (x in 0 until fw) {
                val p = frame[y * fw + x]
                val idx = (y + 1) * (fw + 1) + (x + 1)
                sumTable[idx] = p.toLong() +
                        sumTable[y * (fw + 1) + (x + 1)] +
                        sumTable[(y + 1) * (fw + 1) + x] -
                        sumTable[y * (fw + 1) + x]
                sumSqTable[idx] = (p.toLong() * p) +
                        sumSqTable[y * (fw + 1) + (x + 1)] +
                        sumSqTable[(y + 1) * (fw + 1) + x] -
                        sumSqTable[y * (fw + 1) + x]
            }
        }

        var tSum = 0L
        var tSqSum = 0L
        for (p in template) {
            tSum += p.toLong()
            tSqSum += p.toLong() * p
        }
        val tMean = tSum.toDouble() / (tw * th)
        val tVar = tSqSum.toDouble() / (tw * th) - tMean * tMean
        val tStd = kotlin.math.sqrt(tVar.coerceAtLeast(1e-10))

        var bestScore = -1.0
        var bestX = 0
        var bestY = 0

        for (y in 0..fh - th) {
            for (x in 0..fw - tw) {
                val idxTL = y * (fw + 1) + x
                val idxTR = y * (fw + 1) + (x + tw)
                val idxBL = (y + th) * (fw + 1) + x
                val idxBR = (y + th) * (fw + 1) + (x + tw)

                val fSum = sumTable[idxBR] - sumTable[idxBL] - sumTable[idxTR] + sumTable[idxTL]
                val fSqSum = sumSqTable[idxBR] - sumSqTable[idxBL] - sumSqTable[idxTR] + sumSqTable[idxTL]
                val area = tw * th
                val fMean = fSum.toDouble() / area
                val fVar = fSqSum.toDouble() / area - fMean * fMean
                val fStd = kotlin.math.sqrt(fVar.coerceAtLeast(1e-10))

                var cross = 0.0
                for (ty in 0 until th) {
                    for (tx in 0 until tw) {
                        val fp = frame[(y + ty) * fw + (x + tx)]
                        val tp = template[ty * tw + tx]
                        cross += (fp - fMean) * (tp - tMean)
                    }
                }

                val denom = fStd * tStd * area
                val score = if (denom > 1e-10) cross / denom else 0.0

                if (score > bestScore) {
                    bestScore = score
                    bestX = x
                    bestY = y
                }
            }
        }

        return MatchResult(bestScore.toFloat(), bestX, bestY)
    }

    fun match(frameBitmap: Bitmap, templateBitmap: Bitmap): MatchResult? {
        val frameGray = ImageOps.toGrayscale(frameBitmap)
        val templateGray = ImageOps.toGrayscale(templateBitmap)
        return matchGrayscale(
            frameGray, frameBitmap.width, frameBitmap.height,
            templateGray, templateBitmap.width, templateBitmap.height
        )
    }
}

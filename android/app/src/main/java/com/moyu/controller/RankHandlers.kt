package com.moyu.controller

import android.graphics.Bitmap
import com.moyu.ocr.BubbleSegmentor
import com.moyu.ocr.MoveParser
import kotlinx.coroutines.delay

suspend fun rankInit(ctrl: Controller): String? {
    ctrl.log("rank/init: 等待 begin_rank...")
    val result = ctrl.waitForUi("begin_rank", 60_000L) ?: return "init"
    ctrl.clickFeature("begin_rank")
    delay(2000)
    return "scramble"
}

suspend fun rankScramble(ctrl: Controller): String? {
    val frame = ctrl.lastFrameBitmap() ?: run { delay(500); return "scramble" }
    val feature = ctrl.recipe.feature("scramble_area")
    val crop = if (feature != null && feature.roi != null) {
        val r = feature.roi
        Bitmap.createBitmap(frame, r.x, r.y, r.w, r.h)
    } else frame

    try {
        val bubbles = BubbleSegmentor.segment(crop)
        if (bubbles.isNotEmpty()) {
            val labels = ctrl.classifier.predictBatch(bubbles.map { it.bitmap })
            val moves = MoveParser.parse(labels)
            if (moves.isNotEmpty()) {
                ctrl.scrambleSeenMove = true
                ctrl.noScrambleCnt = 0
                ctrl.queueMoves(moves)
                ctrl.log("打乱: $moves")
                delay(500)
            } else {
                ctrl.noScrambleCnt++
                if (ctrl.scrambleSeenMove && ctrl.noScrambleCnt > 1) {
                    delay(1000)
                    return "solve"
                }
            }
        } else {
            ctrl.noScrambleCnt++
            if (ctrl.scrambleSeenMove && ctrl.noScrambleCnt > 1) {
                delay(1000)
                return "solve"
            }
        }
    } catch (e: Exception) {
        ctrl.log("OCR 错误: ${e.message}")
    }
    delay(1000)
    return "scramble"
}

suspend fun rankSolve(ctrl: Controller): String? {
    ctrl.log("rank/solve: 获取面片...")
    try {
        val facelets = ctrl.getFacelets()
        if (facelets.length != 54) {
            delay(1000)
            return "solve"
        }
        ctrl.log("面片: $facelets")
        val result = ctrl.solver.solve(facelets)
        if (result == null) {
            ctrl.log("求解失败，重试...")
            delay(2000)
            return "solve"
        }
        ctrl.log("解法: ${result.solution} (${result.solution.split(" ").size}步)")
        ctrl.queueMoves(result.solution)

        val start = System.currentTimeMillis()
        val timeout = 180_000L
        while (System.currentTimeMillis() - start < timeout) {
            val frame = ctrl.lastFrameBitmap() ?: run { delay(1000); continue }

            val (endName, _) = ctrl.detector.detectAny(frame,
                listOf("end_rank", "re_rank"))
            when (endName) {
                "end_rank" -> {
                    ctrl.clickFeature("end_rank")
                    delay(1500)
                    return "re_rank"
                }
                "re_rank" -> {
                    ctrl.clickFeature("re_rank")
                    delay(1500)
                    return "scramble"
                }
            }
            try {
                val bubbles = BubbleSegmentor.segment(frame)
                if (bubbles.size >= 2) {
                    ctrl.log("检测到新打乱")
                    return "scramble"
                }
            } catch (_: Exception) {}
            delay(2000)
        }
        return "solve"
    } catch (e: Exception) {
        ctrl.log("求解错误: ${e.message}")
        delay(2000)
        return "solve"
    }
}

suspend fun rankReRank(ctrl: Controller): String? {
    ctrl.log("rank/re_rank: 等待 re_rank...")
    val result = ctrl.waitForUi("re_rank", 30_000L) ?: run {
        delay(1000)
        return "re_rank"
    }
    ctrl.clickFeature("re_rank")
    delay(2000)
    return "scramble"
}

suspend fun semiScramble(ctrl: Controller): String? = rankScramble(ctrl).also {
    ctrl.log("semi/scramble")
}

suspend fun semiSolve(ctrl: Controller): String? {
    ctrl.log("semi/solve")
    val facelets = ctrl.getFacelets()
    if (facelets.length != 54) return "solve"
    val result = ctrl.solver.solve(facelets) ?: return "solve"
    ctrl.queueMoves(result.solution)
    delay(5000)
    return "scramble"
}

suspend fun holderInit(ctrl: Controller): String? {
    ctrl.log("holder/init: 等待 begin_holder...")
    ctrl.waitForUi("begin_holder", 30_000L)?.let {
        ctrl.clickFeature("begin_holder")
        delay(2000)
    }
    return "scramble"
}

suspend fun holderSolve(ctrl: Controller): String? {
    ctrl.log("holder/solve")
    val facelets = ctrl.getFacelets()
    val result = ctrl.solver.solve(facelets) ?: return "solve"
    ctrl.queueMoves(result.solution)
    ctrl.waitForUi("re_holder", 120_000L)?.let {
        ctrl.clickFeature("re_holder")
        delay(2000)
        return "init"
    }
    return "solve"
}

suspend fun holderReHolder(ctrl: Controller): String? {
    ctrl.log("holder/re_holder")
    ctrl.clickFeature("re_holder")
    delay(2000)
    return "init"
}

suspend fun teamInit(ctrl: Controller): String? {
    ctrl.log("team/init")
    ctrl.waitForUi("begin_team", 30_000L)?.let {
        ctrl.clickFeature("begin_team")
        delay(2000)
    }
    return "scramble"
}

suspend fun teamSolve(ctrl: Controller): String? {
    ctrl.log("team/solve")
    val facelets = ctrl.getFacelets()
    val result = ctrl.solver.solve(facelets) ?: return "solve"
    ctrl.queueMoves(result.solution)
    ctrl.waitForUi("continue_team", 120_000L)?.let {
        ctrl.clickFeature("continue_team")
        delay(2000)
        return "scramble"
    }
    return "solve"
}

suspend fun teamReTeam(ctrl: Controller): String? {
    ctrl.log("team/re_team")
    ctrl.clickFeature("continue_team")
    delay(2000)
    return "scramble"
}

suspend fun weekInit(ctrl: Controller): String? {
    ctrl.log("week/init")
    ctrl.waitForUi("begin_team", 30_000L)?.let {
        ctrl.clickFeature("begin_team")
        delay(2000)
    }
    return "scramble"
}

suspend fun weekSolve(ctrl: Controller): String? {
    ctrl.log("week/solve")
    val facelets = ctrl.getFacelets()
    val result = ctrl.solver.solve(facelets) ?: return "solve"
    ctrl.queueMoves(result.solution)
    ctrl.waitForUi("continue_week", 120_000L)?.let {
        ctrl.clickFeature("continue_week")
        delay(2000)
        return "scramble"
    }
    return "solve"
}

suspend fun weekReWeek(ctrl: Controller): String? {
    ctrl.log("week/re_week")
    ctrl.clickFeature("continue_week")
    delay(2000)
    return "scramble"
}

suspend fun remoteSolve(ctrl: Controller): String? {
    ctrl.log("remote/solve")
    val facelets = ctrl.getFacelets()
    val result = ctrl.solver.solve(facelets) ?: return "solve"
    ctrl.queueMoves(result.solution)
    delay(5000)
    return "scramble"
}

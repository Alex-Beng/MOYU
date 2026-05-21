package com.moyu.ocr

object MoveParser {
    private val VALID = MoveClassifier.LABELS.toSet()
    private val EMPTY = setOf("EMPTY", "?")

    fun parse(rawLabels: List<String>): String {
        return rawLabels
            .filter { it in VALID && it !in EMPTY }
            .joinToString(" ")
    }
}

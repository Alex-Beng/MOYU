package com.moyu.solve

object AlgParser {
    private val ROTATION_FACE_MAP = mapOf(
        'x' to mapOf('U' to 'F', 'F' to 'D', 'D' to 'B', 'B' to 'U', 'R' to 'R', 'L' to 'L'),
        'y' to mapOf('U' to 'U', 'R' to 'B', 'F' to 'R', 'L' to 'F', 'B' to 'L', 'D' to 'D'),
        'z' to mapOf('U' to 'L', 'R' to 'U', 'D' to 'R', 'L' to 'D', 'F' to 'F', 'B' to 'B')
    )

    private val DOUBLE_MOVE_MAP = mapOf(
        'u' to mapOf(1 to listOf("D", "y"), 2 to listOf("D2", "y", "y"), 3 to listOf("D'", "y", "y", "y")),
        'd' to mapOf(1 to listOf("U", "y", "y", "y"), 2 to listOf("U2", "y", "y"), 3 to listOf("U'", "y")),
        'r' to mapOf(1 to listOf("L", "x"), 2 to listOf("L2", "x", "x"), 3 to listOf("L'", "x", "x", "x")),
        'l' to mapOf(1 to listOf("R", "x", "x", "x"), 2 to listOf("R2", "x", "x"), 3 to listOf("R'", "x")),
        'f' to mapOf(1 to listOf("B", "z"), 2 to listOf("B2", "z", "z"), 3 to listOf("B'", "z", "z", "z")),
        'b' to mapOf(1 to listOf("F", "z", "z", "z"), 2 to listOf("F2", "z", "z"), 3 to listOf("F'", "z"))
    )

    private val EMS_MOVE_MAP = mapOf(
        'E' to mapOf(1 to listOf("D'", "U", "y", "y", "y"), 2 to listOf("D2", "U2", "y", "y"), 3 to listOf("D", "U'", "y")),
        'M' to mapOf(1 to listOf("L'", "R", "x", "x", "x"), 2 to listOf("L2", "R2", "x", "x"), 3 to listOf("L", "R'", "x")),
        'S' to mapOf(1 to listOf("F'", "B", "z"), 2 to listOf("F2", "B2", "z", "z"), 3 to listOf("F", "B'", "z", "z", "z"))
    )

    private val MOD_COUNT = mapOf("" to 1, "'" to 3, "2" to 2, "2'" to 2)

    fun convertAlgToBasic(algStr: String): Pair<String, String> {
        var raw = algStr.trim('"')
        raw = expandBrackets(raw)

        val tokenPattern = Regex("[URFDLBurfdlbEMSxyz]2'?|[URFDLBurfdlbEMSxyz]['2]?")
        val tokens = tokenPattern.findAll(raw).map { it.value }.filter { it.isNotEmpty() }.toList()

        val expanded = mutableListOf<String>()
        for (t in tokens) {
            val base = t[0]
            val mod = if (t.length > 1) t.substring(1) else ""
            val count = MOD_COUNT[mod] ?: 1

            when {
                base in "URFDLB" -> expanded.add(t)
                base in "xyz" -> repeat(count % 4) { expanded.add(base.toString()) }
                base in "urfdlb" -> {
                    val seq = DOUBLE_MOVE_MAP[base]?.get(count % 4)
                    if (seq != null) expanded.addAll(seq)
                }
                base in "EMS" -> {
                    val seq = EMS_MOVE_MAP[base]?.get(count % 4)
                    if (seq != null) expanded.addAll(seq)
                }
            }
        }

        val result = expanded.toMutableList()
        var i = result.size - 1
        while (i >= 0) {
            val t = result[i]
            if (t in listOf("x", "y", "z")) {
                val rot = t[0]
                for (j in i + 1 until result.size) {
                    val m = result[j]
                    if (m in listOf("x", "y", "z")) continue
                    val face = m[0]
                    val modJ = if (m.length > 1) m.substring(1) else ""
                    result[j] = applyRotation(face, rot) + modJ
                }
                result.removeAt(i)
            }
            i--
        }

        val simplified = mutableListOf<String>()
        i = 0
        while (i < result.size) {
            val move = result[i]
            val base = move[0]
            val mod = if (move.length > 1) move.substring(1) else ""
            var total = MOD_COUNT[mod] ?: 1

            var j = i + 1
            while (j < result.size) {
                val nextMove = result[j]
                val nextBase = nextMove[0]
                if (nextBase != base) break
                val nextMod = if (nextMove.length > 1) nextMove.substring(1) else ""
                total = (total + (MOD_COUNT[nextMod] ?: 1)) % 4
                j++
            }

            when (total) {
                1 -> simplified.add(base.toString())
                2 -> simplified.add("$base" + "2")
                3 -> simplified.add("$base" + "'")
            }
            i = j
        }

        return Pair(simplified.joinToString(" "), expanded.joinToString(" "))
    }

    private fun expandBrackets(s: String): String {
        var result = s
        val bracketPattern = Regex("\\(([^)]+)\\)([2']?2'?)?" )
        while (true) {
            val m = bracketPattern.find(result) ?: break
            val inner = m.groupValues[1].trim()
            val repeatMod = m.groupValues[2]
            val repeatCount = if ('2' in repeatMod) 2 else 1
            val expandedInner = (1..repeatCount).joinToString(" ") { inner }
            result = result.substring(0, m.range.first) + " $expandedInner " + result.substring(m.range.last + 1)
        }
        return result
    }

    private fun applyRotation(face: Char, rot: Char): String {
        return ROTATION_FACE_MAP[rot]?.get(face)?.toString() ?: face.toString()
    }
}

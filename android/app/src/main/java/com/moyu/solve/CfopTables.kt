package com.moyu.solve

object Combinatorics {
    private var cnkCache: Array<IntArray>? = null

    fun cnkTable(): Array<IntArray> {
        val c = cnkCache
        if (c != null) return c
        val table = Array(13) { IntArray(13) }
        for (i in 0..12) {
            table[i][0] = 1
            for (j in 1..i) {
                table[i][j] = table[i - 1][j - 1] + table[i - 1][j]
            }
        }
        cnkCache = table
        return table
    }

    fun combIdx(chosen: BooleanArray, n: Int, k: Int): Int {
        val cnk = cnkTable()
        var idx = 0
        var r = k
        for (i in 0 until n) {
            if (chosen[i]) {
                idx += cnk[n - 1 - i][r]
                r--
            }
        }
        return idx
    }

    fun permIdx(perm: IntArray, n: Int): Int {
        var idx = 0
        val used = BooleanArray(n)
        for (i in 0 until n) {
            var cnt = 0
            for (j in 0 until perm[i]) {
                if (!used[j]) cnt++
            }
            idx = idx * (n - i) + cnt
            used[perm[i]] = true
        }
        return idx
    }

    fun permFromIdx(idx: Int, n: Int): IntArray {
        val perm = IntArray(n)
        val used = BooleanArray(n)
        var remaining = idx
        for (i in 0 until n) {
            var factVal = 1
            for (k in 1 until n - i) factVal *= k
            val cnt = remaining / factVal
            remaining %= factVal
            var j = 0
            var skipped = 0
            while (j < n) {
                if (!used[j]) {
                    if (skipped == cnt) {
                        perm[i] = j
                        used[j] = true
                        break
                    }
                    skipped++
                }
                j++
            }
        }
        return perm
    }

    val F2L_PAIRS = listOf(
        4 to 8, 5 to 9, 6 to 10, 7 to 11
    )

    val F2L_MOVE_INDICES = listOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17)

    val F2L_TRIGGERS = listOf(
        listOf(3, 0, 5), listOf(3, 2, 5), listOf(5, 0, 3), listOf(5, 2, 3),
        listOf(6, 0, 8), listOf(6, 2, 8), listOf(8, 0, 6), listOf(8, 2, 6),
        listOf(12, 0, 14), listOf(12, 2, 14), listOf(14, 0, 12), listOf(14, 2, 12),
        listOf(15, 0, 17), listOf(15, 2, 17), listOf(17, 0, 15), listOf(17, 2, 15)
    )

    val F2L_U_MOVES = listOf(listOf(0), listOf(1), listOf(2))
    val F2L_D_MOVES = listOf(listOf(9), listOf(11), listOf(10))

    val F2L_MACRO_MOVES = F2L_TRIGGERS + F2L_U_MOVES + F2L_D_MOVES
    val N_F2L_MACROS = F2L_MACRO_MOVES.size

    val OPPOSITE_FACE = mapOf(0 to 3, 3 to 0, 1 to 4, 4 to 1, 2 to 5, 5 to 2)
}

fun getCrossPermCoord(state: CubieCube): Int {
    val cnk = Combinatorics.cnkTable()
    var r = 4
    var combVal = 0
    val permPieces = mutableListOf<Int>()
    for (i in 0..11) {
        if (state.ep[i] in 4..7) {
            combVal += cnk[11 - i][r]
            r--
            permPieces.add(state.ep[i] - 4)
        }
    }
    val permOrder = Combinatorics.permIdx(permPieces.toIntArray(), 4)
    return combVal * 24 + permOrder
}

fun getCrossFlipCoord(state: CubieCube): Int {
    val cnk = Combinatorics.cnkTable()
    var r = 4
    var combVal = 0
    var flipBits = 0
    var bitPos = 0
    for (i in 0..11) {
        if (state.ep[i] in 4..7) {
            combVal += cnk[11 - i][r]
            if (state.eo[i] != 0) flipBits = flipBits or (1 shl bitPos)
            bitPos++
            r--
        }
    }
    return combVal * 16 + flipBits
}

const val N_CROSS_PERM = 495 * 24
const val N_CROSS_FLIP = 495 * 16

fun getPairCoord(state: CubieCube, pairIdx: Int): Int {
    val (cornerPiece, edgePiece) = Combinatorics.F2L_PAIRS[pairIdx]
    val cpSlot = state.cp.indexOf(cornerPiece)
    val coVal = state.co[cpSlot]
    val epSlot = state.ep.indexOf(edgePiece)
    val eoVal = state.eo[epSlot]
    return (cpSlot * 3 + coVal) * 24 + (epSlot * 2 + eoVal)
}

fun pairIsSolved(state: CubieCube, pairIdx: Int): Boolean {
    val (cornerPiece, edgePiece) = Combinatorics.F2L_PAIRS[pairIdx]
    val cpSlot = state.cp.indexOf(cornerPiece)
    val epSlot = state.ep.indexOf(edgePiece)
    return cpSlot == cornerPiece && state.co[cpSlot] == 0 &&
            epSlot == edgePiece && state.eo[epSlot] == 0
}

fun pairSolvedCoord(pairIdx: Int): Int {
    val (cornerPiece, edgePiece) = Combinatorics.F2L_PAIRS[pairIdx]
    return (cornerPiece * 3) * 24 + (edgePiece * 2)
}

fun checkCrossIntact(state: CubieCube): Boolean {
    for (e in 4..7) {
        if (state.ep[e] != e || state.eo[e] != 0) return false
    }
    return true
}

private fun edgeMovePerm(ep: IntArray, eo: IntArray, face: Int): Pair<IntArray, IntArray> {
    val newEp = IntArray(12) { ep[CubieCube.MOVE_EP[face][it]] }
    val newEo = IntArray(12) { (eo[CubieCube.MOVE_EP[face][it]] + CubieCube.MOVE_EO[face][it]) % 2 }
    return Pair(newEp, newEo)
}

private fun decodePermToEdge(ps: Int): Pair<IntArray, IntArray> {
    val comb = ps / 24
    val permOrder = Combinatorics.permFromIdx(ps % 24, 4)
    val cnk = Combinatorics.cnkTable()
    val nonCross = intArrayOf(0, 1, 2, 3, 8, 9, 10, 11)
    val ep = IntArray(12) { it }
    val eo = IntArray(12)

    val crossPos = mutableListOf<Int>()
    var combCopy = comb
    var rCopy = 4
    for (i in 0..11) {
        if (combCopy >= cnk[11 - i][rCopy]) {
            combCopy -= cnk[11 - i][rCopy]
            crossPos.add(i)
            rCopy--
        }
    }
    var nonCrossIdx = 0
    for (i in 0..11) {
        if (i !in crossPos) {
            ep[i] = nonCross[nonCrossIdx]
            nonCrossIdx++
        }
    }
    for ((idx, pos) in crossPos.withIndex()) {
        ep[pos] = permOrder[idx] + 4
        eo[pos] = 0
    }
    return Pair(ep, eo)
}

private fun decodeFlipToEdge(fs: Int): Pair<IntArray, IntArray> {
    val comb = fs / 16
    val flipBits = fs % 16
    val cnk = Combinatorics.cnkTable()
    val nonCross = intArrayOf(0, 1, 2, 3, 8, 9, 10, 11)
    val ep = IntArray(12) { it }
    val eo = IntArray(12)

    val crossPos = mutableListOf<Int>()
    var combCopy = comb
    var rCopy = 4
    for (i in 0..11) {
        if (combCopy >= cnk[11 - i][rCopy]) {
            combCopy -= cnk[11 - i][rCopy]
            crossPos.add(i)
            rCopy--
        }
    }
    var nonCrossIdx = 0
    for (i in 0..11) {
        if (i !in crossPos) {
            ep[i] = nonCross[nonCrossIdx]
            nonCrossIdx++
        }
    }
    var piece = 4
    var bitPos = 0
    for (pos in crossPos) {
        ep[pos] = piece
        eo[pos] = (flipBits shr bitPos) and 1
        piece++
        bitPos++
    }
    return Pair(ep, eo)
}

private fun encodePermFromEdge(ep: IntArray, eo: IntArray): Int {
    val cnk = Combinatorics.cnkTable()
    var r = 4
    var combVal = 0
    val permPieces = mutableListOf<Int>()
    for (i in 0..11) {
        if (ep[i] in 4..7) {
            combVal += cnk[11 - i][r]
            permPieces.add(ep[i] - 4)
            r--
        }
    }
    val permOrder = Combinatorics.permIdx(permPieces.toIntArray(), 4)
    return combVal * 24 + permOrder
}

private fun encodeFlipFromEdge(ep: IntArray, eo: IntArray): Int {
    val cnk = Combinatorics.cnkTable()
    var r = 4
    var combVal = 0
    var flipBits = 0
    var bitPos = 0
    for (i in 0..11) {
        if (ep[i] in 4..7) {
            combVal += cnk[11 - i][r]
            if (eo[i] != 0) flipBits = flipBits or (1 shl bitPos)
            bitPos++
            r--
        }
    }
    return combVal * 16 + flipBits
}

fun buildCrossMoveTables(): Pair<Array<IntArray>, Array<IntArray>> {
    val permMove = Array(18) { IntArray(N_CROSS_PERM) }
    val flipMove = Array(18) { IntArray(N_CROSS_FLIP) }

    for (moveIdx in 0..17) {
        val face = moveIdx / 3
        val turns = (moveIdx % 3) + 1

        for (ps in 0 until N_CROSS_PERM) {
            var (ep, eo) = decodePermToEdge(ps)
            repeat(turns) { val p = edgeMovePerm(ep, eo, face); ep = p.first; eo = p.second }
            permMove[moveIdx][ps] = encodePermFromEdge(ep, eo)
        }
        for (fs in 0 until N_CROSS_FLIP) {
            var (ep, eo) = decodeFlipToEdge(fs)
            repeat(turns) { val p = edgeMovePerm(ep, eo, face); ep = p.first; eo = p.second }
            flipMove[moveIdx][fs] = encodeFlipFromEdge(ep, eo)
        }
    }
    return Pair(permMove, flipMove)
}

fun buildCrossPrun(permMove: Array<IntArray>, flipMove: Array<IntArray>): Pair<ByteArray, ByteArray> {
    val solved = CubieCube.solved()
    val solvedPerm = getCrossPermCoord(solved)
    val solvedFlip = getCrossFlipCoord(solved)

    val permPrun = ByteArray(N_CROSS_PERM) { -1 }
    val flipPrun = ByteArray(N_CROSS_FLIP) { -1 }
    permPrun[solvedPerm] = 0
    flipPrun[solvedFlip] = 0

    val permQueue = ArrayDeque<Int>()
    permQueue.addLast(solvedPerm)
    while (permQueue.isNotEmpty()) {
        val idx = permQueue.removeFirst()
        val d = permPrun[idx].toInt()
        for (m in 0..17) {
            val nxt = permMove[m][idx]
            if (permPrun[nxt] == (-1).toByte()) {
                permPrun[nxt] = (d + 1).toByte()
                permQueue.addLast(nxt)
            }
        }
    }

    val flipQueue = ArrayDeque<Int>()
    flipQueue.addLast(solvedFlip)
    while (flipQueue.isNotEmpty()) {
        val idx = flipQueue.removeFirst()
        val d = flipPrun[idx].toInt()
        for (m in 0..17) {
            val nxt = flipMove[m][idx]
            if (flipPrun[nxt] == (-1).toByte()) {
                flipPrun[nxt] = (d + 1).toByte()
                flipQueue.addLast(nxt)
            }
        }
    }

    return Pair(permPrun, flipPrun)
}

fun pairToCube(pc: Int, pairIdx: Int): CubieCube {
    val (cornerPiece, edgePiece) = Combinatorics.F2L_PAIRS[pairIdx]
    val cpSlot = pc / (24 * 3)
    val coVal = (pc / 24) % 3
    val epSlot = (pc % 24) / 2
    val eoVal = pc % 2
    val cube = CubieCube()
    for (i in 0..7) {
        if (cube.cp[i] == cornerPiece && i != cpSlot) {
            cube.cp[i] = cube.cp[cpSlot]
            break
        }
    }
    cube.cp[cpSlot] = cornerPiece
    cube.co[cpSlot] = coVal
    for (i in 0..11) {
        if (cube.ep[i] == edgePiece && i != epSlot) {
            cube.ep[i] = cube.ep[epSlot]
            break
        }
    }
    cube.ep[epSlot] = edgePiece
    cube.eo[epSlot] = eoVal
    return cube
}

fun buildPairMoveTables(): Array<Array<IntArray>> {
    val pairMove = Array(4) { Array(15) { IntArray(576) } }
    for (pairIdx in 0..3) {
        for ((mi, moveIdx) in Combinatorics.F2L_MOVE_INDICES.withIndex()) {
            val face = moveIdx / 3
            val turns = (moveIdx % 3) + 1
            for (pc in 0..575) {
                var s = pairToCube(pc, pairIdx)
                repeat(turns) { s.applyCw(face) }
                pairMove[pairIdx][mi][pc] = getPairCoord(s, pairIdx)
            }
        }
    }
    return pairMove
}

fun buildPairPrun(pairMove: Array<Array<IntArray>>): Array<ByteArray> {
    val pairPrun = Array(4) { ByteArray(576) { -1 } }
    for (pairIdx in 0..3) {
        val solved = pairSolvedCoord(pairIdx)
        pairPrun[pairIdx][solved] = 0
        val queue = ArrayDeque<Int>()
        queue.addLast(solved)
        while (queue.isNotEmpty()) {
            val idx = queue.removeFirst()
            val d = pairPrun[pairIdx][idx].toInt()
            if (d > 11) continue
            for (mi in 0..14) {
                val nxt = pairMove[pairIdx][mi][idx]
                if (pairPrun[pairIdx][nxt] == (-1).toByte()) {
                    pairPrun[pairIdx][nxt] = (d + 1).toByte()
                    queue.addLast(nxt)
                }
            }
        }
    }
    return pairPrun
}

fun buildMacroPairMoveTables(): Array<Array<IntArray>> {
    val macroMove = Array(4) { Array(Combinatorics.N_F2L_MACROS) { IntArray(576) } }
    for (pairIdx in 0..3) {
        for ((macroIdx, macroSeq) in Combinatorics.F2L_MACRO_MOVES.withIndex()) {
            for (pc in 0..575) {
                var s = pairToCube(pc, pairIdx)
                for (m in macroSeq) s.applyMoveIdx(m)
                macroMove[pairIdx][macroIdx][pc] = getPairCoord(s, pairIdx)
            }
        }
    }
    return macroMove
}

fun buildMacroPairPrun(macroMove: Array<Array<IntArray>>): Array<ByteArray> {
    val macroPrun = Array(4) { ByteArray(576) { -1 } }
    for (pairIdx in 0..3) {
        val solved = pairSolvedCoord(pairIdx)
        macroPrun[pairIdx][solved] = 0
        val queue = ArrayDeque<Int>()
        queue.addLast(solved)
        while (queue.isNotEmpty()) {
            val idx = queue.removeFirst()
            val d = macroPrun[pairIdx][idx].toInt()
            if (d >= 15) continue
            for (macroIdx in 0 until Combinatorics.N_F2L_MACROS) {
                val nxt = macroMove[pairIdx][macroIdx][idx]
                if (macroPrun[pairIdx][nxt] == (-1).toByte()) {
                    macroPrun[pairIdx][nxt] = (d + 1).toByte()
                    queue.addLast(nxt)
                }
            }
        }
    }
    return macroPrun
}

fun movesToStr(moveIndices: List<Int>): String {
    return moveIndices.joinToString(" ") { CubieCube.MOVE_NAMES[it] }
}

fun mergeConsecutiveMoves(moveIndices: List<Int>): List<Int> {
    if (moveIndices.isEmpty()) return emptyList()
    val result = mutableListOf<Int>()
    var i = 0
    while (i < moveIndices.size) {
        val face = moveIndices[i] / 3
        var totalTurns = (moveIndices[i] % 3) + 1
        var j = i + 1
        while (j < moveIndices.size && moveIndices[j] / 3 == face) {
            totalTurns += (moveIndices[j] % 3) + 1
            j++
        }
        totalTurns %= 4
        when (totalTurns) {
            1 -> result.add(face * 3)       // CW
            2 -> result.add(face * 3 + 1)   // half
            3 -> result.add(face * 3 + 2)   // CCW
        }
        i = j
    }
    return result
}

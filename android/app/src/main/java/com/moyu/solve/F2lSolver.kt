package com.moyu.solve

object F2lSolver {
    var f2lNodes = 0L

    fun solve(
        state: CubieCube,
        pairPrun: Array<ByteArray>,
        pairMove: Array<Array<IntArray>>,
        macroPrun: Array<ByteArray>?,
        macroMove: Array<Array<IntArray>>?
    ): Pair<List<Int>, CubieCube>? {
        val fullMoves = mutableListOf<Int>()
        val solvedPairs = mutableSetOf<Int>()
        for (i in 0..3) {
            if (pairIsSolved(state, i)) solvedPairs.add(i)
        }

        for (step in 0..3) {
            val remaining = (0..3).filter { it !in solvedPairs }
            if (remaining.isEmpty()) break

            val heuristic = remaining.map { pairPrun[it][getPairCoord(state, it)].toInt() to it }.sortedBy { it.first }

            var found = false
            for ((_, pairIdx) in heuristic) {
                var path = solveF2lPair(state, pairIdx, pairPrun, pairMove, maxDepth = 6, protectedPairs = solvedPairs)

                if (path == null && macroPrun != null && macroMove != null) {
                    path = solveF2lPairMacro(state, pairIdx, macroPrun, macroMove, maxDepth = 8, protectedPairs = solvedPairs)
                }

                if (path != null) {
                    fullMoves.addAll(path)
                    for (m in path) state.applyMoveIdx(m)
                    if (!pairIsSolved(state, pairIdx)) return null
                    solvedPairs.add(pairIdx)
                    found = true
                    break
                }
            }
            if (!found) return null
        }

        val topCorners = (0..3).map { state.cp[it] }.toSet()
        val topEdges = (0..3).map { state.ep[it] }.toSet()
        if (topCorners != setOf(0, 1, 2, 3) || topEdges != setOf(0, 1, 2, 3)) return null

        return Pair(fullMoves, state)
    }

    private fun solveF2lPair(
        state: CubieCube, pairIdx: Int,
        pairPrun: Array<ByteArray>, pairMove: Array<Array<IntArray>>,
        maxDepth: Int = 10, protectedPairs: Set<Int> = emptySet()
    ): List<Int>? {
        if (pairIsSolved(state, pairIdx)) {
            if (checkCrossIntact(state) && protectedPairs.all { pairIsSolved(state, it) }) return emptyList()
        }
        for (depth in 1..maxDepth) {
            f2lNodes = 0
            val path = mutableListOf<Int>()
            if (f2lIda(state, pairIdx, depth, -1, path, pairPrun, pairMove, protectedPairs)) {
                return path
            }
        }
        return null
    }

    private fun f2lIda(
        state: CubieCube, pairIdx: Int,
        remaining: Int, lastFace: Int,
        path: MutableList<Int>,
        pairPrun: Array<ByteArray>, pairMove: Array<Array<IntArray>>,
        protectedPairs: Set<Int>
    ): Boolean {
        f2lNodes++
        val h = pairPrun[pairIdx][getPairCoord(state, pairIdx)].toInt()
        if (h > remaining) return false
        if (remaining == 0) {
            if (!pairIsSolved(state, pairIdx)) return false
            if (protectedPairs.any { !pairIsSolved(state, it) }) return false
            if (!checkCrossIntact(state)) return false
            return true
        }
        val nextMoves = getNextF2lMoves(Combinatorics.F2L_MOVE_INDICES, lastFace)
        for (m in nextMoves) {
            val ns = state.applyMoveIdxCopy(m)
            path.add(m)
            if (f2lIda(ns, pairIdx, remaining - 1, m / 3, path, pairPrun, pairMove, protectedPairs)) return true
            path.removeAt(path.size - 1)
        }
        return false
    }

    private fun solveF2lPairMacro(
        state: CubieCube, pairIdx: Int,
        macroPrun: Array<ByteArray>,
        macroMove: Array<Array<IntArray>>,
        maxDepth: Int = 8, protectedPairs: Set<Int> = emptySet()
    ): List<Int>? {
        if (pairIsSolved(state, pairIdx)) {
            if (checkCrossIntact(state) && protectedPairs.all { pairIsSolved(state, it) }) return emptyList()
        }
        for (depth in 1..maxDepth) {
            f2lNodes = 0
            val path = mutableListOf<Int>()
            if (f2lMacroIda(state, pairIdx, depth, -1, path, macroPrun, protectedPairs)) {
                val moves = mutableListOf<Int>()
                for (macroIdx in path) {
                    moves.addAll(Combinatorics.F2L_MACRO_MOVES[macroIdx])
                }
                return moves
            }
        }
        return null
    }

    private fun f2lMacroIda(
        state: CubieCube, pairIdx: Int,
        remaining: Int, lastMacroFace: Int,
        path: MutableList<Int>,
        macroPrun: Array<ByteArray>,
        protectedPairs: Set<Int>
    ): Boolean {
        f2lNodes++
        val h = macroPrun[pairIdx][getPairCoord(state, pairIdx)].toInt()
        if (h > remaining) return false
        if (remaining == 0) {
            if (!pairIsSolved(state, pairIdx)) return false
            if (protectedPairs.any { !pairIsSolved(state, it) }) return false
            if (!checkCrossIntact(state)) return false
            return true
        }
        for ((macroIdx, macroSeq) in Combinatorics.F2L_MACRO_MOVES.withIndex()) {
            val macroFace = when {
                macroSeq.size == 3 -> macroSeq[0] / 3
                macroSeq[0] / 3 == 0 -> 0
                else -> 3
            }
            if (macroFace == lastMacroFace) continue
            val opp = Combinatorics.OPPOSITE_FACE[lastMacroFace] ?: -1
            if (macroFace == opp && macroFace < lastMacroFace) continue

            var ns = state.copy()
            for (m in macroSeq) ns.applyMoveIdx(m)
            path.add(macroIdx)
            if (f2lMacroIda(ns, pairIdx, remaining - 1, macroFace, path, macroPrun, protectedPairs)) return true
            path.removeAt(path.size - 1)
        }
        return false
    }

    private fun getNextF2lMoves(moves: List<Int>, lastFace: Int): List<Int> {
        val opp = Combinatorics.OPPOSITE_FACE
        return moves.filter { m ->
            val face = m / 3
            face != lastFace && !(face == opp[lastFace] && lastFace > face)
        }
    }
}

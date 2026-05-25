package com.moyu.solve

import android.util.Log

object CrossSolver {
    fun solve(
        state: CubieCube,
        permPrun: ByteArray,
        flipPrun: ByteArray,
        permMove: Array<IntArray>,
        flipMove: Array<IntArray>,
        maxDepth: Int = 8
    ): List<Int>? {
        val perm0 = getCrossPermCoord(state)
        val flip0 = getCrossFlipCoord(state)
        if (permPrun[perm0].toInt() == 0 && flipPrun[flip0].toInt() == 0) return emptyList()

        for (depth in 1..maxDepth) {
            if (CfopSolver.DEBUG) {
                Log.d("Cross", "searching depth=$depth")
                CfopSolver.logFn?.invoke("cross depth=$depth")
            }
            val path = mutableListOf<Int>()
            if (crossIda(perm0, flip0, depth, -1, path, permPrun, flipPrun, permMove, flipMove)) {
                return path
            }
        }
        return null
    }

    private fun crossIda(
        perm: Int, flip: Int,
        remaining: Int, lastFace: Int,
        path: MutableList<Int>,
        permPrun: ByteArray, flipPrun: ByteArray,
        permMove: Array<IntArray>, flipMove: Array<IntArray>
    ): Boolean {
        val h = maxOf(permPrun[perm].toInt(), flipPrun[flip].toInt())
        if (h > remaining) return false
        if (remaining == 0) return permPrun[perm].toInt() == 0 && flipPrun[flip].toInt() == 0

        val nextMoves = getNextMoves(0..17, lastFace)
        for (m in nextMoves) {
            val np = permMove[m][perm]
            val nf = flipMove[m][flip]
            path.add(m)
            if (crossIda(np, nf, remaining - 1, m / 3, path, permPrun, flipPrun, permMove, flipMove)) return true
            path.removeAt(path.size - 1)
        }
        return false
    }

    private fun getNextMoves(moves: IntRange, lastFace: Int): List<Int> {
        val opp = Combinatorics.OPPOSITE_FACE
        return moves.filter { m ->
            val face = m / 3
            face != lastFace && !(face == opp[lastFace] && lastFace > face)
        }
    }
}

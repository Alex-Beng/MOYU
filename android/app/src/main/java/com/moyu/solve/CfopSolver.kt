package com.moyu.solve

class CfopSolver {
    data class SolveResult(
        val cross: String,
        val f2l: String,
        val oll: String?,
        val pll: String?,
        val alll: String?,
        val solution: String
    )

    private var permMove: Array<IntArray>? = null
    private var flipMove: Array<IntArray>? = null
    private var permPrun: ByteArray? = null
    private var flipPrun: ByteArray? = null
    private var pairMove: Array<Array<IntArray>>? = null
    private var pairPrun: Array<ByteArray>? = null
    private var macroPairMove: Array<Array<IntArray>>? = null
    private var macroPairPrun: Array<ByteArray>? = null
    private var ollRec: Map<FourFourKey, Pair<String,String>>? = null
    private var pllRec: Map<FourFourKey, Pair<String,String>>? = null
    private var alllRec: Map<String, Pair<String,String>>? = null

    private var initialized = false

    fun init() {
        if (initialized) return
        val (pm, fm) = buildCrossMoveTables()
        permMove = pm; flipMove = fm
        val (pp, fp) = buildCrossPrun(pm, fm)
        permPrun = pp; flipPrun = fp

        val pMove = buildPairMoveTables()
        pairMove = pMove
        pairPrun = buildPairPrun(pMove)

        val mpMove = buildMacroPairMoveTables()
        macroPairMove = mpMove
        macroPairPrun = buildMacroPairPrun(mpMove)

        ollRec = LLSolver.buildOllRecognition()
        pllRec = LLSolver.buildPllRecognition()

        initialized = true
    }

    fun solve(faceletStr: String): SolveResult? {
        if (!initialized) init()

        var state = CubieCube.fromFacelet(faceletStr)
        if (state.isSolved()) return SolveResult("", "", null, null, null, "")

        val crossMoves = CrossSolver.solve(
            state, permPrun!!, flipPrun!!, permMove!!, flipMove!!
        ) ?: run { return null }
        val crossStr = movesToStr(crossMoves)
        for (m in crossMoves) state.applyMoveIdx(m)

        val f2lResult = F2lSolver.solve(
            state, pairPrun!!, pairMove!!, macroPairPrun, macroPairMove
        ) ?: run { return null }
        val (f2lMoves, f2lState) = f2lResult
        val f2lStr = movesToStr(f2lMoves)
        state = f2lState

        val ollResult = LLSolver.solveOll(state, ollRec!!)
        val (ollAlg, ollState) = ollResult
        if (ollAlg == null) return null
        val ollStr = ollAlg
        state = ollState

        val pllResult = LLSolver.solvePll(state, pllRec!!)
        val (pllAlg, _) = pllResult
        if (pllAlg == null) return null
        val pllStr = pllAlg

        val parts = listOfNotNull(crossStr, f2lStr, ollStr, pllStr).filter { it.isNotEmpty() }
        val solution = parts.joinToString(" ")

        return SolveResult(
            cross = crossStr,
            f2l = f2lStr,
            oll = ollStr,
            pll = pllStr,
            alll = null,
            solution = solution
        )
    }
}

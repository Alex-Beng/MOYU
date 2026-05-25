package com.moyu.solve

import android.util.Log

object LLSolver {
    private const val TAG = "LLSolver"
    val OLL_ALGS = mapOf(
        1 to "R U2 R2 F R F' U2 R' F R F'",
        2 to "y' R U' R2 D' r U r' D R2 U R'",
        3 to "r' R2 U R' U r U2 r' U M'",
        4 to "y' R' F2 R2 U2 R' F' R U2 R2 F2 R",
        5 to "r' U2 R U R' U r",
        6 to "r U2 R' U' R U' r'",
        7 to "r U R' U R U2 r'",
        8 to "y2 r' U' R U' R' U2 r",
        9 to "y R U R' U' R' F R2 U R' U' F'",
        10 to "R U R' U R' F R F' R U2 R'",
        11 to "r' R2 U R' U R U2 R' U M'",
        12 to "y' M' R' U' R U' R' U2 R U' M",
        13 to "F U R U2 R' U' R U R' F'",
        14 to "R' F R U R' F' R F U' F'",
        15 to "r' U' r R' U' R U r' U r",
        16 to "r U r' R U R' U' r U' r'",
        17 to "R U R' U R' F R F' U2 R' F R F'",
        18 to "y R U2 R2 F R F' U2 M' U R U' r'",
        19 to "y S' R U R' S U' R' F R F'",
        20 to "r U R' U' M2 U R U' R' U' M'",
        21 to "R U R' U R U' R' U R U2 R'",
        22 to "R U2 R2 U' R2 U' R2 U2 R",
        23 to "R2 D R' U2 R D' R' U2 R'",
        24 to "r U R' U' r' F R F'",
        25 to "R U2 R D R' U2 R D' R2",
        26 to "y R U2 R' U' R U' R'",
        27 to "R U R' U R U2 R'",
        28 to "r U R' U' M U R U' R'",
        29 to "r2 D' r U r' D r2 U' r' U' r",
        30 to "y' r' D' r U' r' D r2 U' r' U r U r'",
        31 to "R' U' F U R U' R' F' R",
        32 to "S R U R' U' R' F R f'",
        33 to "R U R' U' R' F R F'",
        34 to "y f R f' U' r' U' R U M'",
        35 to "R U2 R2 F R F' R U2 R'",
        36 to "y R U R2 F' U' F U R2 U2 R'",
        37 to "F R' F' R U R U' R'",
        38 to "R U R' U R U' R' U' R' F R F'",
        39 to "y' f' r U r' U' r' F r S",
        40 to "y R' F R U R' U' F' U R",
        41 to "y2 R U R' U R U2 R' F R U R' U' F'",
        42 to "R' U' R U' R' U2 R F R U R' U' F'",
        43 to "y R' U' F' U F R",
        44 to "f R U R' U' f'",
        45 to "F R U R' U' F'",
        46 to "R' U' R' F R F' U R",
        47 to "y' F R' F' R U2 R U' R' U R U2 R'",
        48 to "F R U R' U' R U R' U' F'",
        49 to "y2 r U' r2 U r2 U r2 U' r",
        50 to "r' U r2 U' r2 U' r2 U r'",
        51 to "y2 F U R U' R' U R U' R' F'",
        52 to "y2 R' F' U' F U' R U R' U R",
        53 to "r' U' R U' R' U R U' R' U2 r",
        54 to "r U R' U R U' R' U R U2 r'",
        55 to "y R' F U R U' R2 F' R2 U R' U' R",
        56 to "r U r' U R U' R' U R U' R' r U' r'",
        57 to "R U R' U' M' U R U' r'"
    )

    val PLL_ALGS = mapOf(
        "Aa" to "x R' U R' D2 R U' R' D2 R2 x'",
        "Ab" to "x R2 D2 R U R' D2 R U' R x'",
        "E" to "x' R U' R' D R U R' D' R U R' D R U' R' D' x",
        "F" to "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
        "Ga" to "R2 U R' U R' U' R U' R2 D U' R' U R D'",
        "Gb" to "R' U' R U D' R2 U R' U R U' R U' R2 D",
        "Gc" to "R2 U' R U' R U R' U R2 D' U R U' R' D",
        "Gd" to "R U R' U' D R2 U' R U' R' U R' U R2 D'",
        "H" to "M2 U M2 U2 M2 U M2",
        "Ja" to "R' U L' U2 R U' R' U2 R L x'",
        "Jb" to "R U R' F' R U R' U' R' F R2 U' R'",
        "Na" to "R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'",
        "Nb" to "R' U R U' R' F' U' F R U R' F R' F' R U' R",
        "Ra" to "R U R' F' R U2 R' U2 R' F R U R U2 R'",
        "Rb" to "R' U2 R U2 R' F R U R' U' R' F' R2",
        "T" to "R U R' U' R' F R2 U' R' U' R U R' F'",
        "Ua" to "R U' R U R U R U' R' U' R2",
        "Ub" to "R2 U R U R' U' R' U' R' U R'",
        "V" to "R' U R' U' R D' R' D R' U D' R2 U' R2 D R2",
        "Y" to "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        "Z" to "M' U M2 U M2 U M' U2 M2"
    )

    fun buildOllRecognition(): Map<FourFourKey, Pair<String, String>> {
        val table = mutableMapOf<FourFourKey, Pair<String, String>>()
        val solved = CubieCube.solved()
        for ((name, alg) in OLL_ALGS) {
            val basic = AlgParser.convertAlgToBasic(alg).first
            val inv = invertAlg(basic)
            val s = applyAlgStr(solved.copy(), inv)
            val coKey = FourInts(s.co[0], s.co[1], s.co[2], s.co[3])
            val eoKey = FourInts(s.eo[0], s.eo[1], s.eo[2], s.eo[3])
            val key = FourFourKey(coKey, eoKey)
            if (key !in table) table[key] = Pair("OLL_$name", basic)
        }
        val solvedCo = FourInts(0, 0, 0, 0)
        val solvedEo = FourInts(0, 0, 0, 0)
        table[FourFourKey(solvedCo, solvedEo)] = Pair("skip", "")
        return table
    }

    fun buildPllRecognition(): Map<FourFourKey, Pair<String, String>> {
        val table = mutableMapOf<FourFourKey, Pair<String, String>>()
        val solved = CubieCube.solved()
        val aufStrs = mapOf(0 to "", 1 to "U", 2 to "U2", 3 to "U'")
        for ((name, alg) in PLL_ALGS) {
            val basic = AlgParser.convertAlgToBasic(alg).first
            for (pre in 0..3) for (post in 0..3) {
                val preStr = aufStrs[pre]!!
                val postStr = aufStrs[post]!!
                val fullAlg = listOfNotNull(preStr, basic, postStr).filter { it.isNotEmpty() }.joinToString(" ")
                val invFull = invertAlg(fullAlg)
                val s = applyAlgStr(solved.copy(), invFull)
                val cpKey = FourInts(s.cp[0], s.cp[1], s.cp[2], s.cp[3])
                val epKey = FourInts(s.ep[0], s.ep[1], s.ep[2], s.ep[3])
                val k = FourFourKey(cpKey, epKey)
                if (k !in table || fullAlg.length < table[k]!!.second.length) {
                    table[k] = Pair("PLL_$name", fullAlg)
                }
            }
        }
        val solvedCp = FourInts(0, 1, 2, 3)
        val solvedEp = FourInts(0, 1, 2, 3)
        table[FourFourKey(solvedCp, solvedEp)] = Pair("skip", "")
        return table
    }

    fun solveOll(state: CubieCube, ollRec: Map<FourFourKey, Pair<String, String>>): Pair<String?, CubieCube> {
        for (auf in 0..3) {
            val test = state.applyURot(auf)
            val coKey = FourInts(test.co[0], test.co[1], test.co[2], test.co[3])
            val eoKey = FourInts(test.eo[0], test.eo[1], test.eo[2], test.eo[3])
            val key = FourFourKey(coKey, eoKey)
            if (key in ollRec) {
                val (name, alg) = ollRec[key]!!
                if (CfopSolver.DEBUG) {
                    Log.d(TAG, "OLL case=$name auf=$auf alg=$alg")
                    CfopSolver.logFn?.invoke("oll case=$name alg=$alg")
                }
                val aufStr = mapOf(0 to "", 1 to "U", 2 to "U2", 3 to "U'" )[auf]!!
                if (name == "skip") return Pair("", state)
                val full = listOfNotNull(aufStr, alg).filter { it.isNotEmpty() }.joinToString(" ")
                val newState = applyAlgStr(state, full)
                return Pair(full, newState)
            }
        }
        return Pair(null, state)
    }

    fun solvePll(state: CubieCube, pllRec: Map<FourFourKey, Pair<String, String>>): Pair<String?, CubieCube> {
        for (auf in 0..3) {
            val test = state.applyURot(auf)
            val cpKey = FourInts(test.cp[0], test.cp[1], test.cp[2], test.cp[3])
            val epKey = FourInts(test.ep[0], test.ep[1], test.ep[2], test.ep[3])
            val key = FourFourKey(cpKey, epKey)
            if (key in pllRec) {
                val (name, alg) = pllRec[key]!!
                if (CfopSolver.DEBUG) {
                    Log.d(TAG, "PLL case=$name auf=$auf alg=$alg")
                    CfopSolver.logFn?.invoke("pll case=$name alg=$alg")
                }
                val aufStr = mapOf(0 to "", 1 to "U", 2 to "U2", 3 to "U'" )[auf]!!
                if (name == "skip") return Pair("", state)
                val full = listOfNotNull(aufStr, alg).filter { it.isNotEmpty() }.joinToString(" ")
                val newState = applyAlgStr(state, full)
                return Pair(full, newState)
            }
        }
        return Pair(null, state)
    }
}

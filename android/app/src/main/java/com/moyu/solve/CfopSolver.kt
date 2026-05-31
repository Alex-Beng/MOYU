package com.moyu.solve

import android.util.Log
import java.io.File
import java.io.ObjectInputStream
import java.io.ObjectOutputStream

class CfopSolver {
    companion object {
        var DEBUG = false
        private const val TAG = "CfopSolver"

        private val CW  = intArrayOf(6, 3, 0, 7, 4, 1, 8, 5, 2)
        private val CCW = intArrayOf(2, 5, 8, 1, 4, 7, 0, 3, 6)
        private val I180 = intArrayOf(8, 7, 6, 5, 4, 3, 2, 1, 0)
        private val ID  = intArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8)

        private val ROTATION_RULES: Map<String, List<Triple<Int, Int, IntArray>>> = mapOf(
            "z"  to listOf(Triple(0,4,CW), Triple(1,0,CW), Triple(2,2,CW), Triple(3,1,CW), Triple(4,3,CW), Triple(5,5,CCW)),
            "z'" to listOf(Triple(0,1,CCW),Triple(1,3,CCW),Triple(2,2,CCW),Triple(3,4,CCW),Triple(4,0,CCW),Triple(5,5,CW)),
            "z2" to listOf(Triple(0,3,I180),Triple(1,4,I180),Triple(2,2,I180),Triple(3,0,I180),Triple(4,1,I180),Triple(5,5,I180)),
            "x"  to listOf(Triple(0,2,ID), Triple(1,1,CW), Triple(2,3,ID), Triple(3,5,I180),Triple(4,4,CCW),Triple(5,0,I180)),
            "x'" to listOf(Triple(0,5,I180),Triple(1,1,CCW),Triple(2,0,ID), Triple(3,2,ID), Triple(4,4,CW), Triple(5,3,I180)),
        )

        private val FACE_CHARS = charArrayOf('U', 'R', 'F', 'D', 'L', 'B')
        private val COLOR_MAP: Map<String, IntArray> = mapOf(
            "z"  to intArrayOf(4,0,2,1,3,5),
            "z'" to intArrayOf(1,3,2,4,0,5),
            "z2" to intArrayOf(3,4,2,0,1,5),
            "x"  to intArrayOf(2,1,3,5,4,0),
            "x'" to intArrayOf(5,1,0,2,4,3),
        )

        fun applyFaceletRotation(faceletStr: String, rot: String): String {
            val rules = ROTATION_RULES[rot] ?: return faceletStr
            val faces = Array(6) { faceletStr.substring(it * 9, (it + 1) * 9) }
            val result = CharArray(54)
            for ((dst, src, perm) in rules) {
                val srcFace = faces[src]
                for (j in 0 until 9) {
                    result[dst * 9 + j] = srcFace[perm[j]]
                }
            }
            val cmap = COLOR_MAP[rot] ?: return String(result)
            val sb = StringBuilder()
            for (c in result) {
                val idx = "URFDLB".indexOf(c)
                sb.append(if (idx >= 0) FACE_CHARS[cmap[idx]] else c)
            }
            return sb.toString()
        }

        private fun dbg(msg: String) {
            if (DEBUG) {
                Log.d(TAG, msg)
                logFn?.invoke(msg)
            }
        }

        var logFn: ((String) -> Unit)? = null
    }

    var alllProb: Float = 0.1f

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
    private var alllRec: Map<AlllKey, Pair<String, String>>? = null
    var cacheDir: File? = null

    private var initialized = false

    fun init() {
        dbg("init: building move tables...")
        val (pm, fm) = buildCrossMoveTables()
        permMove = pm; flipMove = fm
        val (pp, fp) = buildCrossPrun(pm, fm)
        permPrun = pp; flipPrun = fp
        dbg("init: cross tables done")

        val pMove = buildPairMoveTables()
        pairMove = pMove
        pairPrun = buildPairPrun(pMove)
        dbg("init: pair tables done")

        val mpMove = buildMacroPairMoveTables()
        macroPairMove = mpMove
        macroPairPrun = buildMacroPairPrun(mpMove)
        dbg("init: macro pair tables done")

        ollRec = LLSolver.buildOllRecognition()
        pllRec = LLSolver.buildPllRecognition()
        val cached = loadAlllCache()
        alllRec = if (cached != null && cached.size > 1000) {
            dbg("init: ALLL loaded from cache (${cached.size} entries)")
            cached
        } else {
            dbg("init: building ALLL table...")
            LLSolver.buildAlllRecognition().also { saveAlllCache(it) }
        }
        dbg("init: OLL/PLL/ALLL recognition done (oll=${ollRec!!.size}, pll=${pllRec!!.size}, alll=${alllRec!!.size})")

        initialized = true
    }

    private fun alllCacheFile(): File? = cacheDir?.resolve("alll_rec_v2.cache")

    @Suppress("UNCHECKED_CAST")
    private fun loadAlllCache(): Map<AlllKey, Pair<String, String>>? {
        val f = alllCacheFile() ?: return null
        if (!f.exists()) return null
        return try {
            ObjectInputStream(f.inputStream().buffered()).use { it.readObject() as Map<AlllKey, Pair<String, String>> }
        } catch (_: Exception) {
            f.delete()
            null
        }
    }

    fun alllRecSize(): Int = alllRec?.size ?: -1

    private fun saveAlllCache(table: Map<AlllKey, Pair<String, String>>) {
        val f = alllCacheFile() ?: return
        try {
            ObjectOutputStream(f.outputStream().buffered()).use { it.writeObject(table) }
        } catch (_: Exception) {}
    }

    fun rebuildAlllCache() {        alllCacheFile()?.delete()
        alllRec = LLSolver.buildAlllRecognition().also { saveAlllCache(it) }
        dbg("ALLL table rebuilt: ${alllRec!!.size} entries")
    }

    fun solve(faceletStr: String, rotation: String? = null): SolveResult? {
        if (!initialized) init()
        dbg("solve: alllProb=$alllProb alllSize=${alllRec?.size}")

        var fc = faceletStr
        if (!rotation.isNullOrBlank()) {
            dbg("rotation=$rotation applying facelet rotation")
            fc = applyFaceletRotation(fc, rotation)
        }

        dbg("facelet=$fc")
        val t0 = System.currentTimeMillis()

        var state = CubieCube.fromFacelet(fc)
        if (state.isSolved()) {
            dbg("already solved")
            return SolveResult("", "", null, null, null, "")
        }

        val crossMoves = CrossSolver.solve(
            state, permPrun!!, flipPrun!!, permMove!!, flipMove!!
        ) ?: run { dbg("cross FAILED"); return null }
        val crossStr = movesToStr(crossMoves)
        val t1 = System.currentTimeMillis()
        dbg("cross = $crossStr  (${crossMoves.size}m, ${t1-t0}ms)")
        for (m in crossMoves) state.applyMoveIdx(m)

        val f2lResult = F2lSolver.solve(
            state, pairPrun!!, pairMove!!, macroPairPrun, macroPairMove
        ) ?: run { dbg("f2l FAILED"); return null }
        val (f2lMoves, f2lState) = f2lResult
        val f2lStr = movesToStr(f2lMoves)
        val t2 = System.currentTimeMillis()
        dbg("f2l = $f2lStr  (${f2lMoves.size}m, ${t2-t1}ms)")
        state = f2lState

        var ollStr = ""
        var pllStr = ""
        var alllStr: String? = null
        var alllFound = false

        val alllResult = if (alllProb > 0f && (alllProb >= 1.0f || Math.random() < alllProb)) {
            dbg("alll: trying (prob=$alllProb, tableSize=${alllRec!!.size})")
            LLSolver.solveAlll(state, alllRec!!)
        } else {
            Pair(null, state)
        }
        if (alllResult.first != null) {
            alllStr = alllResult.first
            state = alllResult.second
            alllFound = true
            dbg("alll = $alllStr")
        } else {
            dbg("alll not found, falling back to OLL+PLL")
            val ollResult = LLSolver.solveOll(state, ollRec!!)
            val (ollAlg, ollState) = ollResult
            if (ollAlg == null) {
                dbg("oll FAILED  co=${state.co.contentToString()} eo=${state.eo.contentToString()}")
                return null
            }
            ollStr = ollAlg
            dbg("oll = $ollStr")
            state = ollState

            val pllResult = LLSolver.solvePll(state, pllRec!!)
            val (pllAlg, _) = pllResult
            if (pllAlg == null) {
                dbg("pll FAILED  cp=${state.cp.contentToString()} ep=${state.ep.contentToString()}")
                return null
            }
            pllStr = pllAlg
            dbg("pll = $pllStr")
        }

        val t3 = System.currentTimeMillis()

        val parts = if (alllFound) {
            listOfNotNull(crossStr, f2lStr, alllStr).filter { it.isNotEmpty() }
        } else {
            listOfNotNull(crossStr, f2lStr, ollStr, pllStr).filter { it.isNotEmpty() }
        }
        val sol = parts.joinToString(" ")

        val finalCross: String
        val finalF2l: String
        val finalOll: String?
        val finalPll: String?
        val finalAlll: String?
        val fullSolution: String

        if (!rotation.isNullOrBlank()) {
            val prefix = rotation
            val wrap = { s: String -> if (s.isNotEmpty()) "$prefix $s" else prefix }
            val (c, _) = AlgParser.convertAlgToBasic(wrap(crossStr))
            val (f, _) = AlgParser.convertAlgToBasic(wrap(f2lStr))
            val (sln, _) = AlgParser.convertAlgToBasic(wrap(sol))
            if (alllFound) {
                val (a, _) = if (!alllStr.isNullOrEmpty()) AlgParser.convertAlgToBasic(wrap(alllStr)) else Pair("", "")
                finalCross = c; finalF2l = f; finalOll = null; finalPll = null; finalAlll = a; fullSolution = sln
            } else {
                val (o, _) = if (ollStr.isNotEmpty()) AlgParser.convertAlgToBasic(wrap(ollStr)) else Pair("", "")
                val (p, _) = if (pllStr.isNotEmpty()) AlgParser.convertAlgToBasic(wrap(pllStr)) else Pair("", "")
                finalCross = c; finalF2l = f; finalOll = o; finalPll = p; finalAlll = null; fullSolution = sln
            }
        } else {
            if (alllFound) {
                finalCross = crossStr; finalF2l = f2lStr; finalOll = null; finalPll = null; finalAlll = alllStr; fullSolution = sol
            } else {
                finalCross = crossStr; finalF2l = f2lStr; finalOll = ollStr; finalPll = pllStr; finalAlll = null; fullSolution = sol
            }
        }

        dbg("solution = $fullSolution  (total ${t3-t0}ms)")

        return SolveResult(
            cross = finalCross,
            f2l = finalF2l,
            oll = finalOll,
            pll = finalPll,
            alll = finalAlll,
            solution = fullSolution
        )

    }
}

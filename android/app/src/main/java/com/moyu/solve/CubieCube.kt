package com.moyu.solve

class CubieCube(
    cp: IntArray = intArrayOf(0, 1, 2, 3, 4, 5, 6, 7),
    co: IntArray = intArrayOf(0, 0, 0, 0, 0, 0, 0, 0),
    ep: IntArray = intArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    eo: IntArray = intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
) {
    var cp = cp.copyOf(8); private set
    var co = co.copyOf(8); private set
    var ep = ep.copyOf(12); private set
    var eo = eo.copyOf(12); private set

    fun copy(): CubieCube = CubieCube(cp, co, ep, eo)

    fun applyCw(face: Int) {
        val oldCp = cp.copyOf(8)
        val oldCo = co.copyOf(8)
        val oldEp = ep.copyOf(12)
        val oldEo = eo.copyOf(12)
        for (i in 0..7) {
            val src = MOVE_CP[face][i]
            cp[i] = oldCp[src]
            co[i] = (oldCo[src] + MOVE_CO[face][i]) % 3
        }
        for (i in 0..11) {
            val src = MOVE_EP[face][i]
            ep[i] = oldEp[src]
            eo[i] = (oldEo[src] + MOVE_EO[face][i]) % 2
        }
    }

    fun applyMove(face: Int, dir: Int) {
        val times = if (dir == 0) 1 else 3
        repeat(times) { applyCw(face) }
    }

    fun applyMoveIdx(idx: Int) {
        val face = idx / 3
        val turns = (idx % 3) + 1
        repeat(turns) { applyCw(face) }
    }

    fun applyMoveIdxInv(idx: Int) {
        val face = idx / 3
        val invTurns = when (idx % 3) {
            0 -> 3; 1 -> 2; else -> 1
        }
        repeat(invTurns) { applyCw(face) }
    }

    fun applyMoveIdxCopy(idx: Int): CubieCube {
        val s = copy()
        s.applyMoveIdx(idx)
        return s
    }

    fun isSolved(): Boolean {
        return cp.contentEquals(intArrayOf(0, 1, 2, 3, 4, 5, 6, 7)) &&
                co.contentEquals(intArrayOf(0, 0, 0, 0, 0, 0, 0, 0)) &&
                ep.contentEquals(intArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)) &&
                eo.contentEquals(intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    }

    fun applyURot(count: Int): CubieCube {
        val s = copy()
        repeat(count) { s.applyCw(0) }
        return s
    }

    companion object {
        val SOLVED_FACELET = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

        val MOVE_CP = arrayOf(
            intArrayOf(3, 0, 1, 2, 4, 5, 6, 7),
            intArrayOf(4, 1, 2, 0, 7, 5, 6, 3),
            intArrayOf(1, 5, 2, 3, 0, 4, 6, 7),
            intArrayOf(0, 1, 2, 3, 5, 6, 7, 4),
            intArrayOf(0, 2, 6, 3, 4, 1, 5, 7),
            intArrayOf(0, 1, 3, 7, 4, 5, 2, 6)
        )

        val MOVE_CO = arrayOf(
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(2, 0, 0, 1, 1, 0, 0, 2),
            intArrayOf(1, 2, 0, 0, 2, 1, 0, 0),
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(0, 1, 2, 0, 0, 2, 1, 0),
            intArrayOf(0, 0, 1, 2, 0, 0, 2, 1)
        )

        val MOVE_EP = arrayOf(
            intArrayOf(3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11),
            intArrayOf(8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0),
            intArrayOf(0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11),
            intArrayOf(0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11),
            intArrayOf(0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11),
            intArrayOf(0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7)
        )

        val MOVE_EO = arrayOf(
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0),
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            intArrayOf(0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1)
        )

        val CORNER_FACELET = arrayOf(
            intArrayOf(8, 9, 20), intArrayOf(6, 18, 38), intArrayOf(0, 36, 47), intArrayOf(2, 45, 11),
            intArrayOf(29, 26, 15), intArrayOf(27, 44, 24), intArrayOf(33, 53, 42), intArrayOf(35, 17, 51)
        )

        val CORNER_COLOR = arrayOf(
            intArrayOf(0, 1, 2), intArrayOf(0, 2, 4), intArrayOf(0, 4, 5), intArrayOf(0, 5, 1),
            intArrayOf(3, 2, 1), intArrayOf(3, 4, 2), intArrayOf(3, 5, 4), intArrayOf(3, 1, 5)
        )

        val EDGE_FACELET = arrayOf(
            intArrayOf(5, 10), intArrayOf(7, 19), intArrayOf(3, 37), intArrayOf(1, 46),
            intArrayOf(32, 16), intArrayOf(28, 25), intArrayOf(30, 43), intArrayOf(34, 52),
            intArrayOf(23, 12), intArrayOf(21, 41), intArrayOf(50, 39), intArrayOf(48, 14)
        )

        val EDGE_COLOR = arrayOf(
            intArrayOf(0, 1), intArrayOf(0, 2), intArrayOf(0, 4), intArrayOf(0, 5),
            intArrayOf(3, 1), intArrayOf(3, 2), intArrayOf(3, 4), intArrayOf(3, 5),
            intArrayOf(2, 1), intArrayOf(2, 4), intArrayOf(5, 4), intArrayOf(5, 1)
        )

        val CENTER_FACELET = intArrayOf(4, 13, 22, 31, 40, 49)
        val COLOR_CHARS = charArrayOf('U', 'R', 'F', 'D', 'L', 'B')

        val MOVE_NAMES = arrayOf("U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", "D", "D2", "D'", "L", "L2", "L'", "B", "B2", "B'")

        fun solved(): CubieCube = CubieCube()

        fun fromFacelet(s: String): CubieCube {
            val f = s.toCharArray()
            val centers = CENTER_FACELET.map { f[it] }
            val cube = CubieCube()
            for (i in 0..7) {
                for (j in 0..7) {
                    for (ori in 0..2) {
                        if ((0..2).all { k ->
                                val idx = (k + ori) % 3
                                f[CORNER_FACELET[i][idx]] == COLOR_CHARS[CORNER_COLOR[j][k]]
                            }) {
                            cube.cp[i] = j
                            cube.co[i] = ori
                            break
                        }
                    }
                }
            }
            for (i in 0..11) {
                for (j in 0..11) {
                    for (ori in 0..1) {
                        if (f[EDGE_FACELET[i][(0 + ori) % 2]] == COLOR_CHARS[EDGE_COLOR[j][0]] &&
                            f[EDGE_FACELET[i][(1 + ori) % 2]] == COLOR_CHARS[EDGE_COLOR[j][1]]) {
                            cube.ep[i] = j
                            cube.eo[i] = ori
                            break
                        }
                    }
                }
            }
            return cube
        }

        fun toFacelet(cube: CubieCube): String {
            val f = SOLVED_FACELET.toCharArray()
            for (i in 0..5) f[CENTER_FACELET[i]] = COLOR_CHARS[i]
            for (i in 0..7) {
                val j = cube.cp[i]
                val ori = cube.co[i]
                for (k in 0..2)
                    f[CORNER_FACELET[i][(k + ori) % 3]] = COLOR_CHARS[CORNER_COLOR[j][k]]
            }
            for (i in 0..11) {
                val j = cube.ep[i]
                val ori = cube.eo[i]
                for (k in 0..2)
                    f[EDGE_FACELET[i][(k + ori) % 2]] = COLOR_CHARS[EDGE_COLOR[j][k]]
            }
            return String(f)
        }
    }
}

fun invertMoveStr(m: String): String {
    return when {
        m.length == 1 -> m + "'"
        m[1] == '\'' -> m[0].toString()
        m[1] == '2' -> m
        else -> m
    }
}

fun invertAlg(alg: String): String {
    val moves = alg.trim().split("\\s+".toRegex())
    return moves.reversed().joinToString(" ") { invertMoveStr(it) }
}

fun applyAlgStr(state: CubieCube, algStr: String): CubieCube {
    val basic = AlgParser.convertAlgToBasic(algStr)
    val tokens = basic.first.trim().split("\\s+".toRegex())
    val s = state.copy()
    for (t in tokens) {
        if (t.isEmpty()) continue
        val base = t[0]
        val mod = if (t.length > 1) t[1] else ' '
        val face = "URFDLB".indexOf(base)
        if (face < 0) continue
        val count = when (mod) { '\'' -> 3; '2' -> 2; else -> 1 }
        repeat(count) { s.applyCw(face) }
    }
    return s
}

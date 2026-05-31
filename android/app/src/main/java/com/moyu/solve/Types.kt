package com.moyu.solve

import java.io.Serializable

data class FourInts(val a: Int, val b: Int, val c: Int, val d: Int) : Serializable
data class FourFourKey(val first: FourInts, val second: FourInts) : Serializable
data class AlllKey(val cp: FourInts, val co: FourInts, val ep: FourInts, val eo: FourInts) : Serializable

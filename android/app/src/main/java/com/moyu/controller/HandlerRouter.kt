package com.moyu.controller

typealias StateHandler = suspend (Controller) -> String?

fun getHandlers(mode: String): Map<String, StateHandler> = when (mode) {
    "rank" -> mapOf(
        "init" to ::rankInit,
        "scramble" to ::rankScramble,
        "solve" to ::rankSolve,
        "re_rank" to ::rankReRank,
    )
    "semi" -> mapOf(
        "scramble" to ::semiScramble,
        "solve" to ::semiSolve,
    )
    "holder" -> mapOf(
        "init" to ::holderInit,
        "scramble" to ::rankScramble,
        "solve" to ::holderSolve,
        "re_holder" to ::holderReHolder,
    )
    "team" -> mapOf(
        "init" to ::teamInit,
        "scramble" to ::rankScramble,
        "solve" to ::teamSolve,
        "re_team" to ::teamReTeam,
    )
    "act" -> mapOf(
        "init" to ::actInit,
        "scramble" to ::rankScramble,
        "solve" to ::actSolve,
        "re_act" to ::actReAct,
    )
    "week" -> mapOf(
        "init" to ::weekInit,
        "scramble" to ::rankScramble,
        "solve" to ::weekSolve,
        "re_week" to ::weekReWeek,
    )
    "remote" -> mapOf(
        "scramble" to ::rankScramble,
        "solve" to ::remoteSolve,
    )
    else -> emptyMap()
}

package com.moyu.device

import com.moyu.common.CubeClient
import com.moyu.common.CubeCommand
import com.moyu.common.CubeDelay
import com.moyu.common.CubeMove
import com.moyu.common.CubeMoveStr
import com.moyu.common.CubeTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import java.util.concurrent.TimeUnit
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class CubeApi(
    private val host: String = "192.168.4.1",
    private val port: Int = 80,
    private val timeoutMs: Long = 7000L,
) : CubeClient {

    private val baseUrl: String get() = "http://$host:$port"

    private val client = OkHttpClient.Builder()
        .connectTimeout(timeoutMs, TimeUnit.MILLISECONDS)
        .readTimeout(timeoutMs, TimeUnit.MILLISECONDS)
        .writeTimeout(timeoutMs, TimeUnit.MILLISECONDS)
        .build()

    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private suspend fun get(path: String): String = withContext(Dispatchers.IO) {
        val request = Request.Builder().url("$baseUrl$path").get().build()
        suspendCancellableCoroutine { cont ->
            client.newCall(request).enqueue(object : okhttp3.Callback {
                override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {
                    if (cont.isActive) cont.resumeWithException(e)
                }

                override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                    response.use { resp ->
                        val body = resp.body?.string() ?: ""
                        if (resp.isSuccessful) cont.resume(body)
                        else cont.resumeWithException(Exception("HTTP ${resp.code}: $body"))
                    }
                }
            })
        }
    }

    private suspend fun post(path: String, jsonBody: String): String = withContext(Dispatchers.IO) {
        val body = jsonBody.toRequestBody(jsonMediaType)
        val request = Request.Builder().url("$baseUrl$path").post(body).build()
        suspendCancellableCoroutine { cont ->
            client.newCall(request).enqueue(object : okhttp3.Callback {
                override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {
                    if (cont.isActive) cont.resumeWithException(e)
                }

                override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                    response.use { resp ->
                        val body = resp.body?.string() ?: ""
                        if (resp.isSuccessful) cont.resume(body)
                        else cont.resumeWithException(Exception("HTTP ${resp.code}: $body"))
                    }
                }
            })
        }
    }

    override suspend fun getFacelets(): String {
        return get("/api/facelets").trim()
    }

    suspend fun clearMoves(): Boolean {
        return try {
            post("/api/moves/clear", "{}").isNotBlank()
        } catch (e: Exception) {
            android.util.Log.w("CubeApi", "clearMoves failed: ${e.message}")
            false
        }
    }

    override suspend fun sendMoves(notation: String): Boolean {
        val moves = parseMoveNotation(notation)
        return sendMovesRaw(moves)
    }

    override suspend fun sendMovesRaw(moves: List<CubeCommand>): Boolean {
        val arr = JSONArray()
        for (m in moves) {
            val obj = org.json.JSONObject()
            when (m) {
                is CubeMove -> {
                    obj.put("face", m.face)
                    obj.put("dir", m.dir)
                }
                is CubeMoveStr -> obj.put("move", m.move)
                is CubeDelay -> obj.put("delay", m.ms)
                is CubeTime -> obj.put("time", m.ms)
            }
            arr.put(obj)
        }
        val body = arr.toString()
        val resp = post("/api/moves", body)
        android.util.Log.d("CubeApi", "sendMovesRaw resp=$resp")
        return resp.isNotBlank()
    }

    override suspend fun setDelay(ms: Int): Boolean {
        return post("/api/delay", "{\"delay\":$ms}").contains("ok", ignoreCase = true)
    }

    override suspend fun getState(): Map<String, Any> {
        val resp = get("/api/state")
        val json = org.json.JSONObject(resp)
        val result = mutableMapOf<String, Any>()
        for (key in json.keys()) {
            result[key] = json.get(key)
        }
        return result
    }

    fun parseMoveNotation(moves: String): List<CubeMove> {
        if (moves.isBlank()) return emptyList()
        val tokens = moves.trim().split("\\s+".toRegex())
        val result = mutableListOf<CubeMove>()
        for (token in tokens) {
            val move = parseOneToken(token) ?: continue
            result.add(move)
        }
        return result
    }

    private fun parseOneToken(token: String): CubeMove? {
        if (token.isEmpty()) return null
        val face = when (token[0]) {
            'U' -> 0; 'R' -> 1; 'F' -> 2
            'D' -> 3; 'L' -> 4; 'B' -> 5
            else -> return null
        }
        val suffix = token.substring(1)
        val dir = when {
            suffix == "'" -> 1
            suffix == "2" || suffix == "2'" -> 2
            else -> 0
        }
        return CubeMove(face, dir)
    }
}

class MockCubeApi : CubeClient {
    var facelets = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    val sentMoves = mutableListOf<CubeMove>()

    override suspend fun getFacelets(): String = facelets

    override suspend fun sendMoves(notation: String): Boolean {
        val tokens = notation.trim().split("\\s+".toRegex())
        for (t in tokens) {
            val face = when (t.firstOrNull()) {
                'U' -> 0; 'R' -> 1; 'F' -> 2
                'D' -> 3; 'L' -> 4; 'B' -> 5
                else -> continue
            }
            val suffix = t.substring(1)
            val dir = when {
                suffix == "'" -> 1
                suffix == "2" || suffix == "2'" -> 2
                else -> 0
            }
            sentMoves.add(CubeMove(face, dir))
        }
        return true
    }

    override suspend fun sendMovesRaw(moves: List<CubeCommand>): Boolean {
        for (m in moves) {
            if (m is CubeMove) sentMoves.add(m)
        }
        return true
    }

    override suspend fun setDelay(ms: Int): Boolean = true

    override suspend fun getState(): Map<String, Any> = mapOf("facelets" to facelets)
}

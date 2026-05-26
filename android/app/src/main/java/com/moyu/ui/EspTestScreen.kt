package com.moyu.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.moyu.common.AppPrefs
import com.moyu.device.CubeApi
import com.moyu.solve.CfopSolver
import kotlinx.coroutines.launch

@Composable
fun EspTestScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var host by remember { mutableStateOf(AppPrefs.espHost(context)) }
    var log by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }

    fun appendLog(msg: String) { log = "$log\n$msg" }

    Column(
        Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        OutlinedTextField(
            value = host,
            onValueChange = { host = it },
            label = { Text("ESP32 IP") },
            singleLine = true,
            modifier = Modifier
                .fillMaxWidth()
                .onFocusChanged { if (!it.isFocused) AppPrefs.saveEspHost(context, host) }
        )
        Spacer(Modifier.height(12.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = {
                    AppPrefs.saveEspHost(context, host)
                    scope.launch {
                        loading = true
                        log = ""
                        try {
                            val api = CubeApi(host = host)
                            appendLog("GET /api/facelets ...")
                            val facelets = api.getFacelets()
                            appendLog("面片 (${facelets.length}): $facelets")
                            if (facelets.length != 54) {
                                appendLog("❌ 面片长度不对，退出")
                                loading = false
                                return@launch
                            }
                            appendLog("CFOP 求解器初始化...")
                            val solver = CfopSolver()
                            CfopSolver.DEBUG = true
                            CfopSolver.logFn = { msg -> appendLog(msg) }
                            solver.init()
                            appendLog("CFOP 求解中...")
                            val result = solver.solve(facelets, null)
                            if (result == null) {
                                appendLog("❌ 求解失败")
                                loading = false
                                return@launch
                            }
                            appendLog("解法: ${result.solution}")
                            appendLog("cross=${result.cross}")
                            appendLog("f2l=${result.f2l}")
                            appendLog("oll=${result.oll}")
                            appendLog("pll=${result.pll}")
                            appendLog("POST /api/moves ...")
                            val ok = api.sendMoves(result.solution)
                            appendLog(if (ok) "✅ 下发成功" else "❌ 下发失败（响应为空）")
                        } catch (e: Exception) {
                            appendLog("❌ 错误: ${e.message}")
                            appendLog(e.stackTraceToString())
                        }
                        loading = false
                    }
                },
                enabled = !loading,
                modifier = Modifier.weight(1f)
            ) { Text("完整流程") }

            Button(
                onClick = {
                    AppPrefs.saveEspHost(context, host)
                    scope.launch {
                        loading = true
                        log = ""
                        try {
                            val api = CubeApi(host = host)
                            appendLog("GET /api/facelets ...")
                            val facelets = api.getFacelets()
                            appendLog("面片 (${facelets.length}): $facelets")
                        } catch (e: Exception) {
                            appendLog("❌ 错误: ${e.message}")
                            appendLog(e.stackTraceToString())
                        }
                        loading = false
                    }
                },
                enabled = !loading,
                modifier = Modifier.weight(1f)
            ) { Text("仅读面片") }
        }

        Spacer(Modifier.height(8.dp))

        if (loading) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                CircularProgressIndicator()
            }
        }

        Spacer(Modifier.height(8.dp))

        SelectionContainer {
            Text(
                text = log.trimStart('\n'),
                fontFamily = FontFamily.Monospace,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
            )
        }
    }
}

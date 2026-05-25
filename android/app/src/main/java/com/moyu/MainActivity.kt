package com.moyu

import android.app.AlertDialog
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.moyu.service.FloatLogService
import com.moyu.service.ScreenCaptureService
import com.moyu.ui.RecipeEditorScreen
import com.moyu.ui.theme.MOYUTheme
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : ComponentActivity() {

    private var ready by mutableStateOf(false)
    private var recipe: String = "rank.json"
    private val overlayLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { startFloatLog() }

    private val mediaProjectionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            FloatLogService.instance?.appendLog("截屏授权成功，启动服务...")
            val intent = Intent(this, ScreenCaptureService::class.java).apply {
                putExtra(ScreenCaptureService.EXTRA_RESULT_CODE, result.resultCode)
                putExtra(ScreenCaptureService.EXTRA_RESULT_DATA, result.data)
                putExtra("recipe", recipe)
            }
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent)
                else startService(intent)
            } catch (e: Exception) {
                FloatLogService.instance?.appendLog("启动截屏失败: ${e.message}")
            }
        } else {
            FloatLogService.instance?.appendLog("截屏授权被拒绝或取消 (code=${result.resultCode})")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MOYUTheme {
                MainScreen(
                    ready = ready,
                    onRecipeSelected = { recipe = it },
                    onStart = { startFloatLog() }
                )
            }
        }
    }

    private fun checkAndStart() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            AlertDialog.Builder(this)
                .setTitle("需要权限")
                .setMessage("需要悬浮窗权限才能显示控制界面")
                .setPositiveButton("去设置") { _, _ ->
                    overlayLauncher.launch(
                        Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
                    )
                }
                .setNegativeButton("取消", null)
                .show()
        } else {
            startFloatLog()
        }
    }

    private fun startFloatLog() {
        ready = true
        val intent = Intent(this, FloatLogService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent)
        else startService(intent)

        val mgr = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        mediaProjectionLauncher.launch(mgr.createScreenCaptureIntent())
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(ready: Boolean, onRecipeSelected: (String) -> Unit, onStart: () -> Unit) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    var currentTab by remember { mutableIntStateOf(0) }

    val context = LocalContext.current
    val recipeFiles = remember {
        val dir = context.filesDir.resolve("recipes")
        dir.mkdirs()
        dir.listFiles()?.filter { it.extension == "json" }?.map { it.name }?.sorted() ?: listOf("rank.json")
    }
    var selectedRecipe by remember { mutableStateOf("rank.json") }
    var recipeExpanded by remember { mutableStateOf(false) }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { innerPadding ->
        Column(Modifier.fillMaxSize().padding(innerPadding)) {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                TextButton(onClick = { currentTab = 0 }) {
                    Text("控制", color = if (currentTab == 0) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface)
                }
                Spacer(Modifier.width(16.dp))
                TextButton(onClick = { currentTab = 1 }) {
                    Text("编辑", color = if (currentTab == 1) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface)
                }
            }

            when (currentTab) {
                0 -> ControlContent(
                    ready = ready,
                    selectedRecipe = selectedRecipe,
                    recipeFiles = recipeFiles,
                    recipeExpanded = recipeExpanded,
                    onRecipeChange = { selectedRecipe = it; recipeExpanded = false; onRecipeSelected(it) },
                    onRecipeExpand = { recipeExpanded = it },
                    onStart = onStart
                )
                1 -> RecipeEditorScreen(onSnackbar = { msg ->
                    scope.launch { snackbarHostState.showSnackbar(msg) }
                })
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ControlContent(
    ready: Boolean,
    selectedRecipe: String,
    recipeFiles: List<String>,
    recipeExpanded: Boolean,
    onRecipeChange: (String) -> Unit,
    onRecipeExpand: (Boolean) -> Unit,
    onStart: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("MOYU", style = MaterialTheme.typography.headlineLarge)
        Spacer(modifier = Modifier.height(16.dp))
        Text(if (ready) "正在运行…" else "魔方自动控制器", style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(24.dp))

        ExposedDropdownMenuBox(
            expanded = recipeExpanded,
            onExpandedChange = onRecipeExpand,
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = selectedRecipe,
                onValueChange = {},
                readOnly = true,
                label = { Text("Recipe") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = recipeExpanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth(),
                singleLine = true,
            )
            ExposedDropdownMenu(expanded = recipeExpanded, onDismissRequest = { onRecipeExpand(false) }) {
                recipeFiles.forEach { name ->
                    DropdownMenuItem(
                        text = { Text(name) },
                        onClick = { onRecipeChange(name) }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onStart, enabled = !ready, modifier = Modifier.fillMaxWidth()) {
            Text(if (ready) "运行中" else "开始授权并启动")
        }
    }
}

package com.moyu.ui

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecipeEditorScreen(onSnackbar: (String) -> Unit = {}) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val recipeDir = remember { context.filesDir.resolve("recipes") }
    val fileNames = remember { mutableStateListOf<String>() }
    var selectedFile by remember { mutableStateOf("") }

    // Refresh file list
    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            recipeDir.mkdirs()
            val names = recipeDir.listFiles()
                ?.filter { it.extension == "json" }
                ?.map { it.name }
                ?.sorted()
                ?: emptyList()
            fileNames.clear()
            fileNames.addAll(names)
        }
    }

    // Form state
    var name by remember { mutableStateOf("") }
    var mode by remember { mutableStateOf("rank") }
    var deviceWidth by remember { mutableStateOf("1080") }
    var deviceHeight by remember { mutableStateOf("2400") }
    var scrambleDelay by remember { mutableStateOf("") }
    var solveDelay by remember { mutableStateOf("") }
    var crossDelay by remember { mutableStateOf("") }
    var f2lDelay by remember { mutableStateOf("") }
    var ollDelay by remember { mutableStateOf("") }
    var pllDelay by remember { mutableStateOf("") }
    var alllDelay by remember { mutableStateOf("") }
    var crossTime by remember { mutableStateOf("") }
    var f2lTime by remember { mutableStateOf("") }
    var ollTime by remember { mutableStateOf("") }
    var pllTime by remember { mutableStateOf("") }
    var alllTime by remember { mutableStateOf("") }
    var alllProb by remember { mutableStateOf("0.1") }
    var rotation by remember { mutableStateOf("") }
    var moveFormat by remember { mutableStateOf("dir") }
    var features = remember { mutableStateListOf<EditableFeature>() }

    fun loadRecipe(fileName: String) {
        if (fileName.isBlank()) return
        scope.launch(Dispatchers.IO) {
            try {
                val root = JSONObject(File(recipeDir, fileName).readText())
                withContext(Dispatchers.Main) {
                    name = root.optString("name", "")
                    mode = root.optString("mode", "rank")
                    val dev = root.optJSONObject("device")
                    deviceWidth = dev?.optInt("width", 1080)?.toString() ?: "1080"
                    deviceHeight = dev?.optInt("height", 2400)?.toString() ?: "2400"
                    scrambleDelay = root.optInt("scramble_delay", -1).let { if (it < 0) "" else it.toString() }
                    solveDelay = root.optInt("solve_delay", -1).let { if (it < 0) "" else it.toString() }
                    crossDelay = root.optInt("cross_delay", -1).let { if (it < 0) "" else it.toString() }
                    f2lDelay = root.optInt("f2l_delay", -1).let { if (it < 0) "" else it.toString() }
                    ollDelay = root.optInt("oll_delay", -1).let { if (it < 0) "" else it.toString() }
                    pllDelay = root.optInt("pll_delay", -1).let { if (it < 0) "" else it.toString() }
                    alllDelay = root.optInt("alll_delay", -1).let { if (it < 0) "" else it.toString() }
                    crossTime = root.optInt("cross_time", -1).let { if (it < 0) "" else it.toString() }
                    f2lTime = root.optInt("f2l_time", -1).let { if (it < 0) "" else it.toString() }
                    ollTime = root.optInt("oll_time", -1).let { if (it < 0) "" else it.toString() }
                    pllTime = root.optInt("pll_time", -1).let { if (it < 0) "" else it.toString() }
                    alllTime = root.optInt("alll_time", -1).let { if (it < 0) "" else it.toString() }
                    alllProb = root.optDouble("alll_prob", 0.1).toString()
                    rotation = root.optString("rotation", "")
                    moveFormat = root.optString("move_format", "dir")
                    features.clear()
                    val ui = root.optJSONObject("ui")
                    if (ui != null) {
                        for (key in ui.keys()) {
                            val feat = ui.getJSONObject(key)
                            features.add(EditableFeature(
                                name = key,
                                templateAsset = feat.optString("template", ""),
                                useRoi = feat.has("roi") && !feat.isNull("roi"),
                                roiX = feat.optJSONObject("roi")?.optInt("x", 0)?.toString() ?: "0",
                                roiY = feat.optJSONObject("roi")?.optInt("y", 0)?.toString() ?: "0",
                                roiW = feat.optJSONObject("roi")?.optInt("w", 0)?.toString() ?: "0",
                                roiH = feat.optJSONObject("roi")?.optInt("h", 0)?.toString() ?: "0",
                                threshold = feat.optDouble("threshold", 0.85).toString(),
                                desc = feat.optString("desc", ""),
                            ))
                        }
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { onSnackbar("加载失败: ${e.message}") }
            }
        }
    }

    fun saveRecipe() {
        if (selectedFile.isBlank() || name.isBlank()) {
            onSnackbar("请填写文件名和名称")
            return
        }
        scope.launch(Dispatchers.IO) {
            try {
                val root = JSONObject()
                root.put("name", name)
                root.put("mode", mode)
                root.put("device", JSONObject().apply {
                    put("width", deviceWidth.toIntOrNull() ?: 1080)
                    put("height", deviceHeight.toIntOrNull() ?: 2400)
                })
                fun putDelay(key: String, v: String) {
                    val i = v.toIntOrNull()
                    if (i != null && i >= 0) root.put(key, i)
                }
                putDelay("scramble_delay", scrambleDelay)
                putDelay("solve_delay", solveDelay)
                putDelay("cross_delay", crossDelay)
                putDelay("f2l_delay", f2lDelay)
                putDelay("oll_delay", ollDelay)
                putDelay("pll_delay", pllDelay)
                putDelay("alll_delay", alllDelay)
                putDelay("cross_time", crossTime)
                putDelay("f2l_time", f2lTime)
                putDelay("oll_time", ollTime)
                putDelay("pll_time", pllTime)
                putDelay("alll_time", alllTime)
                if (rotation.isNotBlank()) root.put("rotation", rotation)
                root.put("move_format", moveFormat)
                alllProb.toDoubleOrNull()?.let { root.put("alll_prob", it) }

                val ui = JSONObject()
                for (f in features) {
                    if (f.name.isBlank()) continue
                    val feat = JSONObject()
                    if (f.templateAsset.isNotBlank()) feat.put("template", f.templateAsset)
                    if (f.useRoi) {
                        feat.put("roi", JSONObject().apply {
                            put("x", f.roiX.toIntOrNull() ?: 0)
                            put("y", f.roiY.toIntOrNull() ?: 0)
                            put("w", f.roiW.toIntOrNull() ?: 0)
                            put("h", f.roiH.toIntOrNull() ?: 0)
                        })
                    }
                    feat.put("threshold", f.threshold.toFloatOrNull() ?: 0.85f)
                    if (f.desc.isNotBlank()) feat.put("desc", f.desc)
                    ui.put(f.name, feat)
                }
                root.put("ui", ui)

                recipeDir.mkdirs()
                File(recipeDir, selectedFile).writeText(root.toString(2))
                withContext(Dispatchers.Main) { onSnackbar("已保存: $selectedFile") }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { onSnackbar("保存失败: ${e.message}") }
            }
        }
    }

    // --- UI ---
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Section A: File Selector
        Text("Recipe File", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        var fileExpanded by remember { mutableStateOf(false) }
        ExposedDropdownMenuBox(
            expanded = fileExpanded,
            onExpandedChange = { fileExpanded = it }
        ) {
            OutlinedTextField(
                value = selectedFile.ifBlank { "选择文件..." }.let { if (it == "选择文件...") it else it.replace(".json", "") } + if (selectedFile.isNotBlank()) ".json" else "",
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = fileExpanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth(),
                singleLine = true,
            )
            ExposedDropdownMenu(expanded = fileExpanded, onDismissRequest = { fileExpanded = false }) {
                fileNames.forEach { fn ->
                    DropdownMenuItem(
                        text = { Text(fn) },
                        onClick = {
                            selectedFile = fn
                            fileExpanded = false
                            loadRecipe(fn)
                        }
                    )
                }
            }
        }
        Spacer(Modifier.height(4.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
                value = selectedFile,
                onValueChange = { s ->
                    selectedFile = s
                    // Clear form for new file
                    if (s !in fileNames) {
                        name = s.removeSuffix(".json")
                    }
                },
                label = { Text("或输入新文件名") },
                singleLine = true,
                modifier = Modifier.weight(1f)
            )
        }
        Spacer(Modifier.height(16.dp))

        // Section B: Basic Settings
        Text("基本设置", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Name") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(8.dp))

        Row(Modifier.fillMaxWidth()) {
            var modeExpanded by remember { mutableStateOf(false) }
            val modes = listOf("rank", "semi", "holder", "team", "act", "week", "remote")
            ExposedDropdownMenuBox(expanded = modeExpanded, onExpandedChange = { modeExpanded = it }, modifier = Modifier.weight(1f)) {
                OutlinedTextField(
                    value = mode, onValueChange = {}, readOnly = true,
                    label = { Text("Mode") }, singleLine = true,
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(modeExpanded) },
                    modifier = Modifier.menuAnchor().fillMaxWidth()
                )
                ExposedDropdownMenu(expanded = modeExpanded, onDismissRequest = { modeExpanded = false }) {
                    modes.forEach { m ->
                        DropdownMenuItem(text = { Text(m) }, onClick = { mode = m; modeExpanded = false })
                    }
                }
            }
            Spacer(Modifier.width(8.dp))
            var fmtExpanded by remember { mutableStateOf(false) }
            val fmts = listOf("dir", "str")
            ExposedDropdownMenuBox(expanded = fmtExpanded, onExpandedChange = { fmtExpanded = it }, modifier = Modifier.weight(1f)) {
                OutlinedTextField(
                    value = moveFormat, onValueChange = {}, readOnly = true,
                    label = { Text("Move Format") }, singleLine = true,
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(fmtExpanded) },
                    modifier = Modifier.menuAnchor().fillMaxWidth()
                )
                ExposedDropdownMenu(expanded = fmtExpanded, onDismissRequest = { fmtExpanded = false }) {
                    fmts.forEach { f ->
                        DropdownMenuItem(text = { Text(f) }, onClick = { moveFormat = f; fmtExpanded = false })
                    }
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        Row(Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value = deviceWidth, onValueChange = { deviceWidth = it },
                label = { Text("Width") }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.weight(1f)
            )
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(
                value = deviceHeight, onValueChange = { deviceHeight = it },
                label = { Text("Height") }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.weight(1f)
            )
        }
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            value = rotation, onValueChange = { rotation = it },
            label = { Text("Rotation") }, singleLine = true, modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("x / x' / z / z' / z2") }
        )
        Spacer(Modifier.height(16.dp))

        // Section C: Delays
        Text("Delay (ms)", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Row(Modifier.fillMaxWidth()) {
            OutlinedTextField(value = scrambleDelay, onValueChange = { scrambleDelay = it }, label = { Text("Scramble") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = solveDelay, onValueChange = { solveDelay = it }, label = { Text("Solve") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
        }
        Spacer(Modifier.height(8.dp))
        Text("Phase Delay (持续)", style = MaterialTheme.typography.labelMedium)
        Spacer(Modifier.height(4.dp))
        Row(Modifier.fillMaxWidth()) {
            OutlinedTextField(value = crossDelay, onValueChange = { crossDelay = it }, label = { Text("Cross") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = f2lDelay, onValueChange = { f2lDelay = it }, label = { Text("F2L") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = ollDelay, onValueChange = { ollDelay = it }, label = { Text("OLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = pllDelay, onValueChange = { pllDelay = it }, label = { Text("PLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = alllDelay, onValueChange = { alllDelay = it }, label = { Text("ALLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
        }
        Spacer(Modifier.height(8.dp))
        Text("Phase Time (一次性)", style = MaterialTheme.typography.labelMedium)
        Spacer(Modifier.height(4.dp))
        Row(Modifier.fillMaxWidth()) {
            OutlinedTextField(value = crossTime, onValueChange = { crossTime = it }, label = { Text("Cross") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = f2lTime, onValueChange = { f2lTime = it }, label = { Text("F2L") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = ollTime, onValueChange = { ollTime = it }, label = { Text("OLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = pllTime, onValueChange = { pllTime = it }, label = { Text("PLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
            Spacer(Modifier.width(8.dp))
            OutlinedTextField(value = alllTime, onValueChange = { alllTime = it }, label = { Text("ALLL") }, singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f))
        }
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            value = alllProb, onValueChange = { alllProb = it },
            label = { Text("ALLL Prob (0~1)") }, singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(16.dp))

        // Section D: UI Features
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("UI Features", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
            OutlinedButton(onClick = {
                features.add(EditableFeature(expanded = true))
            }) { Text("+ Add") }
        }
        Spacer(Modifier.height(8.dp))

        features.forEachIndexed { idx, feat ->
            FeatureCard(
                feature = feat,
                onUpdate = { features[idx] = it },
                onDelete = { features.removeAt(idx) },
                context = context,
            )
            Spacer(Modifier.height(8.dp))
        }
        Spacer(Modifier.height(16.dp))

        // Section E: Save
        Button(
            onClick = { saveRecipe() },
            modifier = Modifier.fillMaxWidth().height(52.dp),
            enabled = selectedFile.isNotBlank() && name.isNotBlank()
        ) {
            Text("Save Recipe", style = MaterialTheme.typography.titleSmall)
        }
        Spacer(Modifier.height(32.dp))
    }
}

data class EditableFeature(
    var name: String = "",
    var templateAsset: String = "",
    var useRoi: Boolean = false,
    var roiX: String = "0",
    var roiY: String = "0",
    var roiW: String = "0",
    var roiH: String = "0",
    var threshold: String = "0.85",
    var desc: String = "",
    var expanded: Boolean = false,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FeatureCard(
    feature: EditableFeature,
    onUpdate: (EditableFeature) -> Unit,
    onDelete: () -> Unit,
    context: Context,
) {
    var expanded by remember { mutableStateOf(feature.expanded) }

    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            Modifier.fillMaxWidth().clickable { expanded = !expanded }.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = onDelete) {
                Text("✕", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.titleMedium)
            }
            Text(
                text = feature.name.ifBlank { "new feature" },
                style = MaterialTheme.typography.titleSmall,
                modifier = Modifier.weight(1f)
            )
            Text(if (expanded) "▲" else "▼")
        }

        if (expanded) {
            Column(Modifier.padding(horizontal = 12.dp, vertical = 8.dp)) {
                OutlinedTextField(
                    value = feature.name, onValueChange = { onUpdate(feature.copy(name = it)) },
                    label = { Text("Feature Name") }, singleLine = true, modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = feature.templateAsset, onValueChange = { onUpdate(feature.copy(templateAsset = it)) },
                    label = { Text("Template Asset Path") }, singleLine = true, modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("templates/btn.png") }
                )
                Spacer(Modifier.height(4.dp))
                Card(Modifier.fillMaxWidth().height(100.dp)) {
                    TemplatePreview(context, feature.templateAsset)
                }
                Spacer(Modifier.height(8.dp))

                var useRoi by remember { mutableStateOf(feature.useRoi) }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(checked = useRoi, onCheckedChange = {
                        useRoi = it
                        onUpdate(feature.copy(useRoi = it))
                    })
                    Text("Use ROI")
                }
                if (useRoi) {
                    Row(Modifier.fillMaxWidth()) {
                        OutlinedTextField(
                            value = feature.roiX, onValueChange = { onUpdate(feature.copy(roiX = it)) },
                            label = { Text("X") }, singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f)
                        )
                        Spacer(Modifier.width(4.dp))
                        OutlinedTextField(
                            value = feature.roiY, onValueChange = { onUpdate(feature.copy(roiY = it)) },
                            label = { Text("Y") }, singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f)
                        )
                        Spacer(Modifier.width(4.dp))
                        OutlinedTextField(
                            value = feature.roiW, onValueChange = { onUpdate(feature.copy(roiW = it)) },
                            label = { Text("W") }, singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f)
                        )
                        Spacer(Modifier.width(4.dp))
                        OutlinedTextField(
                            value = feature.roiH, onValueChange = { onUpdate(feature.copy(roiH = it)) },
                            label = { Text("H") }, singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.weight(1f)
                        )
                    }
                }
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = feature.threshold, onValueChange = { onUpdate(feature.copy(threshold = it)) },
                    label = { Text("Threshold") }, singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal), modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = feature.desc, onValueChange = { onUpdate(feature.copy(desc = it)) },
                    label = { Text("Description") }, singleLine = true, modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun TemplatePreview(context: Context, assetPath: String) {
    var errorMsg by remember { mutableStateOf<String?>(null) }
    val bitmap = remember(assetPath) {
        errorMsg = null
        if (assetPath.isBlank()) null
        else try {
            val bmp = context.assets.open(assetPath).use { BitmapFactory.decodeStream(it) }
            if (bmp == null) errorMsg = "decodeStream returned null"
            bmp
        } catch (e: Exception) {
            errorMsg = e.message
            null
        }
    }
    if (bitmap != null) {
        Card(Modifier.fillMaxWidth().height(120.dp)) {
            Image(
                bitmap = bitmap.asImageBitmap(),
                contentDescription = "Template",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Fit
            )
        }
    } else {
        Text(
            if (assetPath.isNotBlank()) "预览失败: ${errorMsg ?: assetPath}" else "未指定模板",
            color = MaterialTheme.colorScheme.error,
            style = MaterialTheme.typography.bodySmall
        )
    }
}

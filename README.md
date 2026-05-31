# **MOYU** = **M**ore **O**nline **Y**our smart-c**U**be

MOYU 是基于硬件模拟智能魔方，意图实现人类摸鱼（MOYU），机器自动上分的项目。

## 架构

需要：ESP32-C3 + 安卓手机 + 电脑（Python 版）或仅 ESP32-C3 + 安卓手机（Android 版）

- ESP32-C3 运行 [gan-cube-emu](../gan-cube-emu)，BLE 模拟 GAN 智能魔方
- 安卓手机运行 Cube Station，通过 BLE 与 ESP32 连接
- **Python 版**：电脑作为主控制器，通过 scrcpy 控制手机，通过 WiFi HTTP 控制 ESP32
- **Android 版**：控制器直接运行在手机上（APK），无需 PC，通过 WiFi HTTP 控制 ESP32

---

## 功能特性对比

| 特性 | Python 版 | Android Kotlin 版 |
|------|-----------|-------------------|
| **运行模式** | rank / semi / holder / team / week / remote | rank / semi / holder / team / week / remote |
| **屏幕捕获** | scrcpy 客户端（USB/WiFi） | MediaProjection API（系统授权） |
| **UI 点击** | scrcpy.tap() 注入 | MoyuAccessibilityService（无障碍服务） |
| **分类器后端** | knn / template / cnn(ONNX) / hog_svm | 仅 cnn（TFLite） |
| **OCR 气泡分割** | OpenCV HoughCircles | OpenCV HoughCircles（JNI） |
| **CFOP 求解** | Cross + F2L + OLL + PLL + ALLL | Cross + F2L + OLL + PLL + ALLL |
| **ALLL 概率控制** | `ALLL_PROB` 常量（默认 0.1） | recipe `alll_prob` 字段（默认 0.1） |
| **ALLL 表缓存** | pickle（`.cfop_cache.pkl`） | ObjectOutputStream（`alll_rec_v2.cache`） |
| **Recipe 延迟** | `cross/f2l/oll/pll/alll_delay` + `cross/f2l/oll/pll/alll_time` | `cross/f2l/oll_delay`（持续延迟，无 time 类型） |
| **调试工具** | Telnet REPL（动态执行 Python 代码） | 悬浮窗（截图缩略图 + 日志 + 控制按钮） |
| **训练数据采集** | `ocr.trainer collect`（自动保存截图） | 无 |
| **Recipe 编辑** | 手动编辑 JSON | 内置 Compose UI 可视化编辑 |
| **ESP 测试界面** | Telnet / 命令行 | 内置测试 Tab（读面片/求解/ALLL 重建） |
| **部署形态** | 需 PC + Python 环境 | 自包含 APK，无 PC 依赖 |

---

## 状态机流程

状态机按 `mode` 分别定义，通过 handler 表路由。各模式共用同一 `scramble` 实现。

| mode | 流程 |
|------|------|
| **semi** | `scramble` ↔ `solve` |
| **rank** | `init` → `scramble` → `solve` → `re_rank` → `scramble` |
| **holder** | `init` → `scramble` → `solve` → `re_holder` → `init` |
| **team** | `init` → `scramble` → `solve` → `re_team` → `scramble` |
| **week** | `init` → `scramble` → `solve` → `re_week` → `init` |
| **remote** | `scramble` → `solve`（循环等待下一把打乱） |

---

## Python 版

### 并发架构

```
controller.py → asyncio.run(main())
            └─ Controller.run()
                ├─ create_task(_state_machine)    # 状态机驱动
                ├─ create_task(ScreenLoop.run)     # 截图 + UI 检测
                ├─ create_task(CubeLoop.run)       # 魔方状态轮询 + 转动下发
                └─ create_task(_start_telnet)      # Telnet REPL 服务器（可选）
```

### 模块结构

```
moyu/
├── recipe/
│   ├── schema.py              # Recipe JSON schema 定义与校验
│   ├── loader.py              # 加载/热重载 recipe 文件
│   └── recipes/               # 各设备 recipe JSON + 模板图
├── vision/
│   ├── screen_loop.py         # FrameSource 抽象 + ScreenLoop
│   ├── matcher.py             # 模板匹配核心
│   └── detector.py            # UI 检测逻辑
├── ocr/
│   ├── segmentor.py           # HoughCircles 气泡分割
│   ├── classifier.py          # 字符分类器（KNN/模板/CNN/HOG-SVM）
│   ├── trainer.py             # 训练数据采集与模型训练
│   └── parser.py              # 识别结果 → move 序列
├── device/
│   ├── scrcpy_client.py       # scrcpy 封装
│   ├── cube_api.py            # HTTP → ESP32
│   ├── cube_loop.py           # 轮询 + 转动下发循环
│   └── telnet.py              # Telnet REPL 服务器
└── controller.py              # 入口 + 主控制器
```

### Recipe 配置

```json
{
    "name": "pixel_7_pro",
    "device": { "width": 1080, "height": 2400 },
    "mode": "rank",
    "scramble_delay": 90,
    "solve_delay": 90,
    "cross_delay": 0,
    "f2l_delay": 150,
    "oll_delay": 90,
    "pll_time": 200,
    "alll_prob": 1.0,
    "rotation": "x",
    "move_format": "dir",
    "classifier": {
        "type": "cnn",
        "model_path": "ocr/cnn_model.onnx"
    },
    "ui": {
        "begin_rank": {
            "template": "templates/begin_rank.png",
            "roi": { "x": 0, "y": 0, "w": 1080, "h": 200 },
            "threshold": 0.85
        }
    }
}
```

| 字段 | 说明 |
|------|------|
| `scramble_delay` / `solve_delay` | 进入对应阶段时设置 ESP32 转动延迟（ms） |
| `cross/f2l/oll/pll/alll_delay` | 阶段前插入 `{"delay": ms}`（修改后续持续延迟） |
| `cross/f2l/oll/pll/alll_time` | 阶段前插入 `{"time": ms}`（一次性等待） |
| `alll_prob` | ALLL 尝试概率 0.0~1.0，默认 0.1 |
| `rotation` | 面片坐标变换（x/x'/z/z'/z2） |
| `move_format` | `"dir"` = face+dir 数字，`"str"` = 符号字符串 |
| `classifier` | 分类器配置（type + model_path） |

### 分类器后端

| 后端 | 配置 | 特点 |
|------|------|------|
| KNN | `{"type": "knn", "model_path": "ocr/knn_model.pkl"}` | 简单快速，小样本可用 |
| 模板匹配 | `{"type": "template", "templates_dir": "ocr/templates/"}` | 无需训练 |
| CNN | `{"type": "cnn", "model_path": "ocr/cnn_model.onnx"}` | ONNX 推理，精度最高 |
| HOG-SVM | `{"type": "hog_svm", "model_path": "ocr/hog_svm_model.pkl"}` | 传统特征，鲁棒性好 |

### 启动

```bash
python controller.py                              # 默认 example.json
python controller.py --recipe rank.json           # 指定 recipe
python controller.py --classifier cnn             # 指定分类器
python controller.py --state scramble             # 指定初始状态
python controller.py --telnet 5555                # 启动 Telnet REPL（默认开启）
python controller.py --single-step                # 逐步下发（调试）
```

### Telnet REPL

```bash
telnet localhost 5555
```

连接后可访问：`controller`, `recipe`, `cube`, `scrcpy`, `detector`, `logger`

支持 Tab 补全、上下键历史、左右移动光标、Ctrl+W/Z/A 等快捷键。

### 各模块单独测试

```bash
# 模板匹配
python -m vision.matcher screen.png tmpl.png
python -m vision.detector screen.png recipe/recipes/example.json begin_rank

# OCR
python -m ocr.segmentor scramble_screen.png
python -m ocr.classifier char.png --backend cnn --model ocr/cnn_model.onnx

# 训练
python -m ocr.trainer collect --source video --input tests/scramble.mp4 --output data/
python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx

# 设备
python -m device.cube_api 192.168.4.1
```

---

## Android Kotlin 版

### 架构

```
ControllerService（前台服务）
├─ ScreenCaptureService        # MediaProjection 截屏
├─ MoyuAccessibilityService    # 无障碍服务（手势注入）
├─ FloatLogService             # 悬浮窗（日志 + 控制 + 截图缩略图）
└─ Controller（协程）
    ├─ stateMachine()          # 状态机
    ├─ CubeApi（OkHttp）        # ESP32 HTTP 通信
    ├─ Detector（OpenCV）       # UI 模板匹配
    └─ MoveClassifier（TFLite）# CNN 字符识别
```

### 模块结构

```
android/app/src/main/java/com/moyu/
├── controller/
│   ├── Controller.kt          # 主控制器 + 状态机
│   ├── HandlerRouter.kt       # 模式 → handler 表路由
│   ├── RankHandlers.kt        # rank/team/week/holder/semi/remote 各状态 handler
│   └── RankSolveHandlers.kt   # 求解阶段公共逻辑
├── device/
│   ├── CubeApi.kt             # HTTP → ESP32（OkHttp）
│   └── MockCubeApi.kt         # 离线测试 Mock
├── ocr/
│   ├── BubbleSegmentor.kt     # OpenCV HoughCircles 气泡分割
│   ├── MoveClassifier.kt      # TFLite CNN 分类器
│   └── MoveParser.kt          # 识别结果 → move 序列
├── recipe/
│   ├── RecipeConfig.kt        # Recipe 数据类定义
│   └── RecipeLoader.kt        # 加载 assets/recipes/
├── service/
│   ├── ScreenCaptureService.kt # MediaProjection 截屏服务
│   ├── FloatLogService.kt      # 悬浮窗服务
│   └── MoyuAccessibilityService.kt # 无障碍手势服务
├── solve/
│   ├── CfopSolver.kt          # CFOP 求解器主入口
│   ├── CrossSolver.kt         # 底十字 BFS
│   ├── F2lSolver.kt           # F2L 搜索
│   ├── LLSolver.kt            # OLL / PLL / ALLL 识别与求解
│   ├── ExAllls.kt             # 6000+ ALLL 算法集合
│   ├── CubieCube.kt           # 魔方置换群表示
│   ├── AlgParser.kt           # 算法符号解析与转换
│   └── CfopTables.kt          # 剪枝表与坐标函数
├── ui/
│   ├── MainActivity.kt        # 主界面（Compose）
│   ├── RecipeEditorScreen.kt  # Recipe 可视化编辑
│   └── EspTestScreen.kt       # ESP32 测试界面
└── vision/
    └── Detector.kt            # OpenCV 模板匹配（TM_CCOEFF_NORMED）
```

### Recipe 配置

```json
{
    "name": "xiaomi_13_rank",
    "device": { "width": 1080, "height": 2400 },
    "mode": "rank",
    "scramble_delay": 90,
    "solve_delay": 90,
    "cross_delay": 0,
    "f2l_delay": 0,
    "oll_delay": 0,
    "alll_prob": 1.0,
    "rotation": "x",
    "move_format": "dir",
    "initial_state": null,
    "ui": {
        "begin_rank": {
            "template": "templates/begin_rank.png",
            "roi": { "x": 0, "y": 0, "w": 1080, "h": 200 },
            "threshold": 0.85,
            "desc": "排位赛开始按钮"
        }
    }
}
```

| 字段 | 说明 |
|------|------|
| `scramble_delay` / `solve_delay` | 进入对应阶段时设置 ESP32 转动延迟（ms） |
| `cross/f2l/oll_delay` | 阶段前插入 `{"delay": ms}`（修改后续持续延迟） |
| `alll_prob` | ALLL 尝试概率 0.0~1.0，默认 0.1 |
| `rotation` | 面片坐标变换（x/x'/z/z'/z2） |
| `move_format` | `"dir"` = face+dir 数字，`"str"` = 符号字符串 |
| `initial_state` | 覆盖默认初始状态 |

### 悬浮窗功能

- **暂停/继续**：挂起状态机（协程仍运行）
- **停止**：终止状态机
- **重启**：切换目标状态（init/scramble/solve）后重启
- **状态显示**：实时显示 `▶ scramble` 或 `⏸ solve`（每 500ms 刷新）
- **截图缩略图**：实时预览当前屏幕（每 500ms 更新）
- **日志区**：最新一条（青色）+ 可展开滚动日志（保留 200 行）
- **拖动/折叠**：拖动控制栏移动窗口，轻点切换展开/折叠

---

## ESP32 HTTP API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/facelets` | 读取 54 个面片字符串（kociemba 格式） |
| POST | `/api/moves` | 下发转动序列（JSON Array） |
| POST | `/api/moves/clear` | 清空待执行队列 |
| POST | `/api/delay` | 设置电机延迟（ms） |
| GET | `/api/state` | 读取魔方全部状态信息 |

### 指令格式

| 类型 | JSON | 说明 |
|------|------|------|
| 转动（dir 模式） | `{"face": 1, "dir": 0}` | face 0~5 = U/R/F/D/L/B，dir 0/1/2 = CW/CCW/180° |
| 转动（str 模式） | `{"move": "R'"}` | 直接传符号字符串 |
| 持续延迟 | `{"delay": 100}` | 修改后续所有转动间隔 |
| 一次性延迟 | `{"time": 100}` | 仅等待一次，不影响后续延迟（Python 版支持） |

---

## CFOP 求解器

两个版本的求解器逻辑完全一致：

```
输入: facelet 字符串（54 字符）
  ↓
Cross（底十字，BFS + 剪枝表）
  ↓
F2L（四对，IDA* + 宏对优化）
  ↓
ALLL（概率性一步 LL，查 ~97k 条目哈希表）
  ↓（未命中则走 OLL + PLL）
OLL（57 种算法）→ PLL（21 种算法）
  ↓
输出: SolveResult { cross, f2l, oll?, pll?, alll?, solution }
```

ALLL 表由 OLL(57) + PLL(21) + EX_ALLLS(~6000) 算法 × 4 AUF × 4 post-AUF 展开构建，首次构建后序列化缓存，后续启动直接加载。

---

## OCR 字符集

分类器支持 25 个类别：

```
R  R' R2 R2'    U  U' U2 U2'    F  F' F2 F2'
D  D' D2 D2'    B  B' B2 B2'    L  L' L2 L2'
EMPTY
```

气泡定位流程：
1. OpenCV HoughCircles 检测圆形气泡轮廓
2. 裁剪每个气泡区域，resize 到 64×64
3. 送入分类器识别，过滤 EMPTY，拼接为 move 序列

---

## 依赖

### Python 版

- [py-scrcpy-client](https://github.com/leng-yue/py-scrcpy-client)
- [aiohttp](https://pypi.org/project/aiohttp/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [numpy](https://pypi.org/project/numpy/)
- [onnxruntime](https://pypi.org/project/onnxruntime/)（CNN 推理）
- [torch](https://pytorch.org/)（CNN 训练，可选）

### Android 版

- OpenCV 4.4.0（AAR，JNI）
- TensorFlow Lite（CNN 推理）
- OkHttp（ESP32 HTTP 通信）
- Jetpack Compose（UI）

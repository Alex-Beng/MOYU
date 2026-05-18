# **MOYU** = **M**ore **O**nline **Y**our  smart-c**U**be

MOYU 是基于硬件模拟智能魔方，意图实现人类摸鱼（MOYU），机器自动上分的项目。

## 架构

需要：ESP32-C3 + 安卓手机 + 电脑

- ESP32-C3 运行 [gan-cube-emu](../gan-cube-emu)，BLE 模拟 GAN 智能魔方
- 安卓手机运行 Cube Station，通过 BLE 与 ESP32 连接
- 电脑作为主控制器与求解器，通过 scrcpy 控制手机，通过 WiFi HTTP 控制 ESP32

### 并发架构

基于 `asyncio.create_task` + `asyncio.gather`，各功能模块以独立 Task 运行：

```
controller.py → asyncio.run(main())
            └─ Controller.run()
                ├─ create_task(_state_machine)    # 状态机驱动
                ├─ create_task(ScreenLoop.run)     # 截图 + UI 检测
                └─ create_task(CubeLoop.run)       # 魔方状态轮询 + 转动下发
                └─ asyncio.gather(*tasks)          # 等待所有任务
```

任务间通过 `asyncio.Queue` 通信，避免共享状态竞争。

### 状态机流程

状态机按 `mode` 分别定义，通过 `_get_handlers(mode)` 路由到对应的 handler 表。

**semi 模式**（人类操作 UI，AI 只负责 OCR + solve）

```
scramble ──(识别完成)──▶ solve ──(下发完成)──▶ scramble
```

| state | description |
|----------|-------------|
| scramble | OCR 识别打乱序列气泡，下发转动；无气泡且已下发过则进入 solve |
| solve | 获取面片 → CFOP 求解 → 下发转动，完成后回到 scramble |

**rank 模式**（全自动排位赛）

```
init ──(点击begin_rank)──▶ scramble ──(气泡消失)──▶ solve
 ▲                                                      │
 │                   re_rank ◀──(检测到end_rank)────────┘
 └──────────────(点击re_rank)──────────────────────────┘
```

| state | description |
|----------|-------------|
| init | 等待并点击 begin_rank 按钮，进入排位 |
| scramble | OCR 识别打乱气泡并下发；无气泡且已下发过则进入 solve |
| solve | 求解并下发转动；同时检测 end_rank 或新一轮 scramble |
| re_rank | 等待并点击 re_rank 按钮，回到 scramble |

**新增 mode**：在 `controller.py` 末尾添加对应的 `async def _<mode>_<state>` handler 函数，并在 `_get_handlers()` 中注册 `{state: handler}` 字典。同时在 `_init_state()` 中为新 mode 设置默认初始状态。Controller 主体无需改动。

流程控制全部在 Controller 代码中，Recipe 只负责 UI 特征描述。

## 模块拆分

```
moyu/
├── recipe/
│   ├── schema.py              # Recipe JSON schema 定义与校验
│   ├── loader.py              # 加载/热重载 recipe 文件
│   └── recipes/
│       └── example.json       # 设备配置示例
│       └── templates/         # UI 特征模板图（配合 recipe 引用）
├── vision/
│   ├── screen_loop.py         # FrameSource 抽象 + ScreenLoop（截图→检测→推送事件）
│   ├── matcher.py             # 模板匹配核心（基于 recipe 配置）
│   └── detector.py            # 各状态 UI 检测逻辑
├── ocr/
│   ├── segmentor.py           # 圆形轮廓检测 + 字符分割（固定流程）
│   ├── classifier.py          # 字符分类器（KNN / 模板匹配 / CNN，可配置）
│   ├── trainer.py             # 训练数据收集 & 模型训练/导出入口
│   └── parser.py              # 识别结果 → 标准 move 序列
│   ├── knn_model.pkl          # KNN 模型（训练后生成）
│   ├── templates/             # 模板匹配分类器的模板图（训练后导出）
│   └── cnn_model.onnx         # CNN ONNX 模型（训练后生成）
├── device/
│   ├── scrcpy_client.py       # python-scrcpy-client 封装（截图/点击/滑动）
│   ├── cube_api.py            # HTTP → ESP32 转动下发（对接 gan-cube-emu API）
│   └─ cube_loop.py            # 轮询状态 + 消费转动指令循环
└── controller.py              # 入口 + 主控制器（编排任务 + 状态机）
```

## Recipe 配置

Recipe 是纯配置，只描述 UI 特征（模板图、检测区域、阈值），不含任何流程逻辑。

```json
{
    "name": "pixel_7_pro",
    "device": { "width": 1080, "height": 2400 },
    "ui": {
        "match_button": {
            "template": "templates/match_btn.png",
            "roi": [400, 1800, 280, 80],
            "threshold": 0.85
        },
        "scramble_area": {
            "template": "templates/scramble_area.png",
            "roi": [50, 400, 980, 300],
            "threshold": 0.80
        }
    }
}
```

- `ui` 的 key 是特征名称（如 `"match_button"`），由 Controller 代码引用
- Controller 决定在哪个状态检测哪些特征、检测到后做什么动作、转移到哪
- `template` 为相对于 recipe 文件的模板图路径
- `roi` 为检测区域 `[x, y, w, h]`，`null` 表示全图搜索
- 换设备只需换 recipe（模板图 + 坐标），流程代码不变

## ESP32 HTTP API (gan-cube-emu)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web 控制界面 |
| POST | `/api/move` | 单步转动 `{"face":0-5,"dir":0-1}` |
| POST | `/api/moves` | 批量转动 `[{"face":0,"dir":0},...]` |
| GET | `/api/state` | 获取当前魔方状态 JSON |
| GET | `/api/facelets` | 获取 kociemba 格式面片字符串 `UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB` |

Face 映射 (GAN 协议)：`0=U, 1=R, 2=F, 3=D, 4=L, 5=B`

Dir 映射：`0=CW(顺时针90°), 1=CCW(逆时针90°)`

标准记号转换：

| 记号 | face/dir |
|------|----------|
| `R`  | `{face:1, dir:0}` |
| `R'` | `{face:1, dir:1}` |
| `R2` | 两步 `{face:1, dir:0}` |

## OCR 字符集

分类器支持 24 个类别（6面 × 4修饰）：

```
R  R' R2 R2'    U  U' U2 U2'    F  F' F2 F2'
D  D' D2 D2'    B  B' B2 B2'    L  L' L2 L2'
```

字符定位流程（固定，不依赖 recipe）：
1. HoughCircles 检测圆形气泡轮廓
2. 裁剪每个气泡区域，resize 到 64×64
3. 送入分类器识别

分类器后端可配置选择：

| 后端 | 配置 | 特点 |
|------|------|------|
| KNN | `{"type": "knn", "model_path": "ocr/knn_model.pkl"}` | 简单快速，小样本可用 |
| 模板匹配 | `{"type": "template", "templates_dir": "ocr/templates/"}` | 无需训练，每类一张模板图 |
| CNN | `{"type": "cnn", "model_path": "ocr/cnn_model.onnx"}` | ONNX 推理，精度最高 |

## 各模块单独测试

每个模块都有 `if __name__ == "__main__":` 入口，可独立运行调试：

### Vision — 模板匹配

```bash
# matcher: 在图片中查找特征图，可视化匹配结果
python -m vision.matcher screen.png tmpl.png
python -m vision.matcher screen.png tmpl.png 100 200 400 80   # 带 ROI

# detector: 基于 recipe 检测某特征
python -m vision.detector screen.png recipe/recipes/example.json match_button

# screen_loop: 帧流测试（纯黑帧/图片/视频）
python -m vision.screen_loop                     # 纯黑静态帧
python -m vision.screen_loop screen.png          # 图片 mock
python -m vision.screen_loop test_run.mp4        # 视频 mock
```

### OCR — 字符识别

```bash
# segmentor: 检测圆形气泡轮廓，可视化标注 + 逐个查看裁剪
python -m ocr.segmentor scramble_screen.png

# classifier: 对单张 64×64 字符图预测类别
python -m ocr.classifier char.png --backend knn --model ocr/knn_model.pkl
python -m ocr.classifier char.png --backend template --model ocr/templates/
python -m ocr.classifier char.png --backend cnn --model ocr/cnn_model.onnx

# parser: 测试记号转换
python -m ocr.parser R U "R'" "U'"
python -m ocr.parser "RUR'U'"
```

### OCR — 训练

```bash
# 采集样本（从视频交互标注）
python -m ocr.trainer collect --source video --input tests/scramble.mp4 --output data/

# 采集样本（从图片目录）
python -m ocr.trainer collect --source images --input tests/frames/ --output data/

# 训练 KNN
python -m ocr.trainer train --backend knn --data data/ --output ocr/knn_model.pkl

# 导出模板图（用于模板匹配分类器）
python -m ocr.trainer train --backend template --data data/ --output ocr/templates/

# 训练 CNN → ONNX
python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx
```

### Device — 设备控制

```bash
# cube_api: 测试 ESP32 HTTP 接口
python -m device.cube_api              # Mock 测试（无需真实 ESP32）
python -m device.cube_api 192.168.4.1  # 真实设备

# cube_loop: 测试轮询 + 转动下发循环（需先写代码实例化）
#   api = MockCubeAPI()
#   await api.open()
#   asyncio.run(CubeLoop(api, asyncio.Queue(), asyncio.Queue()).run())
```

### Recipe — 配置加载

```bash
# 直接在 Python 中测试
python -c "from recipe.loader import RecipeLoader; r = RecipeLoader(); print(r.recipe.name); print(r.recipe.feature('match_button'))"
```

## 依赖

- [gan-cube-emu](../gan-cube-emu) — ESP32-C3 BLE 魔方模拟器固件
- [py-scrcpy-client](https://github.com/leng-yue/py-scrcpy-client) — 安卓手机 scrcpy 控制
- [aiohttp](https://pypi.org/project/aiohttp/) — 异步 HTTP 客户端（ESP32 通信）
- [opencv-python](https://pypi.org/project/opencv-python/) — 图像处理 / 模板匹配 / 轮廓检测
- [numpy](https://pypi.org/project/numpy/) — 数值计算
- [adbutils](https://github.com/openatx/adbutils) — ADB 连接管理（scrcpy 依赖）

可选依赖（按分类器后端）：
- [onnxruntime](https://pypi.org/project/onnxruntime/) — CNN 推理（如使用 CNN 后端）
- [torch](https://pytorch.org/) — CNN 训练导出 ONNX

## 启动

```bash
python controller.py                        # 按 recipe mode 运行
python controller.py --state scramble       # 指定初始状态（跳过默认起点）
python controller.py --classifier cnn --single-step
```

状态机默认初始状态由 mode 决定（semi → scramble，rank → init），需确保 ESP32 已启动且手机已通过 ADB 连接。
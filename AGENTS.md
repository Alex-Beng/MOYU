# MOYU — 智能魔方自动化

## 项目概要
视觉识别 + CFOP 求解器 + ESP32 模拟 GAN 智能魔方。双版本：**Python 版**（PC 驱动）和 **Android Kotlin 版**（自包含 APK）。

## Python 版

### 入口与执行
- 入口：`python controller.py`（顶层模块，非包结构）
- **无 requirements.txt** —— 依赖见 README：py-scrcpy-client, aiohttp, opencv-python, numpy, onnxruntime, torch（训练时可选）
- Python 模块为**顶层目录**：`crypto/` `device/` `ocr/` `solve/` `vision/` `recipe/` `tools/` `web/`
- 虚拟环境：`.venv/`（Python 3.10.6）

### 开发命令
```bash
python controller.py --recipe rank.json --classifier cnn --host 192.168.50.246
python controller.py --mock --recipe rank.json                          # 离线 Mock 模式
python controller.py --single-step                                      # 逐步下发（调试用）
python controller.py --state scramble                                   # 覆盖初始状态
python controller.py --telnet 0                                         # 禁用 telnet REPL
python controller.py --telnet 5556                                      # 启用 telnet（端口 5556）
python controller.py --web-port 8080                                    # Web 终端（默认 8080，0=关闭）
python controller.py --recipe solo.json                                 # Solo 模式
python controller.py --recipe rank.json --proxy                         # BLE 代理模式：监听真实魔方 + 记录 CSV + 转发到 ESP32
python controller.py --recipe proxy.json --proxy                        # 纯代理模式（无 scrcpy 依赖）
python -m solve.solve 192.168.4.1 --method pocket_o --send              # CLI 求解器
python -m solve.solve 192.168.4.1 --method cfop --send --rotation x     # CFOP + 预旋转
python -m vision.matcher screen.png tmpl.png                            # 模板匹配测试
python -m vision.detector screen.png recipe/recipes/example.json begin_rank
python -m ocr.segmentor scramble_screen.png                             # OCR 气泡分割测试
python -m ocr.classifier char.png --backend cnn --model ocr/cnn_model.onnx
python -m device.cube_api 192.168.4.1                                   # 魔方 API 测试
python -m tools.ble_monitor                                            # BLE 魔方监听器（自动扫描）
python -m tools.ble_monitor --address AA:BB:CC:DD:EE:FF                # 指定地址连接
python -m tools.ble_monitor --no-csv                                   # 仅输出，不记录 CSV
python -m tools.ble_monitor --verbose                                  # 显示面片更新
python -m tools.gan_proxy                                              # 独立代理收集（BLE → CSV）
python -m tools.gan_proxy --host 192.168.50.246                        # 收集 + 批量转发到 ESP32
python -m tools.gan_proxy --address AA:BB:CC:DD:EE:FF --no-csv         # 指定地址纯输出
```

### OCR 训练流程
```bash
python -m tools.collect_training_data ocr --model ocr/cnn_model.onnx --host 192.168.50.246  # 采集+自动标注+下发转动
python -m tools.collect_training_data ocr --output data/                                     # 纯手动采集
python -m tools.collect_training_data ui --output recipe/recipes/templates/                  # UI 模板采集
python -m ocr.trainer collect --source video --input tests/scramble.mp4 --output data/
python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx
python test_pocket.py                                                                        # 二阶求解器测试
python test_pocket_advanced.py                                                               # 二阶进阶测试
```

### 配置文件
- Recipe 配置：`recipe/recipes/*.json` —— 控制模式（rank/semi/holder/team/week/remote/solo/proxy）、延迟、UI 模板、分类器
- 默认 Recipe：`recipe/recipes/example.json`
- 分类器后端：`knn`（`.pkl`）、`template`（目录）、`cnn`（`.onnx`）、`hog_svm`（`.pkl`）

### 求解器
- CFOP（三阶）：BFS 十字 + IDA\* F2L + OLL/PLL + 概率性 ALLL（`alll_prob` 在 recipe 中配置）
- 二阶：`pocket_o`（Ortega）或 `pocket_eg`（EG），仅 RUF 转动，输入 54 字符面片字符串
- ALLL 表首次构建后缓存为 `.cfop_cache.pkl`

### Git 忽略路径（仓库中不存在）
`data/`, `templates/`, `debug/`, `log/`, `*.{pkl,onnx,pt,tflite}`, `*.png`, `*.jpg`, `.cfop_cache.pkl`, `floatlog.txt`, `error.log`

### Telnet REPL
```bash
telnet localhost 5556
# 暴露对象：controller, recipe, cube, scrcpy, detector, logger（支持 Tab 补全）
```

### 并发架构
```
controller.py → asyncio.run(main())
  ├─ _state_machine   （状态机驱动）
  ├─ ScreenLoop.run   （截图 + UI 检测）
  ├─ CubeLoop.run     （魔方轮询 + 转动下发）
  ├─ ProxyLoop.run    （BLE 代理：监听真实魔方 + CSV 记录 + 转发，--proxy 时启用）
  ├─ _start_telnet    （Telnet REPL）
  └─ WebFrameServer   （Web 终端：画面 + 状态 + 远程点击）
```

## Android 版
- Gradle 9.4.1, AGP 9.2.1, Kotlin 2.2.10
- 构建：`cd android && ./gradlew assembleDebug`
- 关键依赖：OpenCV 4.4.0（AAR）、TensorFlow Lite、OkHttp、Jetpack Compose
- CNN 模型部署在 `android/app/src/main/assets/cnn_model.tflite`
- ONNX → TFLite 转换：`powershell -File onnx_to_tflite.ps1`（需 `onnx2tf.exe`）
- TFLite 文件已在 `build.gradle.kts` 中配置 `noCompress`

## 数据流
```
ESP32-C3（BLE 模拟 GAN 魔方） ← HTTP → PC / 安卓
安卓手机（Cube Station） ← BLE → ESP32-C3
PC（Python 版）→ scrcpy（控制手机）+ HTTP（控制 ESP32）
PC（Python 版）→ BLE（真实 GAN 魔方，--proxy 模式）
安卓（APK 版）→ MediaProjection（截屏）+ 无障碍服务（点击）
```

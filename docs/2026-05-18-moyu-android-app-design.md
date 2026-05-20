# MOYU Android App 设计方案

**Date:** 2026-05-18

## Context

当前 MOYU 项目是一个运行在 PC 上的 Python 控制器，通过 ADB/scrcpy 连接 Android 手机，配合 ESP32 硬件（通过 BLE 模拟 GAN 智能魔方）实现 Cube Station 排位赛全自动运行。核心痛点在于必须依赖一台 PC 持续运行 Python 脚本，硬件部署成本高，使用场景受限。

目标是将整个控制器移植为 Android App，在手机上直接运行，仅保留 ESP32 作为底层 BLE 模拟器。

## Discussion

- **保活问题**：自己使用无需适配各种 ROM，App 运行时为前台状态，只需在设置中开启无障碍 + 悬浮窗权限 + 授权录屏即可，无额外成本。
- **零 root**：所有能力均为 Android 公开 API，不需要 root 权限。
- **图像处理依赖**：OpenCV/ONNX Runtime 全部砍掉。图像预处理（灰度/高斯模糊/二值化/直方图均衡化）、Canny 边缘检测、HoughCircles 圆检测、模板匹配（NCC）全部用纯 Kotlin 实现，零第三方 C/C++ 依赖。HoughCircles 输入为 1000×1200 区域，纯 Kotlin 估算 ~150ms/帧。
- **CNN 推理**：使用 TFLite 运行现有模型，APK 增量仅 ~2MB。
- **KNN 分类器**：准确率不够，放弃。
- **语言选择**：Kotlin。相比 Java 代码量减半，相比 Flutter 不存在 WindowManager 桥接问题，是 Android 原生开发的最薄方案。

## Approach

将 PC 控制器移植为 Android App，保留现有 ESP32 硬件。技术栈为 Kotlin + Jetpack Compose + TFLite + OkHttp，零 OpenCV/ONNX 依赖，APK 体积控制在 ~10MB 以内。

## Architecture

### 核心组件

| PC 组件 | Android 替代 | 依赖 |
|---|---|---|
| scrcpy 获取帧 | MediaProjection + ImageReader | 系统 API |
| scrcpy 触控注入 | AccessibilityService | 系统 API |
| OpenCV 灰度/高斯/Hough/模板匹配 | Kotlin 原生实现（~500 行） | 无 |
| OCR KNN 分类器 | ❌ 放弃 | - |
| OCR CNN 分类器 | TFLite | `org.tensorflow:tensorflow-lite` |
| CFOP 求解器 | Kotlin 重写 | 无，纯逻辑 |
| HTTP → ESP32 | OkHttp | `com.squareup.okhttp3:okhttp` |
| 控制台日志 | 悬浮窗 (SYSTEM_ALERT_WINDOW) | 系统 API |

### 数据流

```
手机屏幕
    ↕ MediaProjection API
App 截帧 → Kotlin Canny + HoughCircles 检测气泡
         → 裁剪字符 → TFLite CNN 推理
         → 解析打乱序列 → HTTP → ESP32 → BLE → 手机
                            ↕ HTTP GET /api/facelets
                  CFOP 求解 → HTTP → ESP32（执行解法）
```

### 开发环境搭建

1. **Android Studio** — 下载安装最新稳定版（Ladybug 或更高）
2. **JDK 17** — Android Studio 内置或自行安装
3. **Android SDK** — Studio 内 SDK Manager 安装 API 33+
4. **模型转换**（如现有 onnx 模型）：
   ```bash
   pip install onnx onnx2tf
   onnx2tf -i cnn_model.onnx -o cnn_model.tflite
   ```
5. **项目结构**：
   ```
   app/
   ├── src/main/java/com/moyu/
   │   ├── MainActivity.kt          # 启动 + 权限申请
   │   ├── service/
   │   │   ├── ScreenCaptureService.kt   # MediaProjection 截帧
   │   │   ├── AccessibilityService.kt   # 触控注入
   │   │   └── FloatLogService.kt        # 悬浮窗日志
   │   ├── vision/
   │   │   ├── ImageProcessor.kt     # 灰度/高斯/边缘检测
   │   │   ├── HoughCircles.kt       # 圆检测
   │   │   └── TemplateMatcher.kt    # NCC 模板匹配
   │   ├── ocr/
   │   │   ├── Classifier.kt         # TFLite 封装
   │   │   └── Parser.kt             # 标签 → 记号
   │   ├── solve/
   │   │   └── CfopSolver.kt         # CFOP 求解器
   │   ├── device/
   │   │   └── CubeApi.kt            # HTTP → ESP32
   │   └── state/
   │       └── StateMachine.kt       # 状态机编排
   └── src/main/res/raw/
       └── cnn_model.tflite          # CNN 模型
   ```

### 悬浮窗日志实现要点

- 通过 `SYSTEM_ALERT_WINDOW` 权限创建悬浮窗
- `WindowManager.LayoutParams` 设置 `TYPE_APPLICATION_OVERLAY`
- 日志通过 `Flow` 从后台推送至悬浮窗
- 支持：拖拽移动、点击展开/收起、可调节透明度

### 权限清单

1. `SYSTEM_ALERT_WINDOW` — 悬浮窗日志（设置中一次授权）
2. `MediaProjection` — 屏幕截图（每次启动弹窗确认）
3. `AccessibilityService` — 模拟点击（设置中手动开启）
4. `FOREGROUND_SERVICE` — 后台保活
5. `POST_NOTIFICATIONS` — Android 13+ 通知权限

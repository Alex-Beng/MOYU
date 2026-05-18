# MOYU Android App 设计方案

**Date:** 2026-05-18

## Context

当前 MOYU 项目是一个运行在 PC 上的 Python 控制器，通过 ADB/scrcpy 连接 Android 手机，配合 ESP32 硬件（通过 BLE 模拟 GAN 智能魔方）实现 Cube Station 排位赛全自动运行。核心痛点在于必须依赖一台 PC 持续运行 Python 脚本，硬件部署成本高，使用场景受限。

## Discussion

- **方案 A（保留 ESP32）**：用 Android App 取代 PC 端，App 通过 MediaProjection 获取屏幕、AccessibilityService 注入点击、OpenCV Android SDK 做图像识别、HTTP 控制 ESP32。双权限依赖（悬浮窗授权 + 无障碍服务）是主要门槛，国产 ROM 后台保活是潜在风险。
- **方案 B（纯软件）**：App 同时取代 ESP32，直接在手机上用 BLE GATT Server 模拟 GAN 魔方。零硬件但需要逆向并移植 BLE 协议，多线程复杂度更高。
- **悬浮窗日志**：用户提出后台悬浮窗显示日志的需求，确认可用 SYSTEM_ALERT_WINDOW 权限 + WindowManager.addView() 实现，权限一次开启后永久生效，门槛低于无障碍服务。
- **权衡**：方案 A 更务实，开发成本低（2-4 周 vs 3-6 周），方案 B 体验更彻底但逆向工作量不确定。

## Approach

采用**方案 A**，将 PC 控制器移植为 Android App，保留现有 ESP32 硬件。优先实现核心自动化闭环，后续可根据需要升级为方案 B。

## Architecture

### 核心组件

| PC 组件 | Android 替代 | 备注 |
|---|---|---|
| scrcpy 获取帧 | MediaProjection + ImageReader | 需用户弹窗授权 |
| scrcpy 触控注入 | AccessibilityService | 需用户在系统设置中开启 |
| OpenCV 模板匹配 | OpenCV Android SDK | APK 体积 ~100MB |
| OCR KNN/CNN 分类器 | TFLite / ONNX Runtime Android | 现有 onnx 模型可复用 |
| CFOP 求解器 | Kotlin 重写 | 纯逻辑，无第三方依赖 |
| HTTP → ESP32 | OkHttp 异步请求 | 标准方案 |
| 控制台日志 | 悬浮窗 (SYSTEM_ALERT_WINDOW) | WindowManager.addView，可拖拽/缩放 |

### 数据流

```
手机屏幕
    ↕ MediaProjection API
App 截帧 → OpenCV 检测按钮 → AccessibilityService 点击
         → OCR 识别打乱序列 → HTTP → ESP32 → BLE → 手机
                             ↕ HTTP GET /api/facelets
                   CFOP 求解 → HTTP → ESP32（执行解法）
```

### 悬浮窗日志实现要点

- 通过 `SYSTEM_ALERT_WINDOW` 权限创建悬浮窗
- `WindowManager.LayoutParams` 设置 `TYPE_APPLICATION_OVERLAY`
- 日志通过 `LiveData` 或 `Flow` 从后台服务推送至悬浮窗
- 支持：拖拽移动、点击展开/收起、可调节透明度
- 仅显示关键状态（OCR 结果、解法进度、错误信息），避免滚动刷屏

### 权限清单

1. `SYSTEM_ALERT_WINDOW` — 悬浮窗日志（一次手动授权）
2. `MediaProjection` — 屏幕截图（每次启动弹窗确认）
3. `AccessibilityService` — 模拟点击（设置中手动开启）
4. `FOREGROUND_SERVICE` — 后台保活
5. `POST_NOTIFICATIONS` — Android 13+ 通知权限

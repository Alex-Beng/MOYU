# **MOYU** = **M**ore **O**nline **Y**our  smart-c**U**be

MOYU是基于硬件模拟智能魔方，意图实现人类摸鱼（MOYU），机器自动上分的项目。


## 架构

需要：esp32c3 + 安卓手机 + 电脑

esp32c3用于ble模拟智能魔方，安卓手机用于启动cube station，电脑作为主控制器以及求解器。
安卓手机与esp32通过ble通信，电脑与安卓手机通过usb调试/无线调试连接，并通过wifi与esp32。

流程：wait_init -> init -> scramble -> solve -> reinit

| state | description |
|----------|-------------|
| wait_init ｜ 等待手机与esp连接；电脑与esp及手机连接 ｜
| init | 检测UI状态，开启匹配，等待打乱UI出现 |
| scramble | 打乱，直至打乱UI消失 |
| solve | 电脑求解并下发转动，等待打乱UI出现 or 结算UI|
| reinit | 点击各种结算UI，直至init |


各个阶段需要检测的UI需要可配置，包括几个UI，特征等。

容灾先不管

## 核心问题

1. UI识别的位置需要通过recipe引入，支持不同分辨率 or 机型设置。
2. 一个通用的，基于模板匹配的UI识别，需要可配置UI特征位置，特征图，识别后需点击位置。
3. 打乱UI识别之后，OCR打乱内容，字空间只有，RUFDBL'2，计划圆形轮廓+分类，需训练分类模型/KNN/模板。
4. 电脑与手机交互，拟基于python-scrcpy-client。

## 模块拆分

```
moyu/
├── recipe/
│   ├── schema.py          # Recipe JSON schema 定义与校验
│   ├── loader.py          # 加载/热重载 recipe 文件
│   └── recipes/
│       └── example.json   # 设备配置示例
├── vision/
│   ├── matcher.py         # 模板匹配核心（可配置特征图+位置）
│   ├── screenshot.py      # 截图抓取（scrcpy）
│   └── detector.py        # 状态机各阶段 UI 检测逻辑
├── ocr/
│   ├── segmentor.py       # 圆形轮廓检测 + 字符分割
│   ├── classifier.py      # KNN/模板匹配分类（字符集 RUFDBL'2）
│   ├── trainer.py         # 训练数据收集 & 模型训练入口
│   └── parser.py          # 原始识别结果 → 标准 move 序列
├── device/
│   ├── scrcpy_client.py   # python-scrcpy-client 封装（截图/点击/滑动/连接管理）
│   └── cube_api.py        # HTTP → ESP32 转动下发
├── controller.py          # 状态机主循环（wait_init→init→scramble→solve→reinit）
└── main.py                # 入口
```

## 依赖

- [gan-cube-emu](../gan-cube-emu) — ESP32-C3 BLE 魔方模拟器固件

"""BLE 魔方监听器 —— 纯连接 GAN i3，实时输出转动/陀螺仪并记录 CSV

用法：
    python -m tools.ble_monitor                              # 自动扫描 + 连接
    python -m tools.ble_monitor --address AA:BB:CC:DD:EE:FF  # 指定地址
    python -m tools.ble_monitor --no-csv                     # 仅输出，不记录
    python -m tools.ble_monitor --verbose                    # 显示面片更新
"""
import argparse
import asyncio
import logging
import signal
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ble_monitor")
logging.getLogger("bleak").setLevel(logging.WARNING)


def _format_ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:12]


async def main():
    parser = argparse.ArgumentParser(description="BLE 魔方监听器")
    parser.add_argument("--address", default=None, help="BLE 设备地址 (MAC)")
    parser.add_argument("--no-csv", action="store_true", help="仅输出，不记录 CSV")
    parser.add_argument("--verbose", action="store_true", help="显示面片更新等详细信息")
    args = parser.parse_args()

    from device.ble_cube import (
        BLECubeConnection,
        Gen2ProtocolParser,
        Gen2MoveEvent,
        Gen2GyroEvent,
        Gen2FaceletsEvent,
        scan_for_gen2,
    )

    proxy_logger = None
    if not args.no_csv:
        from device.proxy_logger import ProxyLogger
        proxy_logger = ProxyLogger()

    try:
        addr = args.address
        if not addr:
            print(f"[{_format_ts()}] 扫描 GAN i3 魔方...")
            addr = await scan_for_gen2(timeout=10.0)
            if not addr:
                print(f"[{_format_ts()}] 未发现 GAN i3 魔方")
                sys.exit(1)

        conn = BLECubeConnection(addr)
        await conn.connect()
        print(f"[{_format_ts()}] 已连接: {addr}")

        parser = Gen2ProtocolParser(conn.mac)
        print(f"[{_format_ts()}] 密钥派生完成，开始监听通知...")
        print("-" * 60)

        async for raw_data in conn.start_notify(None):
            ts = _format_ts()
            event = parser.parse(raw_data)
            if event is None:
                continue

            if isinstance(event, Gen2MoveEvent):
                print(f"[{ts}] 转动: {event.notation:>4s}  (face={event.face}, dir={event.direction})")
                if proxy_logger:
                    proxy_logger.log_move(event.face, event.direction)

            elif isinstance(event, Gen2GyroEvent):
                print(f"[{ts}] 陀螺仪: qw={event.qw:.4f}, qx={event.qx:.4f}, qy={event.qy:.4f}, qz={event.qz:.4f}, "
                      f"q2_sum={event.q2_sum:.4f}, v=({event.vx:+d},{event.vy:+d},{event.vz:+d})")
                if proxy_logger:
                    proxy_logger.log_gyro(event.qw, event.qx, event.qy, event.qz, event.vx, event.vy, event.vz)

            elif isinstance(event, Gen2FaceletsEvent):
                if args.verbose:
                    print(f"[{ts}] 面片更新: serial={event.serial}")

    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print(f"\n[{_format_ts()}] 用户中断")
    except Exception as e:
        logger.error("异常: %s", e, exc_info=True)
    finally:
        if proxy_logger:
            proxy_logger.close()
        print(f"[{_format_ts()}] 已断开")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
#!/usr/bin/env python3
"""MOYU - More Online Your Cube

入口点
"""
import asyncio
import logging
from pathlib import Path

from controller import Controller

LOG_DIR = Path("log")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(filename)s:%(lineno)d: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "moyu.log", encoding="utf-8"),
    ],
)


async def main():
    controller = Controller()
    await controller.run()


if __name__ == "__main__":
    asyncio.run(main())

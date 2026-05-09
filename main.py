#!/usr/bin/env python3
"""MOYU - More Online Your Cube

入口点
"""
import asyncio
import logging

from controller import Controller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(filename)s:%(lineno)d: %(message)s",
)


async def main():
    controller = Controller()
    await controller.run()


if __name__ == "__main__":
    asyncio.run(main())

"""CSV 日志记录器 —— 记录 BLE 魔方转动、陀螺仪、面片数据"""
import csv
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path("data") / "proxy"

CSV_HEADER = [
    "timestamp", "type",
    "face", "dir",
    "qw", "qx", "qy", "qz", "vx", "vy", "vz",
    "facelets",
]


class ProxyLogger:
    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else DATA_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._file: Path | None = None
        self._writer: csv.writer | None = None
        self._fh = None
        self._row_count = 0
        self._open_file()

    def _open_file(self):
        today = datetime.now().strftime("%Y%m%d")
        idx = 0
        while True:
            path = self.output_dir / f"{today}_{idx}.csv"
            if not path.exists():
                break
            idx += 1
        self._fh = open(path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._fh)
        self._writer.writerow(CSV_HEADER)
        self._file = path
        self._row_count = 0
        logger.info("CSV 日志: %s", path)

    def log_move(self, face: int, direction: int):
        ts = datetime.now().isoformat(timespec="microseconds")
        self._writer.writerow([ts, "move", face, direction, "", "", "", "", "", "", "", ""])
        self._row_count += 1
        self._maybe_flush()

    def log_gyro(self, qw: float, qx: float, qy: float, qz: float, vx: int = 0, vy: int = 0, vz: int = 0):
        ts = datetime.now().isoformat(timespec="microseconds")
        self._writer.writerow([ts, "gyro", "", "", f"{qw:.6f}", f"{qx:.6f}", f"{qy:.6f}", f"{qz:.6f}", vx, vy, vz, ""])
        self._row_count += 1
        self._maybe_flush()

    def log_facelets(self, facelets_str: str):
        ts = datetime.now().isoformat(timespec="microseconds")
        self._writer.writerow([ts, "facelets", "", "", "", "", "", "", "", "", "", facelets_str])
        self._row_count += 1
        self._maybe_flush()

    def _maybe_flush(self):
        if self._row_count % 50 == 0:
            self._fh.flush()

    def close(self):
        if self._fh:
            self._fh.flush()
            self._fh.close()
            self._fh = None
            logger.info("CSV 日志已关闭: %s (共 %d 行)", self._file, self._row_count)
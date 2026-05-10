"""原始识别结果 → 标准 move 序列

输入：分类器输出的标签列表，如 ["R", "U", "R'", "U'"]
输出：空格分隔的标准记号字符串，如 "R U R' U'"
"""
import logging
import re

from ocr.classifier import LABELS

logger = logging.getLogger(__name__)

_VALID_LABELS = set(LABELS)
_EMPTY_LABELS = {"EMPTY", "?"}


def parse(raw_labels: list[str]) -> str:
    """将分类器输出的标签列表转换为标准魔方转动序列。

    Args:
        raw_labels: Classifier.predict_batch() 的输出，如 ["R", "U", "R'", "U'"]

    Returns:
        空格分隔的 move 序列，如 "R U R' U'"。
        无效标签（"?"）会被过滤掉并记录警告。
    """
    valid = []
    for label in raw_labels:
        if label in _VALID_LABELS and label not in _EMPTY_LABELS:
            valid.append(label)
        elif label not in _EMPTY_LABELS:
            logger.warning("过滤无效标签: %r", label)
    return " ".join(valid)


if __name__ == "__main__":
    """单独测试：python -m ocr.parser [labels...]

    示例：
        python -m ocr.parser R U "R'" "U'"
        python -m ocr.parser "RUR'U'"
    """
    import sys
    logging.basicConfig(level=logging.INFO)

    args = sys.argv[1:]
    if not args:
        print("Usage: python -m ocr.parser [labels...] | \"RUR'U'\"")
        sys.exit(1)

    # 若只传一个无空格字符串，走 parse_from_string
    if len(args) == 1 and " " not in args[0]:
        result = parse_from_string(args[0])
        print(f"parse_from_string({args[0]!r}) → {result!r}")
    else:
        result = parse(args)
        print(f"parse({args}) → {result!r}")


def parse_from_string(raw: str) -> str:
    """从原始字符串（无空格）解析 move 序列，用于 OCR 文本识别场景。

    Example:
        "RUR'U'" → "R U R' U'"
    """
    # 匹配 move 记号：字母 + 可选 2 + 可选 '
    tokens = re.findall(r"[RUFDBL][2]?'?", raw)
    valid = [t for t in tokens if t in _VALID_LABELS]
    invalid = set(tokens) - set(valid)
    if invalid:
        logger.warning("过滤无效 token: %s", invalid)
    return " ".join(valid)
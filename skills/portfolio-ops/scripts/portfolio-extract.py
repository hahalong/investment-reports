#!/usr/bin/env python3
"""
portfolio-extract.py
从同花顺/富途/老虎截图提取持仓数据，写入标准JSON格式记忆文件。
用法：python3 portfolio-extract.py <image_path> [--account <account_name>] [--output <json_path>]
"""

import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def extract_text_from_image(image_path: str) -> str:
    """用pytesseract做OCR，失败时返回空字符串"""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text
    except ImportError:
        return ""
    except Exception as e:
        print(f"[WARN] OCR失败: {e}", file=sys.stderr)
        return ""


def parse_args():
    p = argparse.ArgumentParser(description="持仓截图提取工具")
    p.add_argument("image", help="截图路径（支持多个）", nargs="+")
    p.add_argument("--account", default="unknown", help="账户名称")
    p.add_argument("--output", default=None, help="输出JSON路径")
    p.add_argument("--workspace", default="/home/ecs-user/.openclaw/workspace-investment-officer",
                   help="工作区路径")
    return p.parse_args()


def main():
    args = parse_args()
    workspace = Path(args.workspace)
    today = datetime.now().strftime("%Y-%m-%d")

    result = {
        "extract_time": datetime.now().isoformat(),
        "account": args.account,
        "source_images": args.image,
        "holdings": [],
        "total_count": 0,
        "notes": []
    }

    # OCR提取（辅助，主要靠Agent视觉能力）
    for img_path in args.image:
        text = extract_text_from_image(img_path)
        if text:
            result["notes"].append(f"OCR text from {img_path}: {text[:500]}")

    # 输出路径
    output_path = args.output or str(workspace / "memory" / f"{today}-extract.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[OK] 提取结果已写入: {output_path}")
    return output_path


if __name__ == "__main__":
    main()

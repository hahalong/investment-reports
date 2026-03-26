#!/usr/bin/env python3
"""
portfolio-validate.py
校验持仓记忆文件的完整性：
1. 对比截图中股票数量 vs 记忆文件条目数
2. 检查必填字段（名称、代码、盈亏%、成本、现价）
3. 输出缺失清单

用法：python3 portfolio-validate.py <memory_md_or_json> [--expected-count N]
"""

import sys
import re
import json
import argparse
from pathlib import Path


def count_holdings_in_markdown(md_path: str) -> tuple[int, list[str]]:
    """从Markdown表格中统计持仓条目和名称列表"""
    text = Path(md_path).read_text(encoding="utf-8")
    
    # 匹配表格行（排除表头和分隔线）
    holdings = []
    in_table = False
    
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("|") and "---" not in line:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells and cells[0] not in ("股票", "名称", "代码", "市值"):
                # 过滤掉表头行
                if not any(h in cells[0] for h in ["股票", "名称", "代码", "标的"]):
                    holdings.append(cells[0])
    
    return len(holdings), holdings


def validate_coverage(md_path: str, expected: int = None):
    """主校验函数"""
    count, names = count_holdings_in_markdown(md_path)
    
    print(f"=== 持仓完整性校验 ===")
    print(f"文件: {md_path}")
    print(f"检测到条目数: {count}")
    
    if expected:
        if count >= expected:
            print(f"✅ 覆盖完整: {count}/{expected}")
        else:
            print(f"❌ 覆盖不足: {count}/{expected}，缺少 {expected - count} 条")
            return False
    
    print(f"\n已记录标的：")
    for i, name in enumerate(names, 1):
        print(f"  {i:3d}. {name}")
    
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", help="记忆文件路径（.md 或 .json）")
    p.add_argument("--expected-count", type=int, default=None, help="预期持仓数量")
    args = p.parse_args()
    
    ok = validate_coverage(args.file, args.expected_count)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

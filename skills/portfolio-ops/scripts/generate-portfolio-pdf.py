#!/usr/bin/env python3
"""
generate-portfolio-pdf.py
读取持仓记忆JSON/MD，生成带操作建议的标准PDF。
依赖：google-chrome (headless) 或 wkhtmltopdf

用法：python3 generate-portfolio-pdf.py <memory_file> [--output <pdf_path>] [--template <html_template>]
"""

import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


HTML_WRAPPER = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', sans-serif;
          font-size: 10.5pt; color: #1a1a2e; line-height: 1.7; }}
  .page {{ padding: 36px 48px; }}
  h1 {{ font-size: 17pt; font-weight: 700; color: #0f3460;
        border-bottom: 3px solid #ffc832; padding-bottom: 7px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 9.5pt; }}
  th {{ background: #0f3460; color: #fff; padding: 7px 10px; font-weight: 600; text-align: left; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #eaeff5; }}
  tr:nth-child(even) td {{ background: #f7f9fc; }}
  .up {{ color: #c0392b; font-weight: 700; }}
  .dn {{ color: #1a7a4a; font-weight: 700; }}
  .tag-r {{ background:#fde8e8; color:#c0392b; border-radius:4px; padding:2px 7px; font-size:8.5pt; }}
  .tag-g {{ background:#e8f8ee; color:#1a7a4a; border-radius:4px; padding:2px 7px; font-size:8.5pt; }}
  .tag-y {{ background:#fff8e1; color:#b8860b; border-radius:4px; padding:2px 7px; font-size:8.5pt; }}
  .footer {{ font-size: 8.5pt; color: #999; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
</style>
</head>
<body>
<div class="page">
{content}
<div class="footer">生成时间：{gen_time} · 仅供参考，不构成投资建议</div>
</div>
</body>
</html>"""


def render_pdf(html_content: str, output_path: str) -> bool:
    """用Chrome headless渲染PDF"""
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html_content)
        tmp_html = f.name
    
    try:
        result = subprocess.run([
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={output_path}",
            "--print-to-pdf-no-header",
            f"file://{tmp_html}"
        ], capture_output=True, text=True, timeout=60)
        
        if Path(output_path).exists():
            size = Path(output_path).stat().st_size
            print(f"[OK] PDF已生成: {output_path} ({size/1024:.1f}KB)")
            return True
        else:
            print(f"[ERROR] PDF生成失败: {result.stderr[:200]}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Chrome超时", file=sys.stderr)
        return False
    finally:
        Path(tmp_html).unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("memory_file", help="持仓记忆文件（.md 或 .json）")
    p.add_argument("--output", default=None, help="输出PDF路径")
    args = p.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    output = args.output or f"/home/ecs-user/.openclaw/workspace-investment-officer/reports/{today}-portfolio-ops.pdf"

    # 读取内容（实际分析由Agent完成，此脚本负责渲染）
    content = f"<h1>持仓操作建议 · {today}</h1><p>请由Agent填充分析内容后调用此脚本渲染。</p>"
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M GMT+8")

    html = HTML_WRAPPER.format(content=content, gen_time=gen_time)
    success = render_pdf(html, output)
    
    if success:
        print(output)  # stdout输出路径供调用方使用
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

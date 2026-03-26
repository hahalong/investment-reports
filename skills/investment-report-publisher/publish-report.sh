#!/bin/bash
# 投资报告发布脚本 - 测试版
# 自动生成PDF、上传GitHub、通知老板

set -e

# 配置
REPO_DIR="/home/ecs-user/.openclaw/workspace/investment-reports"
GITHUB_REPO="hahalong/investment-reports"
REPORT_DATE=${1:-$(date +%Y-%m-%d)}
REPORT_FILE="report-${REPORT_DATE}.html"
PDF_FILE="report-${REPORT_DATE}.pdf"

echo "========================================"
echo "投资报告发布系统"
echo "日期: ${REPORT_DATE}"
echo "========================================"

# Step 1: 检查依赖
echo "[1/5] 检查依赖..."
if ! command -v wkhtmltopdf &> /dev/null; then
    echo "❌ 错误: wkhtmltopdf 未安装"
    echo "请运行: sudo apt-get install -y wkhtmltopdf"
    exit 1
fi
echo "✅ wkhtmltopdf 已安装"

# Step 2: 获取报告内容
echo "[2/5] 获取报告内容..."

# 优先从参数2获取报告内容（JSON格式文件路径）
if [ -n "$2" ] && [ -f "$2" ]; then
    echo "从文件读取报告内容: $2"
    REPORT_CONTENT=$(cat "$2")
elif [ -n "$2" ]; then
    echo "从参数读取报告内容"
    REPORT_CONTENT="$2"
else
    echo "使用示例数据（测试模式）"
    REPORT_CONTENT=$(cat << 'EOF'
<h2>【主要指数表现】</h2>
<table>
    <tr><th>指数</th><th>收盘</th><th>涨跌</th><th>涨跌幅</th></tr>
    <tr><td>标普500</td><td>6591.90</td><td style="color:#e74c3c">+35.53</td><td style="color:#e74c3c">+0.54%</td></tr>
    <tr><td>纳斯达克</td><td>21929.83</td><td style="color:#e74c3c">+167.94</td><td style="color:#e74c3c">+0.77%</td></tr>
    <tr><td>道琼斯</td><td>46429.49</td><td style="color:#e74c3c">+305.43</td><td style="color:#e74c3c">+0.66%</td></tr>
</table>

<h2>【热门科技股】</h2>
<table>
    <tr><th>股票</th><th>价格</th><th>涨跌</th></tr>
    <tr><td>英伟达 (NVDA)</td><td>$178.68</td><td style="color:#e74c3c">+1.99%</td></tr>
    <tr><td>亚马逊 (AMZN)</td><td>$211.71</td><td style="color:#e74c3c">+2.16%</td></tr>
    <tr><td>特斯拉 (TSLA)</td><td>$385.95</td><td style="color:#e74c3c">+0.76%</td></tr>
</table>

<h2>【中概股表现】</h2>
<table>
    <tr><th>股票</th><th>价格</th><th>涨跌</th></tr>
    <tr><td>京东 (JD)</td><td>$29.75</td><td style="color:#e74c3c">+8.30% ⭐</td></tr>
    <tr><td>拼多多 (PDD)</td><td>$102.61</td><td style="color:#e74c3c">+4.61%</td></tr>
    <tr><td>阿里巴巴 (BABA)</td><td>$129.87</td><td style="color:#e74c3c">+3.50%</td></tr>
</table>

<div style="background:#fff3cd;padding:15px;border-radius:5px;margin:20px 0;">
    <strong>市场观察：</strong><br>
    1️⃣ 大盘连续第二日收涨，罗素2000涨1.23%<br>
    2️⃣ 中概股全线上涨，京东大涨8.30%，拼多多涨4.61%<br>
    3️⃣ VIX回落至25，恐慌情绪持续缓解
</div>

<p><strong>风险提示：</strong>美股连续两日反弹，中概股表现强劲。VIX回落显示市场情绪改善。以上数据仅供参考，不构成投资建议。</p>
EOF
)
fi

# Step 3: 生成HTML报告
echo "[3/5] 生成HTML报告..."

cat > "${REPO_DIR}/${REPORT_FILE}" << HTMLEOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>美股收盘复盘报告 - ${REPORT_DATE}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            color: #333;
        }
        h1 {
            color: #1a1a1a;
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c2c2c;
            margin-top: 30px;
            border-left: 4px solid #00d4ff;
            padding-left: 10px;
        }
        .header {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: white;
            border: none;
            margin: 0;
            font-size: 28px;
        }
        .meta {
            color: rgba(255,255,255,0.9);
            font-size: 14px;
            margin-top: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 美股收盘复盘报告</h1>
        <div class="meta">报告日期：${REPORT_DATE} | 数据来源：Yahoo Finance | 生成时间：$(date '+%Y-%m-%d %H:%M:%S')</div>
    </div>
    
    <div class="content">
        ${REPORT_CONTENT}
    </div>
    
    <div class="footer">
        <p>本报告由AI投资官自动生成，仅供参考，不构成投资建议。</p>
        <p>© 2026 Investment Officer | Powered by OpenClaw</p>
    </div>
</body>
</html>
HTMLEOF

echo "✅ HTML报告已生成: ${REPORT_FILE}"

# Step 4: 生成PDF
echo "[4/5] 生成PDF..."
cd "${REPO_DIR}"

if wkhtmltopdf --enable-local-file-access --page-size A4 "${REPORT_FILE}" "${PDF_FILE}"; then
    echo "✅ PDF已生成: ${PDF_FILE}"
else
    echo "❌ PDF生成失败"
    exit 1
fi

# 更新README
cat > README.md << EOF
# 投资报告仓库

自动生成的投资复盘报告PDF存档。

## 最新报告

- **${REPORT_DATE}** - [查看PDF](${PDF_FILE}) | [查看HTML](${REPORT_FILE})

## 历史报告

| 日期 | PDF | HTML |
|:---|:---|:---|
| ${REPORT_DATE} | [PDF](${PDF_FILE}) | [HTML](${REPORT_FILE}) |

## 说明

- 本仓库由AI投资官自动维护
- 每日美股收盘后自动生成报告（北京时间05:00）
- 报告仅供参考，不构成投资建议
EOF

echo "✅ README已更新"

# Step 5: 上传到GitHub
echo "[5/5] 上传到GitHub..."
git config user.email "kitty@openclaw.ai"
git config user.name "Kitty"
git add -A

if git commit -m "添加${REPORT_DATE}美股复盘报告"; then
    if git push origin main; then
        echo "✅ 已上传到GitHub"
    else
        echo "❌ GitHub推送失败"
        exit 1
    fi
else
    echo "⚠️ 没有新内容需要提交"
fi

# 获取文件大小
PDF_SIZE=$(du -h "${PDF_FILE}" | cut -f1)
GITHUB_URL="https://github.com/${GITHUB_REPO}/blob/main/${PDF_FILE}"

echo ""
echo "========================================"
echo "✅ 报告发布完成！"
echo "========================================"
echo "日期: ${REPORT_DATE}"
echo "PDF文件: ${PDF_FILE} (${PDF_SIZE})"
echo "GitHub链接: ${GITHUB_URL}"
echo "========================================"

# 输出JSON格式的结果（供调用者解析）
echo ""
echo "{\"status\":\"success\",\"date\":\"${REPORT_DATE}\",\"pdf\":\"${PDF_FILE}\",\"size\":\"${PDF_SIZE}\",\"url\":\"${GITHUB_URL}\"}"

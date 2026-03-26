#!/bin/bash
# 芒格投资官 — 自动上传报告到GitHub + 更新README
# 用法：./scripts/upload-to-github.sh <pdf文件名> <报告标题> <说明>
# 示例：./scripts/upload-to-github.sh 2026-03-26-top10-potential-stocks.pdf "十倍潜力牛股" "精选10标的低位深度分析"

set -e

WORKSPACE="/home/ecs-user/.openclaw/workspace-investment-officer"
source "$WORKSPACE/.openclaw/github.env"

FILE_NAME="${1:-}"
REPORT_TITLE="${2:-}"
REPORT_DESC="${3:-}"
DATE=$(date +%Y-%m-%d)

cd "$WORKSPACE"

git config user.email "$GITHUB_EMAIL"
git config user.name "芒格投资官"
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/investment-reports.git"

# 添加新文件
if [ -n "$FILE_NAME" ]; then
    git add "reports/$FILE_NAME" 2>/dev/null || true
fi
git add reports/ memory/ 2>/dev/null || true

# 只提交有变更的情况
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    REPORT_COUNT=$(ls reports/*.pdf 2>/dev/null | wc -l)
    COMMIT_MSG="📊 投资报告更新 ${DATE}"
    if [ -n "$REPORT_TITLE" ]; then
        COMMIT_MSG="📊 新增报告：${REPORT_TITLE} (${DATE})"
    fi
    git commit -m "$COMMIT_MSG (共${REPORT_COUNT}份PDF)" && \
    git push origin main && \
    echo "✅ GitHub上传成功"
fi

# 更新README（如果提供了文件名和说明）
if [ -n "$FILE_NAME" ] && [ -n "$REPORT_TITLE" ]; then
    python3 "$WORKSPACE/scripts/update-readme.py" \
        "$FILE_NAME" "$REPORT_TITLE" "${REPORT_DESC:-}" "$DATE" && \
    echo "✅ README已更新"
fi

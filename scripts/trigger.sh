#!/bin/bash
# 投资官cron触发脚本 — 通过Gateway REST API发送消息
# 用法: trigger.sh "触发消息"

GATEWAY_PORT=18789
SESSION_KEY="agent:investment-officer:feishu:direct:ou_9e1faeb04ed22cca6b10152077633edb"
MESSAGE="${1:-[CRON] 心跳检查}"
LOG_FILE="/home/ecs-user/.openclaw/workspace-investment-officer/logs/cron.log"

mkdir -p "$(dirname $LOG_FILE)"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发: $MESSAGE" >> "$LOG_FILE"

RESPONSE=$(curl -s -X POST "http://localhost:${GATEWAY_PORT}/api/sessions/send" \
  -H "Content-Type: application/json" \
  -d "{\"sessionKey\": \"${SESSION_KEY}\", \"message\": \"${MESSAGE}\"}" 2>&1)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 响应: $RESPONSE" >> "$LOG_FILE"

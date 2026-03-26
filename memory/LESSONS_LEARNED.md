# 投资官工作日志 — 踩坑记录

## 坑1：飞书发送本地文件（2026-03-09）
**问题**：`message(action=send, media=/local/path)` 发本地文件，用户收到的是路径文字
**根因**：feishu `outbound.ts` 上传失败时 silent fallback 成文字
**正确做法**：直接调飞书REST API
```js
// 1. 获取token: POST /auth/v3/tenant_access_token/internal
// 2. 上传文件: POST /im/v1/files (multipart/form-data, file_type=pdf)
// 3. 发送消息: POST /im/v1/messages, msg_type=file, content={file_key}
```
**配置信息**：
- appId: `cli_a927c0a8fb38dcb1`
- appSecret: `RNb8TFYnJ8ztwQdDwdtEwhCLpWIVGBZx`
- 用户 open_id: `ou_9e1faeb04ed22cca6b10152077633edb`

---

## 坑2：时间判断错误（2026-03-10）
**问题**：凌晨00:19说"A股还有10分钟开盘（10:00）"，美股开盘时间也错了
**错误清单**：
1. A股/港股开盘是09:30，不是10:00
2. 美股3月起（夏令时）北京时间21:30开盘，不是22:30（冬令时才是22:30）
3. 没查当前时间就乱推算，凌晨说"还有10分钟开盘"

**根因**：没有调用 `session_status` 确认当前时间，直接用错误假设

**规则（必须遵守）**：
- ❌ 禁止不查时间直接推算"现在几点"、"距开盘还有X分钟"
- ✅ 凡涉及时间判断，必须先调用 `session_status` 获取当前时间
- ✅ 正确开盘时间：
  - A股/港股：**09:30**（竞价 08:00-09:20）
  - 美股夏令时（3月第二个周日 - 11月第一个周日）：北京时间 **21:30**
  - 美股冬令时（其余时间）：北京时间 **22:30**
  - 2026年夏令时开始：3月8日；结束：11月1日

---

## 坑3：跨Agent通信（2026-03-09/10）
**问题**：无法用 `sessions_list` / `sessions_send` 联系Kitty
**根因**：`tools.sessions.visibility` 未配置为 `all`，只能看到自己的session
**解决方案**：需要Kitty或老板在openclaw配置中开启 `tools.sessions.visibility=all`
**临时方案**：通过用户转达消息给Kitty

---

## 坑4：未主动执行每日职责（2026-03-09）
**问题**：整天没有主动推送交易计划、复盘等
**根因**：没有heartbeat/cron触发机制，被动等待消息
**解决方案**：需配置定时cron任务触发以下职责：
- 08:30 — 当日交易计划
- 15:35 — A股/港股收盘复盘
- 21:25 — 美股开盘前分析（夏令时）/ 22:25（冬令时）
- 周六11:00 — 周度复盘
- 月末17:00 — 月度复盘

# SKILL: research-report
## 研究报告生成标准流程（调研→分析→PDF）

### 触发条件
- 用户要求对某个标的/主题进行研究分析
- 用户说"调研一下XXX"、"分析XXX"、"生成XXX报告"
- 用户要求生成PDF报告

---

## 标准三段式流程

### 阶段零：获取实时价格（⚠️ 强制步骤，所有个股分析必须先执行）

**在任何分析开始前，必须用 yfinance 查询实时价格，禁止使用搜索结果里的估算价格或记忆中的历史数据。**

```python
import yfinance as yf

# A股格式：后缀 .SS（上交所）或 .SZ（深交所）
# 港股格式：去掉前导0，后缀 .HK（如 9988.HK，不是 09988.HK）
# 美股格式：直接代码（GOOGL、MSFT、TSLA）

stocks = {
    '标的名称': '代码.交易所',
    # 例：'中国核建': '601611.SS'
    # 例：'阿里巴巴': '9988.HK'
    # 例：'谷歌': 'GOOGL'
}
for name, sym in stocks.items():
    t = yf.Ticker(sym)
    h = t.history(period='5d')
    if not h.empty:
        last = h['Close'].iloc[-1]
        date = h.index[-1].strftime('%m-%d')
        print(f'{name} {sym}: {last:.3f} ({date})')
```

**止损/目标价计算规则**：
- 止损价 = `实时价格 × (1 - 止损百分比)`，**禁止硬编码固定数字**
- 目标价 = `预期EPS × 合理PE倍数`，需说明PE来源

> ⚠️ **教训记录（2026-03-21）**：
> - 中国核建初始使用搜索估算15.48元，实际收盘14.75元 → 用户纠正
> - GOOGL止损写$130（历史旧价），实际收盘$301 → 严重偏离
> - **根本原因**：跳过了实时价格查询步骤

---

### 阶段一：调研（Research）

**目标**：获取准确、多源交叉验证的数据

1. **并行搜索**（同时发起，节省时间）：
   - 中文搜索：`web_search(query="XXX 最新动态/财报/技术分析", search_lang="zh")`
   - 英文搜索：`web_search(query="XXX analysis/earnings/support level", search_lang="en")`

2. **数据验证规则**：
   - **股价数据**：必须用 yfinance 实时查询（见阶段零），不使用搜索结果里的价格
   - 关键数据必须2个来源交叉验证
   - 不确定数据标注 ⚠️ 待验证
   - 绝不使用模拟/虚构数据

3. **调研范围（根据报告类型选择）**：
   - **个股分析**：当日价格、财报/公告、机构评级、技术支撑位、行业对比
   - **宏观主题**：政策动向、数据发布、市场反应、机构观点
   - **对比分析**：两个标的的驱动逻辑差异、数据对比、操作建议

---

### 阶段二：分析（Analysis）

**目标**：从数据中提炼结论，给出有逻辑支撑的判断

**分析框架（必须包含）**：
1. **现状描述**：今日/最新数据，不遗漏关键数字
2. **原因拆解**：为什么会这样？至少拆解3个层次
3. **支撑位/目标位**：技术面关键价位，来源标注
4. **操作建议**：具体到：什么情景→什么操作→什么价格→什么时间
5. **置信度标注**：每个结论标注 高/中/低

**分析质量要求**：
- 结论必须自我验证，不能推回给用户复核
- 操作建议必须有情景分析（不只有一个结论）
- 不确定的一律标注，不假装确定

---

### 阶段三：生成PDF（Report Generation）

**目标**：输出美观、信息密度高、易于阅读的PDF报告

**HTML模板规范**：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  /* 基础字体 */
  body { font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'PingFang SC', sans-serif;
         font-size: 10.5pt; color: #1a1a2e; line-height: 1.75; }
  .page { max-width: 960px; margin: 0 auto; padding: 36px 48px; background: #fff; }
  
  /* 标题区：使用渐变色背景，根据主题选颜色 */
  /* 绿色系：投资/化工/A股 → #1b4332~#40916c */
  /* 紫色系：宏观/贵金属/综合 → #4a1942~#9c4daa */
  /* 蓝色系：科技/AI/互联网 → #0d3a6b~#1565c0 */
  
  /* 必须包含：h2（章节标题）、表格、alert-box（四色：绿/黄/蓝/红）*/
  /* 操作建议区：使用三色情景卡片（红=跌、黄=平、绿=涨）*/
</style>
</head>
```

**PDF生成命令**：
```bash
google-chrome \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --run-all-compositor-stages-before-draw \
  --print-to-pdf="/home/ecs-user/.openclaw/workspace-investment-officer/reports/YYYY-MM-DD-{topic}.pdf" \
  --print-to-pdf-no-header \
  "file:///home/ecs-user/.openclaw/workspace-investment-officer/reports/YYYY-MM-DD-{topic}.html"
```

**发送规则**：
```python
message(
    action="send",
    channel="feishu",
    target="ou_9e1faeb04ed22cca6b10152077633edb",  # 老板
    media="/home/ecs-user/.openclaw/workspace-investment-officer/reports/YYYY-MM-DD-{topic}.pdf"
)
```

---

### 阶段四：推送GitHub（⚠️ 强制步骤，每次生成/更新报告后必须执行）

**所有报告生成或更新后，必须默认推送到 GitHub 并更新 README。**

```bash
cd /home/ecs-user/.openclaw/workspace-investment-officer

# 1. 加载 Token（禁止在代码/内存中明文写入 Token）
source .openclaw/github.env

# 2. 设置带 Token 的远程地址
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/hahalong/investment-reports.git"

# 3. 暂存 & 拉取最新（避免冲突）
git stash 2>/dev/null || true
git pull origin main --rebase 2>/dev/null || true
git stash pop 2>/dev/null || true

# 4. 提交报告
git add reports/YYYY-MM-DD-{topic}.pdf reports/YYYY-MM-DD-{topic}.html 2>/dev/null || true
git add -A
git commit -m "📊 报告：{报告标题} {YYYY-MM-DD}"

# 5. 推送
git push origin main
```

**README 更新规则（与上传同步执行）**：
- 每次上传后在 README 表格顶部插入一行：`| YYYY-MM-DD | 文件链接 | 报告说明 |`
- 可调用 `scripts/upload-to-github.sh` 脚本自动完成上传+README更新：
  ```bash
  ./scripts/upload-to-github.sh "文件名.pdf" "报告标题" "一句话说明"
  ```

**完成后通知用户 GitHub 链接**：
```
✅ 已推送GitHub：
https://github.com/hahalong/investment-reports/blob/main/reports/YYYY-MM-DD-{topic}.pdf
```

> ⚠️ **安全规则**：Token 存于 `.openclaw/github.env`（已加入 .gitignore），禁止在任何代码、memory文件、提交内容中写入 Token 明文。

---

## 报告文件命名规范

| 类型 | 命名格式 | 示例 |
|------|------|------|
| 个股分析 | `YYYY-MM-DD-{ticker}-analysis.pdf` | `2026-03-19-alibaba-earnings.pdf` |
| 对比分析 | `YYYY-MM-DD-{topic}-compare.pdf` | `2026-03-19-chem-us-vs-cn.pdf` |
| 行情分析 | `YYYY-MM-DD-{topic}.pdf` | `2026-03-19-gold-silver-aluminum.pdf` |
| 含个人持仓 | 结尾不加 `-public` | 仅发老板，注明⚠️请勿外传 |
| 公开版 | 结尾加 `-public` | 可转发 |

---

## 质量检查清单（发送前必须确认）

- [ ] 数据来源已标注（至少一处）
- [ ] 不确定数据已标注 ⚠️
- [ ] 操作建议有情景分析（至少2个情景）
- [ ] 置信度已标注
- [ ] PDF文件大小合理（100KB–2MB）
- [ ] 如含个人持仓，底部有"请勿外传"提示
- [ ] 发送绝对路径（`/home/ecs-user/...`），非相对路径

---

## Token优化策略

| 操作 | 优化方式 |
|------|------|
| 搜索 | 中英并行，一次查够，不重复搜索 |
| 分析 | 直接写HTML，不先写Markdown再转换 |
| PDF | 一次生成，不反复修改 |
| 发送 | 生成后立即发送，不等确认 |

---

## 错误处理

- Chrome生成失败 → 重试1次，仍失败则发Markdown原文
- Feishu发送失败 → 检查绝对路径，重试1次，仍失败报告用户
- 搜索结果为空 → 标注"数据暂缺"，用已有信息分析，不造数据

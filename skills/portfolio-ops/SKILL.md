---
name: portfolio-ops
description: 三账户持仓管理全流程Skill：从截图读取持仓→维护记忆文件→逐只股票分析+关键点位→完整性校验→生成PDF发送。当用户发送持仓截图、要求持仓操作建议、要求生成持仓报告PDF，或提及"持仓分析"、"下周操作建议"时触发本Skill。
---

# Portfolio Ops Skill

三账户（港股主账户/港美混合/国金A股）持仓管理全流程。

## 流程总览（4步，必须按序执行）

```
Step 1: 提取  →  Step 2: 维护记忆  →  Step 3: 分析  →  Step 4: 校验+输出PDF
```

---

## Step 1：从截图提取持仓

**接收截图时**，用视觉能力逐行读取，不使用OCR脚本（精度更高）。

**提取规则：**
- 逐账户逐行点数，数清每个截图的股票总数
- 在提取结束时**大声报数**："账户X共提取到 N 只股票"
- 多张截图时分批提取，每批完成后汇总

**标准读取字段：** 股票名称、代码、市值、持仓量、现价、成本、盈亏(元)、盈亏%

---

## Step 2：维护记忆文件

写入 `memory/YYYY-MM-DD.md`，格式见 `references/memory-format.md`。

**强制校验（写入后立即执行）：**
```bash
python3 scripts/portfolio-validate.py memory/YYYY-MM-DD.md --expected-count N
```

若输出 `❌ 覆盖不足`，立即补充漏掉的条目，再次验证通过后才能进入Step 3。

**三账户分别建表，表头统一：**
```
| 股票 | 代码 | 市值 | 持仓量 | 现价 | 成本 | 持仓盈亏 | 盈亏% |
```

---

## Step 3：逐只分析+操作建议

参考 `references/analysis-framework.md` 的优先级和宏观框架。

**每只股票必须包含：**
- 操作方向（清仓/减仓/持有/加仓/观望）
- 止损位（必填，不可为空）
- 目标价
- 1-2句操作逻辑

**特别注意：**
- 杠杆ETF（07226、MSTZ、UGL、HIMZ等）：单独说明每日损耗风险
- 成本价异常高（疑似反向拆股）：标注说明，不以此为止损参考
- 同一标的跨账户持仓：合并分析

**HTML报告生成：**
以 `assets/pdf-template.html` 为样式基础，内容填充到对应章节。

---

## Step 4：完整性校验 + 生成PDF

### 校验清单（生成PDF前必须完成）

```
账户一港股：截图N只 → 报告N只 ✅/❌
账户二港股：截图N只 → 报告N只 ✅/❌
账户二美股：截图N只 → 报告N只 ✅/❌
账户三A股：截图N只 → 报告N只 ✅/❌
合计：截图总计N只 → 报告覆盖N只 ✅
```

有任何 `❌` 则补充后再生成PDF。

### 生成PDF（Chrome headless，不用wkhtmltopdf）

```bash
google-chrome \
  --headless=new --no-sandbox --disable-gpu \
  --disable-dev-shm-usage \
  --run-all-compositor-stages-before-draw \
  --print-to-pdf="reports/YYYY-MM-DD-portfolio-ops.pdf" \
  --print-to-pdf-no-header \
  "file:///absolute/path/to/report.html"
```

### 发送PDF

```python
message(
    action="send",
    channel="feishu",
    target="ou_9e1faeb04ed22cca6b10152077633edb",
    media="/home/ecs-user/.openclaw/workspace-investment-officer/reports/YYYY-MM-DD-portfolio-ops.pdf",
    message="摘要文字"
)
```

---

## 常见错误与修复

| 错误 | 原因 | 修复 |
|------|------|------|
| 部分股票未出现在PDF | 记忆文件提取时漏行 | 回看截图原图，补充漏掉的行 |
| 成本价显示异常高 | 反向拆股导致 | 备注说明，不作为止损参考 |
| PDF乱码/方块 | wkhtmltopdf不支持emoji | 始终用Chrome headless |
| Chrome超时 | HTML过大或网络问题 | 拆分HTML或增加超时时间 |

---

## 文件路径约定

```
workspace/
├── memory/YYYY-MM-DD.md        # 持仓快照（每日）
├── reports/YYYY-MM-DD-portfolio-ops.pdf  # 操作建议PDF
└── skills/portfolio-ops/
    ├── scripts/portfolio-validate.py     # 完整性校验
    ├── scripts/generate-portfolio-pdf.py # PDF生成辅助
    ├── references/memory-format.md       # 记忆文件格式规范
    ├── references/analysis-framework.md  # 分析框架
    └── assets/pdf-template.html          # HTML样式模板
```

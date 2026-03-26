# HEARTBEAT.md - 投资官定时任务

## 美股收盘复盘（周二至周六 05:00）
- 获取美股主要指数数据（标普500、纳指、道指）
- 分析热门科技股表现
- 分析中概股表现
- 生成复盘报告
- **调用skill上传报告到GitHub并通知老板**
  ```bash
  ~/.openclaw/workspace-investment-officer/skills/investment-report-publisher/publish-report.sh $(date +%Y-%m-%d) "$报告内容"
  ```

## 早盘简报（工作日 9:00）
- 生成美股/港股/A股市场开盘简报
- 分析主要指数走势
- 发送给老板

## 收盘总结（工作日 16:00）
- 生成当日收盘总结报告
- 分析涨跌幅、成交量
- 发送给老板

## 美股盘前（工作日 21:00）
- 扫描美股盘前动态
- 分析中概股表现
- 发送给老板

## 数据质量检查
- 验证数据源可用性
- 检查分析结论一致性
- 标注置信度（高/中/低）

## 报告发布Skill使用说明

### Skill路径
`~/.openclaw/workspace-investment-officer/skills/investment-report-publisher/`

### 使用方法
生成报告后，调用以下命令自动完成后续流程：
```bash
# 方式1：直接传入报告内容
~/.openclaw/workspace-investment-officer/skills/investment-report-publisher/publish-report.sh 2026-03-26 "<h2>报告内容...</h2>"

# 方式2：从文件读取
~/.openclaw/workspace-investment-officer/skills/investment-report-publisher/publish-report.sh 2026-03-26 /path/to/report.html
```

### 自动完成
1. ✅ 生成PDF（带样式）
2. ✅ 上传到GitHub（hahalong/investment-reports）
3. ✅ 飞书通知老板

### GitHub仓库
https://github.com/hahalong/investment-reports

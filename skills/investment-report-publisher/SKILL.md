# Investment Report Publisher Skill

## 功能
将投资官的美股复盘报告自动生成PDF，上传GitHub，并通知老板。

## 使用方式

### 方式1：在投资官cron任务中调用（推荐）

修改投资官的cron任务配置，在生成报告后调用：

```bash
# 在 investment-officer 的 cron 任务脚本末尾添加：
~/.openclaw/workspace/skills/investment-report-publisher/publish-report.sh $(date +%Y-%m-%d) "$(cat /tmp/investment_report.html)"
```

### 方式2：手动执行

```bash
cd ~/.openclaw/workspace/skills/investment-report-publisher

# 使用示例数据测试
./publish-report.sh

# 指定日期和报告内容
./publish-report.sh 2026-03-26 "<h2>报告内容</h2><p>...</p>"

# 从文件读取报告内容
./publish-report.sh 2026-03-26 /path/to/report.html
```

## 工作流程

1. **获取报告内容** - 从参数或文件读取投资官生成的HTML报告
2. **生成PDF** - 使用wkhtmltopdf转换为PDF（带样式）
3. **上传GitHub** - 推送到 hahalong/investment-reports 仓库
4. **通知老板** - 通过飞书发送报告链接

## 依赖安装

```bash
# 安装wkhtmltopdf
sudo apt-get update
sudo apt-get install -y wkhtmltopdf

# 配置GitHub访问（需要设置GITHUB_TOKEN环境变量）
export GITHUB_TOKEN="your_github_token"
```

## 配置说明

| 配置项 | 默认值 | 说明 |
|:---|:---|:---|
| REPO_DIR | `~/investment-reports` | 本地仓库路径 |
| GITHUB_REPO | `hahalong/investment-reports` | GitHub仓库 |
| REPORT_DATE | 当天日期 | 报告日期 |

## 输出示例

```
========================================
投资报告发布系统
日期: 2026-03-26
========================================
[1/5] 检查依赖...
✅ wkhtmltopdf 已安装
[2/5] 获取报告内容...
使用示例数据（测试模式）
[3/5] 生成HTML报告...
✅ HTML报告已生成: report-2026-03-26.html
[4/5] 生成PDF...
✅ PDF已生成: report-2026-03-26.pdf
[5/5] 上传到GitHub...
✅ 已上传到GitHub
========================================
✅ 报告发布完成！
日期: 2026-03-26
PDF文件: report-2026-03-26.pdf (45K)
GitHub链接: https://github.com/hahalong/investment-reports/blob/main/report-2026-03-26.pdf
========================================
```

## 与OpenClaw集成

在OpenClaw中调用此skill：

```json
{
  "skill": "investment-report-publisher",
  "action": "publish",
  "params": {
    "date": "2026-03-26",
    "content": "<h2>美股复盘报告</h2>...",
    "notify": {
      "channel": "feishu",
      "target": "ou_97758f3e96bdd4ae6962c805c5e62676"
    }
  }
}
```

## 测试状态

- [x] HTML生成测试通过
- [x] PDF生成测试通过（45KB）
- [ ] GitHub推送（需要配置GITHUB_TOKEN）
- [ ] 飞书通知集成

## 待办

1. 配置GITHUB_TOKEN环境变量
2. 集成飞书通知功能
3. 对接投资官实际数据输出

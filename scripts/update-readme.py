#!/usr/bin/env python3
"""
更新 GitHub investment-reports 仓库的 README.md
在"最新报告"表格顶部插入新行

用法：python3 update-readme.py <文件名> <报告标题> <说明> <日期>
"""
import sys, json, base64, urllib.request, urllib.error
from pathlib import Path

WORKSPACE = Path("/home/ecs-user/.openclaw/workspace-investment-officer")

def load_config():
    env_path = WORKSPACE / ".openclaw/github.env"
    config = {}
    for line in env_path.read_text().splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            config[k.strip()] = v.strip()
    return config

def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def api_put(url, token, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def main():
    if len(sys.argv) < 4:
        print("用法：python3 update-readme.py <文件名> <报告标题> <说明> [日期]")
        sys.exit(1)

    file_name = sys.argv[1]
    title = sys.argv[2]
    desc = sys.argv[3] if len(sys.argv) > 3 else ""
    date = sys.argv[4] if len(sys.argv) > 4 else __import__('datetime').date.today().isoformat()

    config = load_config()
    token = config['GITHUB_TOKEN']
    user = config['GITHUB_USER']
    repo = "investment-reports"

    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/README.md"
    result = api_get(api_url, token)
    sha = result['sha']
    current = base64.b64decode(result['content']).decode('utf-8')

    # 构造新行（同时支持PDF和HTML）
    base = file_name.replace('.pdf', '').replace('.html', '')
    has_html = (WORKSPACE / "reports" / f"{base}.html").exists()
    
    if has_html:
        file_link = f"[PDF](reports/{base}.pdf) \\| [HTML](reports/{base}.html)"
    else:
        file_link = f"[PDF](reports/{file_name})"
    
    new_row = f"| {date} | **{title}** | {file_link} | {desc} |"

    # 在表格header后插入新行
    header = "| 日期 | 报告名称 | 文件 | 说明 |"
    separator = "|:---|:---|:---|:---|"
    
    if header in current and separator in current:
        insert_after = separator
        new_content = current.replace(
            insert_after,
            insert_after + "\n" + new_row
        )
    else:
        # 如果表格格式不对，在最新报告section后追加
        new_content = current.replace(
            "## 📊 最新报告\n",
            f"## 📊 最新报告\n\n| 日期 | 报告名称 | 文件 | 说明 |\n|:---|:---|:---|:---|\n{new_row}\n"
        )

    # 更新最后更新时间
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    new_content = new_content.replace(
        new_content[new_content.rfind('*最后更新：'):new_content.rfind('*最后更新：')+20] 
        if '*最后更新：' in new_content else '',
        f'*最后更新：{now}*'
    ) if '*最后更新：' in new_content else new_content

    content_b64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    result = api_put(api_url, token, {
        "message": f"📋 README更新：新增 {title} ({date})",
        "content": content_b64,
        "sha": sha
    })
    print(f"✅ README更新成功: {result['commit']['sha'][:8]}")

if __name__ == "__main__":
    main()

# Ideas MCP Server - OpenCode Configuration

## 已完成的配置

Ideas MCP Server 已添加到 OpenCode 配置中！

### 配置位置

文件: `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "browsermcp": {
      "args": ["@browsermcp/mcp@latest"],
      "command": "npx"
    },
    "ideas": {
      "args": ["-m", "ideas_mcp.server"],
      "command": "/Users/maxazure/projects/ideas/mcp-server/venv/bin/python"
    }
  }
}
```

### 重启 OpenCode

添加配置后，**重启 OpenCode** 即可使用。

## 可用的 MCP 工具

在 OpenCode 中，你可以直接对 Claude 说：

### Idea Management
```
创建一个新想法：学习 Python 异步编程
列出所有待办的想法
查看想法 #1 的详情
更新想法 #1 的内容为新描述
执行想法 #1
取消想法 #1 的执行
给想法 #1 添加消息：这是用户的补充说明
```

### Agent Execution
```
轮询待处理的ideas
领取想法 #1
开始执行想法 #1
给想法 #1 提交反馈：已完成 50%
向想法 #1 提问：应该使用哪种方案？
完成想法 #1，附上总结
标记想法 #1 为失败，原因为：无法继续
```

## 手动安装步骤

如果你需要重新配置：

### 1. 编辑 settings.json

```bash
nano ~/.claude/settings.json
```

在 `mcpServers` 部分添加：

```json
"ideas": {
  "args": ["-m", "ideas_mcp.server"],
  "command": "/Users/maxazure/projects/ideas/mcp-server/venv/bin/python"
}
```

### 2. 验证配置

```bash
source /Users/maxazure/projects/ideas/mcp-server/venv/bin/activate
python -c "from ideas_mcp.server import mcp; print(f'Server: {mcp.name}')"
```

### 3. 重启 OpenCode

完全退出并重新启动 OpenCode。

## API 地址

MCP 服务器连接到的 API: `https://ideas.u.jayliu.co.nz`

## 问题排查

1. **MCP 工具不可用**
   - 确认 venv 路径正确
   - 重启 OpenCode

2. **API 连接失败**
   - 检查网络连接
   - 确认 API 服务正常运行: `curl https://ideas.u.jayliu.co.nz/health`

3. **权限错误**
   - 确保 settings.json 格式正确
   - JSON 格式验证: `python -c "import json; json.load(open('~/.claude/settings.json'))"`

# TODO 任务列表

## ✅ 已完成
- [x] 创建项目结构和虚拟环境 - 完成时间: 2026-01-07
- [x] 创建开发计划文档 docs/dev_plan.md - 完成时间: 2026-01-07
- [x] 创建数据库模型（Idea, Message） - 完成时间: 2026-01-07
- [x] 编写模型单元测试（4个测试） - 完成时间: 2026-01-07
- [x] 创建 API 端点（想法管理） - 完成时间: 2026-01-07
- [x] 编写 API 单元测试（17个测试） - 完成时间: 2026-01-07
- [x] 实现 Agent 处理机制 API - 完成时间: 2026-01-07
- [x] 实现等待用户指示机制 - 完成时间: 2026-01-07
- [x] 运行所有测试确保通过（21个测试全部通过） - 完成时间: 2026-01-07
- [x] 功能验收测试（手动 curl 测试完整流程） - 完成时间: 2026-01-07
- [x] 部署到生产服务器 - 完成时间: 2026-01-07
  - 服务器: maxazure@192.168.31.205
  - 服务: systemd ideas.service
  - 端口: 8100 (内部)
- [x] 配置 https 证书 - 完成时间: 2026-01-07
  - 域名: ideas.u.jayliu.co.nz
  - 证书: Let's Encrypt (自动续期)
- [x] 添加 API 认证机制 - 完成时间: 2026-01-07
  - 可选 API Key 认证
  - 通过环境变量 API_KEY 和 API_KEY_ENABLED 配置

## 💡 优化建议 (未来可选)
- [ ] 添加分页支持 - 提出时间: 2026-01-07
- [ ] 添加搜索功能 - 提出时间: 2026-01-07
- [ ] 添加 WebSocket 实时推送 - 提出时间: 2026-01-07

## 📚 使用说明

### 生产环境
- API 地址: https://ideas.u.jayliu.co.nz
- API 文档: https://ideas.u.jayliu.co.nz/docs

### 本地开发
```bash
cd ~/projects/ideas
source venv/bin/activate
PYTHONPATH=src pytest tests/ -v  # 运行测试
PYTHONPATH=src uvicorn ideas.main:app --reload  # 启动开发服务器
```

### 生产服务管理
```bash
ssh maxazure@192.168.31.205
sudo systemctl status ideas
sudo systemctl restart ideas
```

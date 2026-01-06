# Idea Execution Loop System - Development Plan

## 技术架构

### 技术栈
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy (async)
- **Python版本**: 3.13.2

### 项目结构
```
ideas/
├── src/ideas/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── models.py        # SQLAlchemy 模型
│   ├── schemas.py       # Pydantic 模式
│   └── routers/
│       ├── __init__.py
│       ├── ideas.py     # 想法管理 API
│       └── agent.py     # Agent 处理 API
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # 测试配置
│   ├── test_models.py   # 模型测试
│   └── test_api.py      # API 测试
├── docs/
│   └── dev_plan.md      # 开发计划
└── requirements.txt
```

## 数据模型

### Idea (想法)
- id: 主键
- content: 想法内容
- status: 状态枚举
- created_at: 创建时间
- updated_at: 更新时间

### Message (消息/事件)
- id: 主键
- idea_id: 关联想法
- type: 消息类型 (user_input, agent_feedback, system_event)
- content: 消息内容
- created_at: 创建时间

## 状态机

### 状态定义
- draft: 草稿（仅记录）
- pending: 待执行
- claimed: 已被 Agent 领取
- executing: 执行中
- waiting_user: 等待用户指示
- waiting_agent: 等待 Agent 继续
- completed: 已完成
- failed: 已失败
- cancelled: 已取消

### 状态流转
1. draft → pending (用户选择立刻执行)
2. pending → claimed (Agent 领取)
3. claimed → executing (Agent 开始执行)
4. executing → waiting_user (Agent 请求用户指示)
5. waiting_user → waiting_agent (用户追加指示)
6. waiting_agent → executing (Agent 继续执行)
7. executing → completed/failed (任务结束)
8. 任意状态 → cancelled (用户取消)

## API 设计

### 想法管理
- POST /api/ideas - 创建想法
- GET /api/ideas - 获取所有想法
- GET /api/ideas/{id} - 获取单个想法
- PUT /api/ideas/{id} - 更新想法
- POST /api/ideas/{id}/execute - 立刻执行
- POST /api/ideas/{id}/cancel - 取消执行
- POST /api/ideas/{id}/messages - 追加消息
- GET /api/ideas/{id}/messages - 获取消息历史

### Agent API
- GET /api/agent/poll - 轮询可执行任务
- POST /api/agent/claim/{id} - 领取任务
- POST /api/agent/feedback/{id} - 提交反馈
- POST /api/agent/ask/{id} - 请求用户指示
- POST /api/agent/complete/{id} - 完成任务
- POST /api/agent/fail/{id} - 任务失败

## 开发阶段

### Phase 1: 基础架构 ✅
- [x] 项目结构
- [x] 虚拟环境
- [x] 依赖安装

### Phase 2: 数据模型 ✅
- [x] 数据库模型 (Idea, Message)
- [x] 模型测试 (4 tests)

### Phase 3: 想法管理 API ✅
- [x] CRUD API
- [x] 状态转换 API
- [x] API 测试 (7 tests)

### Phase 4: Agent API ✅
- [x] 轮询/领取
- [x] 反馈/完成
- [x] 多轮协作 (9 tests)

### Phase 5: 集成测试 ✅
- [x] 完整流程测试 (1 test)
- [x] 功能验收 (手动 curl 测试通过)

## 验收标准完成情况

根据 PRD 第 8 节定义的成功标准：

1. ✅ 用户可以把一个想法从"记录"推进到"完成"
2. ✅ Agent 可以安全、唯一地领取想法并执行
3. ✅ 用户与 Agent 可以围绕同一想法进行多轮交互
4. ✅ 执行过程与状态变化全部可追溯
5. ✅ 用户始终对执行节奏拥有最终控制权

## 运行指南

### 安装依赖
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 运行测试
```bash
PYTHONPATH=src pytest tests/ -v
```

### 启动服务器
```bash
PYTHONPATH=src uvicorn ideas.main:app --host 0.0.0.0 --port 8000
```

### API 文档
启动服务器后访问: http://localhost:8000/docs

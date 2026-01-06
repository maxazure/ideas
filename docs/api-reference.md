# Ideas API - MCP 工具开发文档

## 概述

想法执行闭环系统 API，用于 AI Agent 管理和执行用户的想法。

**Base URL**: `https://ideas.u.jayliu.co.nz`

## 状态枚举

### IdeaStatus (想法状态)
| 值 | 说明 |
|---|---|
| `draft` | 草稿，仅记录 |
| `pending` | 待执行，等待 Agent 领取 |
| `claimed` | 已被 Agent 领取 |
| `executing` | 执行中 |
| `waiting_user` | 等待用户指示 |
| `waiting_agent` | 等待 Agent 继续 |
| `completed` | 已完成 |
| `failed` | 已失败 |
| `cancelled` | 已取消 |

### MessageType (消息类型)
| 值 | 说明 |
|---|---|
| `user_input` | 用户输入 |
| `agent_feedback` | Agent 反馈 |
| `system_event` | 系统事件 |

---

## 想法管理 API

### 1. 创建想法

创建一个新想法，初始状态为 `draft`。

```
POST /api/ideas
```

**请求体**:
```json
{
  "content": "想法内容描述"
}
```

**响应** (201):
```json
{
  "id": 1,
  "content": "想法内容描述",
  "status": "draft",
  "agent_id": null,
  "created_at": "2026-01-07T09:00:00.000000",
  "updated_at": "2026-01-07T09:00:00.000000"
}
```

---

### 2. 获取想法列表

获取所有想法，可按状态筛选。

```
GET /api/ideas
GET /api/ideas?status_filter=pending
```

**查询参数**:
| 参数 | 类型 | 说明 |
|---|---|---|
| `status_filter` | string | 可选，按状态筛选 |

**响应** (200):
```json
[
  {
    "id": 1,
    "content": "想法内容",
    "status": "draft",
    "agent_id": null,
    "created_at": "2026-01-07T09:00:00.000000",
    "updated_at": "2026-01-07T09:00:00.000000"
  }
]
```

---

### 3. 获取单个想法（含消息历史）

获取想法详情及其完整消息线程。

```
GET /api/ideas/{idea_id}
```

**响应** (200):
```json
{
  "id": 1,
  "content": "想法内容",
  "status": "executing",
  "agent_id": "agent-001",
  "created_at": "2026-01-07T09:00:00.000000",
  "updated_at": "2026-01-07T09:05:00.000000",
  "messages": [
    {
      "id": 1,
      "idea_id": 1,
      "type": "system_event",
      "content": "Idea created",
      "created_at": "2026-01-07T09:00:00.000000"
    },
    {
      "id": 2,
      "idea_id": 1,
      "type": "agent_feedback",
      "content": "正在处理...",
      "created_at": "2026-01-07T09:05:00.000000"
    }
  ]
}
```

---

### 4. 更新想法

修改想法内容（不影响历史消息）。

```
PUT /api/ideas/{idea_id}
```

**请求体**:
```json
{
  "content": "更新后的想法内容"
}
```

**响应** (200): 返回更新后的想法对象

---

### 5. 立刻执行

将想法状态从 `draft` 改为 `pending`，使其可被 Agent 领取。

```
POST /api/ideas/{idea_id}/execute
```

**前提条件**: 想法状态必须为 `draft`

**响应** (200):
```json
{
  "id": 1,
  "old_status": "draft",
  "new_status": "pending",
  "message": "Idea marked for execution"
}
```

---

### 6. 取消执行

取消想法执行。

```
POST /api/ideas/{idea_id}/cancel
```

**前提条件**: 想法状态不能是 `completed`、`failed`、`cancelled`

**响应** (200):
```json
{
  "id": 1,
  "old_status": "executing",
  "new_status": "cancelled",
  "message": "Idea cancelled"
}
```

---

### 7. 添加用户消息

用户向想法线程追加消息/指示。

```
POST /api/ideas/{idea_id}/messages
```

**请求体**:
```json
{
  "content": "用户的补充说明或指示"
}
```

**特殊行为**: 如果想法状态为 `waiting_user`，会自动转为 `waiting_agent`

**响应** (201):
```json
{
  "id": 5,
  "idea_id": 1,
  "type": "user_input",
  "content": "用户的补充说明或指示",
  "created_at": "2026-01-07T09:10:00.000000"
}
```

---

### 8. 获取消息历史

获取想法的所有消息（按时间排序）。

```
GET /api/ideas/{idea_id}/messages
```

**响应** (200): 消息数组

---

## Agent API

### 1. 轮询可执行任务

获取所有可领取的任务（状态为 `pending` 或 `waiting_agent`）。

```
GET /api/agent/poll
```

**响应** (200):
```json
[
  {
    "id": 1,
    "content": "待执行的想法",
    "status": "pending",
    "agent_id": null,
    "created_at": "2026-01-07T09:00:00.000000",
    "updated_at": "2026-01-07T09:00:00.000000"
  }
]
```

---

### 2. 领取任务

Agent 领取一个待执行的想法。

```
POST /api/agent/claim/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id"
}
```

**前提条件**: 想法状态必须为 `pending`

**响应** (200):
```json
{
  "id": 1,
  "old_status": "pending",
  "new_status": "claimed",
  "message": "Task claimed by agent your-agent-id"
}
```

---

### 3. 开始执行

Agent 开始执行已领取的任务。

```
POST /api/agent/start/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id"
}
```

**前提条件**: 
- 想法状态必须为 `claimed` 或 `waiting_agent`
- 必须是领取该任务的 Agent

**响应** (200):
```json
{
  "id": 1,
  "old_status": "claimed",
  "new_status": "executing",
  "message": "Execution started"
}
```

---

### 4. 提交反馈

Agent 在执行过程中提交进度反馈。

```
POST /api/agent/feedback/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id",
  "content": "当前进度：已完成 50%..."
}
```

**前提条件**: 
- 想法状态必须为 `executing`
- 必须是领取该任务的 Agent

**响应** (200):
```json
{
  "id": 1,
  "old_status": "executing",
  "new_status": "executing",
  "message": "Feedback recorded"
}
```

---

### 5. 请求用户指示

Agent 遇到问题，需要用户提供指示。

```
POST /api/agent/ask/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id",
  "question": "需要用户决策的问题描述"
}
```

**前提条件**: 
- 想法状态必须为 `executing`
- 必须是领取该任务的 Agent

**响应** (200):
```json
{
  "id": 1,
  "old_status": "executing",
  "new_status": "waiting_user",
  "message": "Waiting for user instruction"
}
```

---

### 6. 完成任务

Agent 声明任务已完成。

```
POST /api/agent/complete/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id",
  "summary": "任务完成总结（可选）"
}
```

**前提条件**: 
- 想法状态必须为 `executing`
- 必须是领取该任务的 Agent

**响应** (200):
```json
{
  "id": 1,
  "old_status": "executing",
  "new_status": "completed",
  "message": "Task completed"
}
```

---

### 7. 任务失败

Agent 声明任务失败。

```
POST /api/agent/fail/{idea_id}
```

**请求体**:
```json
{
  "agent_id": "your-agent-id",
  "reason": "失败原因说明"
}
```

**前提条件**: 
- 想法状态必须为 `executing`
- 必须是领取该任务的 Agent

**响应** (200):
```json
{
  "id": 1,
  "old_status": "executing",
  "new_status": "failed",
  "message": "Task failed"
}
```

---

## 错误响应

所有 API 在出错时返回统一格式：

```json
{
  "detail": "错误描述"
}
```

常见 HTTP 状态码：
- `400` - 请求无效（如状态不允许的操作）
- `403` - 权限不足（如非授权 Agent）
- `404` - 资源不存在

---

## MCP 工具建议实现

基于此 API，建议实现以下 MCP 工具：

| 工具名 | 功能 | 对应 API |
|---|---|---|
| `idea_create` | 创建新想法 | POST /api/ideas |
| `idea_list` | 列出想法 | GET /api/ideas |
| `idea_get` | 获取想法详情 | GET /api/ideas/{id} |
| `idea_update` | 更新想法内容 | PUT /api/ideas/{id} |
| `idea_execute` | 标记立刻执行 | POST /api/ideas/{id}/execute |
| `idea_cancel` | 取消执行 | POST /api/ideas/{id}/cancel |
| `idea_reply` | 用户回复/追加指示 | POST /api/ideas/{id}/messages |
| `agent_poll` | 轮询待处理任务 | GET /api/agent/poll |
| `agent_claim` | 领取任务 | POST /api/agent/claim/{id} |
| `agent_start` | 开始执行 | POST /api/agent/start/{id} |
| `agent_feedback` | 提交进度反馈 | POST /api/agent/feedback/{id} |
| `agent_ask` | 请求用户指示 | POST /api/agent/ask/{id} |
| `agent_complete` | 完成任务 | POST /api/agent/complete/{id} |
| `agent_fail` | 标记失败 | POST /api/agent/fail/{id} |

---

## 典型工作流程

```
1. 用户创建想法 → POST /api/ideas
2. 用户标记执行 → POST /api/ideas/{id}/execute
3. Agent 轮询任务 → GET /api/agent/poll
4. Agent 领取任务 → POST /api/agent/claim/{id}
5. Agent 开始执行 → POST /api/agent/start/{id}
6. Agent 提交反馈 → POST /api/agent/feedback/{id}
7. (可选) Agent 请求指示 → POST /api/agent/ask/{id}
8. (可选) 用户回复 → POST /api/ideas/{id}/messages
9. (可选) Agent 继续 → POST /api/agent/start/{id}
10. Agent 完成/失败 → POST /api/agent/complete/{id} 或 fail/{id}
```

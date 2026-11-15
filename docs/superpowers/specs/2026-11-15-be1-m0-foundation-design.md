# BE1 M0 平台基础设计

| 项目项 | 内容 |
|---|---|
| 状态 | 已确认 |
| 日期 | 2026-11-15 |
| 负责人 | BE1 |
| 范围 | T01、T02、T03 |
| 上游文档 | `Requirements.md` v1.1、`Design.md` v1.1、`tasks.md` v1.0 |

## 1. 目标

本设计只覆盖 BE1 的首批 P0 任务：

1. T01：建立可安装、可启动、可测试的 Python/FastAPI 与 React/Vite/TypeScript 项目骨架。
2. T02：建立 BE1 负责的 HTTP、Pydantic、错误、分页和 SSE 核心契约，并导出 OpenAPI。
3. T03：建立 SQLAlchemy 2 数据模型、SQLite 运行配置和 Alembic 初始迁移。

T08、T11、T13、T15 及后续 BE1 任务不在本轮实现。本轮可以提供后续任务依赖的基础设施，但不提前实现上传、任务业务服务或 SSE 传输。

## 2. 方案选择

采用单一 Python 项目结构：

- 根目录 `pyproject.toml` 管理 Python 依赖与质量工具。
- `backend/app` 作为可安装的 `app` 包，使根目录能执行 `uv run uvicorn app.api.main:app`。
- `backend/migrations` 由 Alembic 管理。
- `backend/tests` 保存后端测试。
- `frontend` 保存最小 React/Vite/TypeScript 包骨架，供 FE1 后续接管页面实现。

未采用独立 `backend/pyproject.toml`，因为设计要求统一从仓库根目录运行 Python 命令。未采用纯占位目录，因为 T01 要求应用可启动，T02/T03 还要求契约与迁移可验证。

## 3. 仓库与启动骨架

根目录提供：

```text
pyproject.toml
uv.lock
.env.example
.gitignore
backend/
  app/
    api/
    application/
    infrastructure/
    worker/
  migrations/
  tests/
frontend/
scripts/
  contracts/
data/
docs/
```

具体约束：

1. Python 固定为 `>=3.11,<3.12`。
2. 运行时依赖包含 FastAPI、Uvicorn、Pydantic 2、SQLAlchemy 2、Alembic。
3. 开发依赖包含 Pytest、HTTPX、Ruff、Pyright。
4. `app` 包由根 `pyproject.toml` 安装，源码位于 `backend/app`。
5. `data` 只保留目录占位，数据库、日志和任务文件均被 Git 忽略。
6. `.env.example` 记录 `DOC_AGENT_DATA_DIR` 等后续运行配置，不包含密钥。
7. 最小前端提供 React、TypeScript、Vite 依赖和构建脚本，不实现页面业务。

## 4. API 与 Pydantic 契约

### 4.1 通用约定

- API 基础路径为 `/api/v1`。
- 所有 ID 使用 UUID 字符串。
- 所有时间使用带 UTC 时区的 ISO 8601 值。
- 列表使用游标分页，不使用无上限全量接口。
- 错误响应严格包含 `code`、`message`、`details`、`request_id`。
- Pydantic 模型启用严格枚举、禁止未知请求字段和显式白名单序列化。

### 4.2 核心类型

本轮定义：

1. 任务、轮次、Job、依赖、上传、产物、结果组、事件、严重度和消息角色枚举。
2. `ErrorCode` 覆盖 `Design.md` 第 9.9 节列出的全部稳定错误码。
3. `ErrorResponse`、`AppError` 和统一的 FastAPI 异常处理。
4. 泛型 `CursorPage[T]`，包含 `items`、`next_cursor`、`has_more`。
5. 上传、任务摘要、任务详情、轮次、Job、结果组和文件角色 DTO 的核心字段。
6. 创建任务、新增轮次和基础读取请求模型。

### 4.3 SSE 契约

SSE 事件模型采用以 `type` 为判别字段的 Pydantic 判别联合，覆盖：

`task.queued`、`task.started`、`plan.created`、`clarification.required`、`job.waiting`、`job.status`、`job.blocked`、`template.diagnosed`、`conversion.started`、`conversion.finished`、`tool.started`、`tool.finished`、`validation.finished`、`artifact.ready`、`turn.finished`、`task.finished`、`heartbeat`。

每个事件包含 `seq`、`type`、`task_id`、`turn_id`、`job_id`、`timestamp` 和事件专用 `data`。本轮只建立契约，不实现 T15 的持久化回放或流式响应。

### 4.4 FastAPI 应用

本轮应用至少提供：

1. `GET /health`：返回应用和数据库基础可用状态。Office 深度检查留给 T08。
2. `GET /api/v1/openapi.json`：返回当前应用 OpenAPI 文档。
3. 统一异常响应，并确保 `request_id` 存在。

OpenAPI 导出脚本写入固定路径，生成结果纳入版本控制；重复执行不得产生差异。

## 5. 数据库设计

### 5.1 技术约束

- SQLAlchemy 2 使用声明式映射和类型标注。
- SQLite 通过 SQLAlchemy 事件在每个连接上执行：
  - `PRAGMA journal_mode = WAL`
  - `PRAGMA foreign_keys = ON`
  - `PRAGMA busy_timeout = 5000`
  - `PRAGMA synchronous = NORMAL`
- 主键使用 TEXT UUID，时间使用 UTC DATETIME，结构化数据使用 JSON。
- 所有 schema 变化通过 Alembic，不使用运行时 `create_all` 代替迁移。
- 业务外键默认 `ON DELETE CASCADE`。

### 5.2 表范围

初始迁移覆盖 `Design.md` 第 10.2-10.18 节的全部表：

- `tasks`
- `task_turns`
- `messages`
- `uploads`
- `uploaded_files`
- `jobs`
- `job_inputs`
- `job_dependencies`
- `job_attempts`
- `template_inspections`
- `result_groups`
- `artifacts`
- `document_snapshots`
- `content_chunks`
- `clarifications`
- `execution_events`
- `tool_invocations`
- `validation_results`
- `model_invocations`
- `idempotency_keys`

同时创建 `content_chunks_fts` 外部内容表及同步触发器。FTS 写入和检索服务不在本轮实现，但 schema 必须为后续读取能力保留。

### 5.3 关键约束与索引

1. `task_turns(task_id, sequence)` 唯一。
2. 非空 `jobs(turn_id, artifact_slot)` 使用部分唯一索引。
3. `job_inputs(job_id, input_kind, input_id)` 唯一。
4. `job_dependencies` 主键为 `(job_id, depends_on_job_id)`。
5. `result_groups(job_id)` 唯一。
6. `execution_events(task_id, id)` 建立查询索引。
7. 按设计建立任务状态/更新时间、Job 状态/依赖状态、产物任务/类型/状态等查询索引。
8. `document_snapshots` 的 `artifact_id` 与 `uploaded_file_id` 必须恰好一个非空。
9. `idempotency_keys` 保存 Key 哈希、作用域、请求哈希、资源 ID 和过期时间。

## 6. 测试策略

实现遵循测试先行：

1. 契约测试：
   - 错误结构字段完整。
   - UUID、UTC 时间、分页和枚举序列化。
   - SSE 判别联合可解析全部事件类型。
   - OpenAPI 端点包含核心 schema。
2. 迁移测试：
   - 空 SQLite 数据库执行 `alembic upgrade head` 成功。
   - 目标表、唯一索引、部分唯一索引和外键存在。
   - 级联删除生效。
   - FTS5 表和触发器可创建。
3. 数据库运行测试：
   - 连接后 WAL、foreign keys、busy timeout 和 synchronous 生效。
   - 从空路径创建数据库时不依赖仓库内已提交数据库文件。
4. 应用测试：
   - FastAPI 应用可导入并通过健康检查。
   - 错误处理器返回统一错误结构和 `request_id`。
5. 静态检查：
   - `uv run ruff check .`
   - `uv run pyright backend`
   - `uv run pytest`
   - `pnpm --dir frontend typecheck`
   - `pnpm --dir frontend build`
   - `uv run alembic upgrade head`

## 7. Git 工作流

采用 GitHub Flow：

1. 从 `master` 创建 `feat/be1-m0-foundation`。
2. 按 T01、T02、T03 分成独立、可测试的提交。
3. 推送功能分支。
4. 创建面向 `master` 的 Pull Request，等待评审后合并。
5. 不直接向 `master` 推送实现提交。

## 8. 完成标准

以下条件同时满足时，本轮完成：

- 根目录执行 `uv sync` 成功。
- `uv run uvicorn app.api.main:app` 可以启动。
- `pnpm --dir frontend install` 和 `pnpm --dir frontend build` 成功。
- Pydantic 核心 DTO、错误码和 SSE 判别联合有契约测试。
- OpenAPI 可从应用和导出脚本稳定生成。
- Alembic 能从空库升级到 head。
- SQLite WAL、外键、索引和级联删除有自动化测试。
- 所有声明的质量命令通过。
- 功能分支已推送，并创建面向 `master` 的 PR。

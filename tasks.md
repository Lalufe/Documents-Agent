# 多格式文档处理与办公 Agent 任务分解

| 项目项 | 内容 |
|---|---|
| 文档版本 | 1.0 |
| 日期 | 2026-11-15 |
| 上游文档 | `Requirements.md` v1.1、`Design.md` v1.1 |
| 团队规模 | 前端 4 人、后端 4 人、数据与联调 3 人 |
| 排期方式 | 按阶段门禁推进，不绑定固定日期 |
| 任务优先级 | P0 必须完成；P1 在 P0 稳定后完成；P2 仅在不影响验收时安排 |

## 1. 目标与使用方式

本文件把需求和设计拆成 11 人可并行执行的实施单元。每个任务必须有唯一负责人、明确前置依赖、可检查交付物和验收口径。`tasks.md` 是项目管理基线，产品范围仍以 `Requirements.md` 为准，技术方案仍以 `Design.md` 为准。

执行规则如下：

1. 每个任务开始前先确认依赖已完成，不在依赖未稳定时并行写同名契约。
2. 每个实现任务先补测试或验收样例，再完成实现；完成后至少运行该任务声明的质量命令。
3. 任务只有在交付物可运行、测试可重复、文档或契约已同步时才标记完成。
4. 发现需求或设计需要变更时，先更新对应文档和任务依赖，不在代码中静默改契约。
5. 任何任务都不得突破 `Design.md` 第 20.1 节列出的 MVP 约束。

## 2. 团队角色与职责

### 2.1 人员编号

| 编号 | 角色 | 主责任务 | 主要文件边界 |
|---|---|---|---|
| FE1 | 前端基础设施与工作台 | 应用外壳、路由、任务列表、状态层骨架、响应式外壳 | `frontend/src/app/`、`frontend/src/components/layout/`、`frontend/src/features/tasks/` |
| FE2 | 上传与任务创建 | 上传、预检展示、文件角色、任务创建、多轮基准选择 | `frontend/src/features/uploads/`、`frontend/src/features/task-create/` |
| FE3 | 对话、DAG 与 SSE | SSE 客户端、Query 缓存、对话、Job DAG、澄清、错误诊断 | `frontend/src/features/conversation/`、`frontend/src/features/jobs/`、`frontend/src/features/clarifications/`、`frontend/src/lib/sse/` |
| FE4 | 预览、结果与视觉质量 | 文档/表格/文本/图片预览、结果、血缘、下载、主题、视觉验收 | `frontend/src/features/preview/`、`frontend/src/features/results/`、`frontend/src/styles/` |
| BE1 | 平台、API 与持久化 | 脚手架、数据库、上传与任务 API、SSE 服务端、下载删除、本地安全 | `backend/app/api/`、`backend/app/application/`、`backend/app/infrastructure/db/`、`backend/migrations/` |
| BE2 | Agent、Worker 与调度 | 意图、歧义门禁、Plan Compiler、Job DAG、Worker、租约、恢复 | `backend/app/agent/`、`backend/app/scheduling/`、`backend/app/worker/` |
| BE3 | Office、PDF 与渲染 | Word/Excel/PPT/PDF 适配器、Office COM Gate、页面渲染与预览产物 | `backend/app/documents/word/`、`backend/app/documents/excel/`、`backend/app/documents/ppt/`、`backend/app/documents/pdf/`、`backend/app/infrastructure/office/` |
| BE4 | 文本、转换、模板、生成与验证 | CSV/MD/TXT/图片、转换注册表、模板、生成、验证与修复流水线 | `backend/app/documents/text/`、`backend/app/documents/tables/`、`backend/app/documents/images/`、`backend/app/conversion/`、`backend/app/templates/`、`backend/app/generation/`、`backend/app/validation/` |
| DI1 | 数据与评测资产 | 文档夹具、预期结果、固定哈希、转换样例、评测集与演示数据 | `tests/fixtures/`、`data/eval/`、`scripts/fixtures/` |
| DI2 | 契约、模型适配与集成 | OpenAPI 类型生成、假模型、Provider 适配、集成测试框架、故障注入 | `scripts/contracts/`、`backend/app/infrastructure/model_gateway/` 的适配测试、`backend/tests/integration/` |
| DI3 | 端到端、安全、性能与发布 | Playwright、验收追踪、安全与性能测试、启动器验收、答辩演示脚本 | `tests/e2e/`、`scripts/qa/`、`scripts/release/`、`docs/acceptance/` |

### 2.2 协作边界

- BE1 是 HTTP、Pydantic、OpenAPI 和数据库迁移的唯一契约负责人。
- BE2 是 Agent 状态、Job DAG、SSE 领域事件语义和 Worker 状态机的唯一负责人。
- BE3 与 BE4 只能通过 Tool Registry 暴露能力，不直接让模型选择内部函数或文件路径。
- FE3 只消费后端生成的 TypeScript 契约，不手写第二套状态枚举。
- FE4 不自行拼装下载路径，只使用 artifact ID、result group ID 和后端预览清单。
- DI1 负责样例事实与预期值，业务实现人员不得为通过测试而修改固定样例。
- DI2 负责契约差异检测和真实模型适配，业务模块不得直接依赖供应商 SDK。
- DI3 的 E2E 用例是发布门禁，不因功能“本地手测可用”而豁免。

### 2.3 决策与评审

| 事项 | 最终决策人 | 必须评审 |
|---|---|---|
| HTTP、SSE、数据库契约 | BE1 | BE2、FE3、DI2 |
| Job DAG、状态机、失败传播 | BE2 | BE1、BE4、FE3 |
| Office 渲染与预览 | BE3 | BE4、FE4、DI3 |
| 转换矩阵、模板语法、生成规格 | BE4 | BE2、DI1、DI3 |
| 数据集与预期结果 | DI1 | BE3、BE4、DI3 |
| 模型 Provider 与假模型 | DI2 | BE2、DI3 |
| 验收通过结论 | DI3 | 全体负责人 |

## 3. 阶段与门禁

| 阶段 | 目标 | 关键门禁 |
|---|---|---|
| M0 契约与骨架 | 所有模块可以启动、联调、测试和提交 | API 可读、前端可启动、Worker 可运行、CI 全绿 |
| M1 最小纵向切片 | 完成“上传 TXT/CSV 文件 -> 创建读取任务 -> SSE 进度 -> 预览/回答”的端到端链路 | 假模型下稳定通过，无真实外部服务依赖 |
| M2 核心文档能力 | Word、Excel、PPT、PDF 读取/编辑/渲染，图片与文本处理可调用 | AC-006 至 AC-011、AC-025 至 AC-027 的最小样例通过 |
| M3 高级工作流 | 转换矩阵、模板、从零生成、多 Job DAG、修复、多轮与历史 | AC-029 至 AC-039、AC-044 通过 |
| M4 集成硬化 | 安全、性能、恢复、响应式、全部转换对和错误路径 | 安全用例、性能目标、崩溃恢复、1280/1440/960/375 截图检查通过 |
| M5 发布验收 | 交付启动器、演示数据、验收记录和回归包 | `Requirements.md` P0 验收项全部有证据并可复现 |

每个阶段结束时由 DI3 汇总门禁证据。未达到门禁时，不把下一阶段任务全部启动，只允许与解除阻塞直接相关的任务继续。

## 4. 关键路径

```text
仓库骨架与质量门禁
  -> Pydantic/OpenAPI/数据库契约
  -> 最小上传与任务纵向切片
  -> Agent 意图与 Plan Compiler
  -> Job DAG Scheduler 与持久事件
  -> 文档工具与转换注册表
  -> 模板/生成/验证/修复
  -> 全量联调、安全、性能与发布验收
```

关键路径上的任务必须由主负责人持续跟进：`T01`、`T02`、`T03`、`T11`、`T13`、`T15`、`T17`、`T18`、`T19`、`T21`、`T31`、`T32`、`T34`、`T50`、`T59`、`T60`、`T64`、`T69`、`T90`。

## 5. M0：契约、环境与骨架

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T01 | P0 | BE1 | FE1、DI2 | 无 | 按 `Design.md` 4.4 创建 `backend/`、`frontend/`、`scripts/`、`data/` 目录和 Python/Node 包管理骨架 | `uv sync`、`pnpm install` 成功；目录边界与设计一致；空应用可启动 |
| T02 | P0 | BE1 | BE2、FE3、DI2 | T01 | 建立 Pydantic 核心 DTO、统一错误结构、分页、ID 与时间约定，导出 `/api/v1/openapi.json` | OpenAPI 文件可生成；核心 DTO 有契约测试；错误至少覆盖 `Design.md` 9.9 的 P0 错误码 |
| T03 | P0 | BE1 | BE2、DI2 | T02 | 建立 SQLAlchemy 2 + Alembic 初始迁移，覆盖任务、轮次、上传、Job、依赖、产物、事件与幂等表 | 从空库执行 `alembic upgrade head` 成功；外键、索引和 WAL 配置有 Repository 测试 |
| T04 | P0 | DI2 | BE1、FE3 | T02 | 用 `openapi-typescript` 生成前端类型和 SSE 判别联合，建立契约差异检查 | 生成文件可提交；后端 DTO 变化未重新生成时 CI 失败；前端不手写重复枚举 |
| T05 | P0 | FE1 | FE4 | T01 | 建立 React/Vite 路由、三栏应用外壳、Ant Design 主题、TanStack Query 与 Zustand 骨架 | `/tasks`、`/tasks/:taskId`、`/privacy` 可访问；1280px 下三栏结构正确；无负字距和视口缩放字体 |
| T06 | P0 | DI1 | BE3、BE4 | T01 | 建立夹具目录、命名规范、固定哈希清单和最小 TXT/CSV/DOCX/XLSX/PPTX/PDF/PNG 样例 | 每个样例有格式、来源、规模、预期定位和 SHA-256；测试不访问网络 |
| T07 | P0 | DI2 | BE1、FE1、DI3 | T01、T04 | 建立 CI：Python lint/type/test、TypeScript type/lint/test、前端 build、OpenAPI 差异检查 | 任意推送可执行；失败阻断合并；本地提供等价命令 |
| T08 | P0 | BE1 | BE4、DI3 | T03 | 建立配置、数据根目录、启动时迁移检查、路径守卫和健康检查 | `DOC_AGENT_DATA_DIR` 生效；路径穿越被拒绝；`/health` 返回数据库、配置、Office 状态 |
| T09 | P0 | BE1 | BE2、DI3 | T01 | 建立结构化 JSON 日志、请求 ID、任务/Job 字段和敏感信息脱敏 | 日志无正文、密钥、Cookie 和绝对路径；错误响应含 `request_id` |
| T10 | P0 | DI2 | BE2、BE3、BE4 | T02 | 建立 Fake Model Gateway、固定时钟、故障注入开关和测试用 Worker 驱动 | 测试可在无网络下执行 understand、plan、vision；可注入超时、429、Schema 错误 |

## 6. M1：最小纵向切片

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T11 | P0 | BE1 | BE3、BE4、FE2 | T03、T08 | 实现 `POST/GET/DELETE /uploads`、流式暂存、SHA-256、浅层校验和预检状态 | 支持单文件上传和删除；扩展名/MIME/魔数不一致被拒绝；未消费上传可过期 |
| T12 | P0 | FE2 | FE1、FE3 | T05、T11、T04 | 实现 `FileDock`、拖放/选择、预检状态、移除文件和候选角色展示 | 0 至 10 个文件可见；失败文件不能提交；文件大小、格式和状态不溢出容器 |
| T13 | P0 | BE1 | BE2、DI2 | T02、T03 | 实现 `POST/GET /tasks`、`GET /tasks/{id}` 和创建轮次 API 骨架，返回任务详情与空 DAG | `202 Accepted`、游标分页、幂等键和错误结构符合契约；重启后任务仍可查询 |
| T14 | P0 | FE1 | FE2、FE3 | T05、T04 | 实现任务侧栏、任务创建入口、任务筛选、历史列表和空白工作台状态 | 与 URL 同步；创建后跳转任务页；任务状态同时以文字和图标显示；无卡片套卡片 |
| T15 | P0 | BE1 | BE2、FE3、DI2 | T03、T09、T13 | 实现 `execution_events` 写入、SSE 回放、实时订阅、心跳和游标校验 | 断线重连不丢事件；非法游标返回 `EVENT_CURSOR_INVALID`；15 秒心跳可观测 |
| T16 | P0 | FE3 | FE1、DI2 | T04、T05、T15 | 建立 SSE 客户端、事件去重、Query 缓存更新和任务详情恢复 | 重连后按事件 ID 去重；`task.finished` 刷新详情；顺序异常时重新拉取任务 |
| T17 | P0 | BE2 | BE1、DI2 | T10、T13 | 实现 intake、understand、文件角色和结构化 `Intent` 校验，先接 Fake Model Gateway | 清晰读取指令产出合法 Intent；文档文本不能改变系统指令；Schema 错误可诊断 |
| T18 | P0 | BE2 | BE1、T04 | T17 | 实现最小 Plan Compiler 与 DAG 校验：唯一 Job、悬空依赖、环、深度和产物槽冲突 | 合法计划可持久化；循环、深度超过 3、超过 20 个 Job 和重复产物槽被拒绝 |
| T19 | P0 | BE2 | BE1、DI2 | T03、T13、T18 | 实现 Worker 原子领取、租约、心跳、单 Worker 串行执行和过期租约恢复 | 同步领取任务时只有一次成功；中断任务进入 `interrupted`；不自动复用 staged 文件 |
| T20 | P0 | BE4 | BE3、DI1 | T06 | 实现文本解码、TXT/MD 读取定位和 CSV 方言解析基础层 | UTF-8/BOM/GB18030 样例可判定；非法字节不静默替换；CSV 引号、多行字段正确 |
| T21 | P0 | BE2 | BE1、BE4、FE3 | T15、T17、T18、T19、T20 | 打通单个读取 Job：解析 TXT/CSV/MD -> 产出回答/结构化结果 -> 写验证记录和事件 | M1 固定样例完成；消息含来源定位；无产物读取 Job 不创建伪文件 |
| T22 | P0 | BE3 | BE4、DI1 | T06 | 实现 PyMuPDF 电子 PDF 文本、页码、坐标和阅读顺序提取 | 电子 PDF 样例可读取并返回页码定位；原 PDF 哈希不变；只读能力边界可见 |
| T23 | P0 | FE3 | FE1、FE2 | T12、T14、T16、T21 | 实现中栏对话、指令输入 Dock、任务创建、消息和最小执行时间线 | 可提交自然语言指令；读取结果和 Job 状态实时出现；固定输入区不遮挡内容 |
| T24 | P0 | FE4 | FE3、BE1 | T04、T05 | 实现安全文本预览、CSV 只读表格预览和结果区骨架 | MD/HTML 白名单清洗；CSV 值不变成公式或链接；预览 API 只接受 UUID |
| T25 | P0 | DI3 | DI1、DI2 | T21、T23、T24 | 建立 M1 Playwright 主路径：上传 TXT/CSV、创建任务、等待 SSE、查看回答和预览 | 无网络、Fake Model 下稳定通过；失败截图和 trace 可归档 |

## 7. M2：核心文档能力

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T30 | P0 | BE3 | BE1、DI1 | T08、T22 | 实现 DOCX 读取、段落/表格/样式定位和内容哈希快照 | 中英文正文、页眉页脚、表格和目录定位正确；重新解析后哈希稳定 |
| T31 | P0 | BE3 | BE4、DI1 | T30 | 实现 `word.edit` 与 `word.format` 的 P0 操作：文字、段落、常用字体样式、对齐、行距和页边距 | AC-006 样例通过；未要求修改的对象保留或告警；输出为新文件 |
| T32 | P0 | BE3 | BE4、DI1 | T08、T30 | 实现 Office COM Gate、DOCX 渲染 PDF、PyMuPDF 页面图和 COM 超时清理 | 同一时间只运行一个 COM 子进程；超时终止进程；预览绑定产物哈希 |
| T33 | P0 | BE3 | BE4、DI1 | T30、T32 | 实现 XLSX 读取、工作表/区域定位、关键单元格和图表关系提取 | 多工作表、公式缓存、图表样例可识别；超过 10 万行被限制 |
| T34 | P0 | BE3 | BE4、DI1 | T33 | 实现 Excel 重算、关键单元格复查、图表引用检查和 `excel.transform` 基础操作 | 去重、空白清理、筛选、排序和汇总可复算；输出可重新打开 |
| T35 | P0 | BE3 | BE4、DI1 | T32、T33 | 实现 PPTX 读取、幻灯片/形状/备注定位和页面渲染 | 多版式、表格、备注可定位；SmartArt/动画无法确认时产生警告 |
| T36 | P0 | BE3 | BE4、DI1 | T35 | 实现 `ppt.edit`、`ppt.layout` 的 P0 操作：文字、图片位置、增删/重排、主题和对齐 | AC-008 样例通过；复杂对象保留或明确告警；输出为新文件 |
| T37 | P0 | BE4 | BE3、DI1 | T20 | 实现 Markdown AST 读取、块级编辑、安全序列化和 TXT 改写/拼接 | 未修改块不重排；源码位置稳定；输出编码和换行可验证 |
| T38 | P0 | BE4 | BE3、DI1 | T20 | 实现 CSV 去重、缺失值、空白清理、筛选、排序、分组统计和公式注入防护 | 统计规则、命中行数可复算；不可信公式值默认转义并告警 |
| T39 | P0 | BE4 | BE3、DI1 | T06 | 实现 Pillow 图片探测、受限解码、EXIF 方向、Alpha 和缩略图基础能力 | 超像素/边长/帧数图片被拒绝；方向一致；损坏流不崩溃 |
| T40 | P0 | BE3 | FE4、BE4、DI1 | T32、T35 | 实现预览清单和页面图片接口：Word/PPT/PDF 页面、Excel/CSV 表分页、图片缩略图 | 按需加载页面；缓存键含产物哈希；删除后 URL 不返回旧内容 |
| T41 | P0 | FE4 | FE3、BE3 | T24、T40 | 实现 `PageViewer`、`ThumbnailRail`、Excel/CSV 表格预览、图片缩略图和预览切换 | 1280px 下页码、预览和结果不重叠；预览接口错误有可见降级状态 |
| T42 | P0 | FE2 | FE3、BE1 | T12、T13 | 实现多轮基准选择：原件或最新已发布结果，提交前可改选 | 修改类请求缺少有效基准时不可提交；跨任务或 staged 产物被前端和后端同时拒绝 |
| T43 | P0 | BE1 | FE3、FE4、DI3 | T11、T13、T15 | 实现产物下载、结果组 ZIP、任务归档和删除任务/全部任务 | 下载头、ETag 和 manifest 正确；删除后数据库和文件均不可访问 |
| T44 | P0 | FE3 | FE2、FE4、BE1 | T16、T23、T42、T43 | 实现多轮对话、当前工作副本提示、结果卡片和任务级状态聚合展示 | 两轮修改可追踪；失败/阻塞/部分成功状态清楚；成功产物可下载 |
| T45 | P0 | DI1 | BE3、BE4 | T30、T33、T35、T37、T38、T39 | 补齐 Word、Excel、PPT、PDF、CSV、MD、TXT、图片固定夹具和预期结果 | 每类至少一个正常样例和一个风险样例；固定哈希、定位器和预期状态齐全 |
| T46 | P0 | DI2 | BE1、BE3、BE4 | T31、T34、T36、T37、T38、T39 | 建立文档工具集成测试矩阵和 Office smoke test | 每个 P0 工具至少成功、失败、路径拒绝三类断言；Windows Office smoke 可运行 |
| T47 | P0 | DI3 | FE4、DI1 | T41、T44 | 建立 M2 端到端用例：Word 样式、Excel 统计、PPT 样式、PDF 问答和图片转换 | AC-006 至 AC-011、AC-025 至 AC-027 的最小验收路径有证据 |

## 8. M3：转换、模板、生成与 Job DAG

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T50 | P0 | BE4 | BE3、DI1、DI2 | T22、T30、T33、T35、T37、T38、T39 | 实现版本化 Conversion Registry 和 `/capabilities/conversions` | 矩阵内组合可查询；矩阵外返回 `UNSUPPORTED_CONVERSION`；注册项含保真、输入规则和验证器 |
| T51 | P0 | BE4 | BE3、DI1 | T50 | 实现 CSV↔XLSX、TXT↔MD、DOCX/PPTX→TXT/MD 和文本/表格构建文档 | 每个转换生成新产物；损失项进入摘要；源文件哈希不变 |
| T52 | P0 | BE4 | BE3、DI1 | T50、T32 | 实现文档→PDF 转换路由、PDF 页面图片结果组和 PDF 只读限制 | DOCX/XLSX/PPTX→PDF 可执行；PDF→Office 明确拒绝；拆页结果有顺序 manifest |
| T53 | P0 | BE4 | BE3、DI1 | T50、T37、T38 | 实现 TXT/MD/CSV→DOCX/PPTX/PDF、多图片→PDF/DOCX/PPTX 和图片格式互转 | 标题/段落/表格映射、透明转 JPEG、超宽表格和多图顺序均有验证与警告 |
| T54 | P0 | BE4 | BE3、DI1 | T30、T33、T35 | 实现 DOCX/XLSX/PPTX 模板标记解析和 `TemplateManifest` | 命名值、重复区、可选区块、图片四类标记可定位；跨 run Word 标记可解析 |
| T55 | P0 | BE4 | BE3、DI1、FE3 | T54 | 实现模板诊断：未闭合、重复、冲突、缺数据、表达式/外部关系和不安全重复单位 | 诊断有稳定码、位置、严重度和建议；阻止级诊断不输出含标记文件 |
| T56 | P0 | BE4 | BE3、DI1 | T54、T55 | 实现模板字段映射与 `template.generate`：一个模板、零个或多个数据源、单一输出 | 三个 Office 模板样例生成成功；无占位符残留；原模板不变；缺失映射可澄清 |
| T57 | P0 | BE2 | BE1、BE4、DI2 | T17、T18 | 实现 `GenerationSpec` 校验和从零生成计划：DOCX/XLSX/PPTX/MD/TXT/CSV 直接生成，PDF 拆转换 Job | 无来源和多来源样例可计划；非法结构、缺少目标和直接 PDF 生成被拒绝 |
| T58 | P0 | BE4 | BE3、DI1、DI2 | T57、T51、T52 | 实现格式专用 Builder：DOCX 章节/表格、XLSX 工作表/字段、PPTX 幻灯片、文本和 CSV 输出 | AC-035 六种直接目标可打开；关键结构和数量有断言；不执行模型生成代码 |
| T59 | P0 | BE2 | BE1、BE4 | T18、T19、T57 | 实现完整 Job DAG Scheduler：拓扑就绪、冻结输入哈希、串行执行、前驱失败阻塞和警告传播 | 循环/深度/悬空依赖被拒绝；无关分支继续；警告沿链传播；重试不覆盖旧产物 |
| T60 | P0 | BE4 | BE2、BE3、DI1 | T50、T54、T57、T59 | 实现验证器接口和 P0 验证流水线：重开、结构、关键内容、编码、公式、图表、模板和渲染断言 | 每个交付型 Job 至少一个 validator；未验证项不能标记通过；结果写入 `validation_results` |
| T61 | P0 | BE2 | BE1、BE4 | T59、T60 | 实现最多 2 轮修复循环、预算控制、15 分钟任务硬超时和调用次数限制 | 第 3 次修复被拒绝；达到预算后记录失败项；模型/工具重试计入预算 |
| T62 | P0 | BE2 | DI2、DI3 | T60、T61 | 实现 Model Gateway 的真实 OpenAI 兼容适配、结构化输出校验、429/5xx 短重试和稳定错误码 | 无密钥泄漏；Schema 失败最多重规划一次；外部服务失败不伪造产物 |
| T63 | P0 | BE1 | BE2、FE3 | T15、T59 | 补齐 DAG、澄清、警告、阻塞、部分成功、任务结束和中断相关 SSE 事件 | 事件类型与 Pydantic 判别联合一致；时间线顺序稳定；敏感字段被脱敏 |
| T64 | P0 | BE2 | BE1、FE3 | T17、T23、T63 | 实现歧义门禁和澄清流程：2 至 3 个互斥选项、推荐理由、自由输入、取消和恢复 | AC-004 通过；取消不修改文件；回答后恢复同一轮次而非新建任务 |
| T65 | P0 | FE3 | BE2、FE4 | T16、T44、T63 | 实现定制 `JobDagTimeline`、依赖关系、等待前驱、被阻塞、修复轮次、警告时间和工具步骤 | 后继在前驱发布前不能显示执行中；部分成功可直接理解；无原始思维链 |
| T66 | P0 | FE3 | BE1、BE2、T64 | T64、T65 | 实现 `ClarificationCard`、错误诊断面板和澄清恢复交互 | 推荐项、互斥选项和自由输入完整；提交中防重复；取消状态正确 |
| T67 | P0 | FE2 | BE4、FE3 | T55、T56 | 实现模板诊断、字段映射摘要、候选数据源和缺数据提示界面 | 诊断码、位置和严重度可读；阻止级问题不展示可提交生成入口 |
| T68 | P0 | FE4 | BE3、BE4、FE3 | T41、T65 | 实现转换摘要、结果血缘、中间产物、结果组顺序、警告和下载入口 | 生成后转换的两个产物均有下载；警告持续可见；被阻塞 Job 无伪下载按钮 |
| T69 | P0 | BE1 | FE3、DI3 | T43、T59 | 实现应用重启后的历史恢复、任务中断展示、删除协调器和 staged 清理 | AC-017、AC-018 通过；中断不显示成功；已发布产物不被清理 |
| T70 | P0 | DI1 | BE3、BE4 | T50、T54、T57 | 补齐转换矩阵每个 P0 转换对、模板诊断和从零生成夹具及预期结果 | 每个转换至少成功和不支持/前置失败样例；预期保真、警告和结构断言明确 |
| T71 | P0 | DI2 | BE2、BE4、BE1 | T59、T60、T62、T63 | 建立 DAG/转换/模板/生成集成测试：多分支、警告传播、阻塞、幂等、SSE 回放和 provider 故障 | 假模型和固定样例下稳定；故障注入能触发稳定错误码；契约无漂移 |
| T72 | P0 | DI3 | FE3、FE4、DI2 | T65、T66、T67、T68、T71 | 建立 M3 Playwright：澄清、DAG 部分失败、模板生成、生成后转换和结果组下载 | AC-004、AC-033 至 AC-039、AC-044 有可复现证据 |

## 9. M4：安全、性能与集成硬化

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T80 | P0 | BE1 | DI3、BE2 | T11、T13、T43、T69 | 完成本地访问安全：Host、Origin、会话 Cookie、请求头、CSP、安全响应头和 UUID 下载 | 非本机 Host/Origin 和缺少保护头请求返回 403；无宽泛 CORS |
| T81 | P0 | BE3 | DI1、DI3 | T30、T33、T35、T39 | 完成 OOXML、PDF、图片解析资源限制：压缩体积、条目数、XML 深度、外部关系、像素和 CPU 预算 | AC-041、AC-042 通过；恶意样例不触发外链、宏或资源耗尽 |
| T82 | P0 | BE4 | DI1、DI3 | T37、T38、T51、T56、T58 | 完成文本、CSV、Markdown、模板和生成安全：编码、公式注入、XSS、外部关系、占位残留 | AC-019、AC-040 通过；不可信内容不执行；输出重新解码验证 |
| T83 | P0 | BE2 | BE1、DI2、DI3 | T59、T61、T62 | 完成依赖安全：冻结哈希、同任务同轮次校验、删除/篡改后阻塞和警告继承 | AC-043、AC-044 通过；跨任务 artifact ID 被拒绝；缓存 URL 不泄露旧产物 |
| T84 | P0 | DI3 | FE4、BE1 | T41、T68 | 完成 1280px、1440px、960px、375px Playwright 截图与布局检查 | 操作按钮、下载入口、验证风险、文件名和输入 Dock 不重叠/截断 |
| T85 | P0 | DI3 | DI2、BE1、BE2 | T63、T71、T72 | 完成性能基准：2 秒接收、5 秒状态反馈、常规 3 分钟、上限 10 分钟和 15 分钟硬超时 | 排队、等待前驱、执行和验证时间分别可见；慢任务有明确原因 |
| T86 | P0 | DI2 | BE2、BE1、DI3 | T19、T69、T71 | 完成崩溃恢复与并发测试：租约过期、SSE 断线、幂等重放、单 Worker 争用、队列上限 | 恢复后状态稳定；同任务不双领取；队列第 4 个任务返回 `QUEUE_FULL` |
| T87 | P0 | DI1 | BE3、BE4、DI3 | T45、T70、T81 | 补齐中英文、公式、表格、图表、扫描 PDF、编码冲突、透明图片、模板、提示注入和超大文件验收数据 | 数据可复现，含固定哈希；无真实个人信息；所有 P0 验收项至少被一个夹具覆盖 |
| T88 | P0 | BE1 | FE1、DI3 | T08、T69 | 实现 Windows 单入口启动器和交付期 FastAPI 托管前端构建产物 | 启动顺序为 Worker->API；健康检查失败有可见提示；退出清理 Worker 和超时 Office 进程 |
| T89 | P0 | FE1 | FE4、DI3 | T14、T84 | 完成响应式外壳：右栏底部抽屉、左栏 Drawer、中央单栏和面板独立滚动 | `<960px` 可完成任务查看、进度、验证和下载；固定输入区不覆盖内容 |
| T90 | P0 | DI3 | 全体 | T80 至 T89 | 执行 `Requirements.md` 第 12 章 P0 验收扫描，建立 AC 到测试/证据映射 | 每个 P0 AC 有通过证据或明确阻塞项；不存在“手测可用但无记录”的验收项 |

## 10. M5：发布与答辩准备

| ID | 优先级 | 主负责人 | 协作 | 前置 | 任务 | 交付物与验收 |
|---|---|---|---|---|---|---|
| T95 | P0 | DI1 | BE3、BE4 | T87 | 准备演示数据包和可复现演示场景：Word 排版、Excel 清洗汇总、PPT 样式、PDF 问答表格、多文件部分失败 | 数据不含敏感信息；每个场景有输入、指令、预期结果和异常说明 |
| T96 | P0 | DI3 | 全体 | T90、T95 | 完成一次从全新数据目录开始的完整回归：安装、迁移、启动、演示、退出、重启恢复 | 结果可重复；失败项有负责人和修复 ID；无未提交生成契约 |
| T97 | P0 | BE1 | DI3、FE1 | T88、T96 | 完成发布包和运行说明：环境变量示例、数据目录、日志位置、Office 依赖、故障排查 | 新机器按说明可启动；密钥不在发布包；日志和数据库不进入包 |
| T98 | P1 | DI3 | FE3、BE2 | T96 | 编写验收报告和答辩技术要点：架构、5 个业务工具视图、DAG、验证与修复、安全边界 | 每个技术亮点能追溯到设计章节、代码任务和测试证据 |
| T99 | P1 | 全体 | DI3 | T96 | 处理回归缺陷并按 P0/P1 分级，P0 清零后冻结发布候选 | P0 缺陷为零；P1 缺陷有影响说明和规避方案；发布候选有 SHA 记录 |

## 11. P1 延展任务

以下任务只有在 M4 门禁通过后安排，不得挤占 P0 验收：

| ID | 优先级 | 主负责人 | 协作 | 任务 | 验收 |
|---|---|---|---|---|---|
| T101 | P1 | DI1 | BE2、DI3 | 建立 50 条以上中英文口语指令评测集，覆盖读取、编辑、转换、模板和生成 | 指令有预期任务类型、工具和输出，可统计路由准确率 |
| T102 | P1 | DI2 | BE2 | 增加模型路由准确率、Schema 成功率、超时率和 token 用量报表 | 固定评测集可一键运行并输出 Markdown/JSON 报告 |
| T103 | P1 | FE3 | BE3、BE4 | 增加修改清单和“原稿 vs 结果”结构化摘要展示 | 只展示工具/验证器提供的证据，不做像素级差异高亮 |
| T104 | P1 | DI3 | FE4 | 增加待人工复核清单汇总到结果区 | 低置信 OCR、复杂对象和未验证项集中可见 |
| T105 | P1 | BE4 | DI1 | 增加失败时“返还原件 + 失败说明”的独立下载选项 | 状态仍为失败，不伪装成功，原件只读可追溯 |

## 12. 明确不排期

以下能力不属于 MVP，不在本任务表内安排实现：

1. 多用户、账号、权限、共享和云端同步。
2. 旧版 `.doc/.xls/.ppt`、宏、加密文档处理。
3. PDF 编辑、合并、拆分、表单填写和页面重排。
4. PDF 转 Office、Office 跨家族重建和 Office 直接转图片。
5. 模板表达式、循环嵌套、宏、脚本和外部数据连接。
6. 独立 AI 生图、抠图、修图和像素编辑。
7. 多 Worker、PostgreSQL、集群、计费和 SLA。
8. 复杂版本树、可视化回退和移动端完整编辑。

## 13. Definition of Done

每个任务完成时必须同时满足：

- [ ] 交付物位于约定目录，接口名称与 `Design.md` 一致。
- [ ] 先有失败测试或固定验收样例，实现后测试通过。
- [ ] P0 路径不依赖真实外部模型或网络；真实 Provider 单独由集成测试覆盖。
- [ ] 错误具备稳定错误码、可读原因和建议，不泄露路径、正文或密钥。
- [ ] 关键状态同时写入数据库和事件，不以进程内存作为唯一事实源。
- [ ] 未验证 staged 文件不会被发布，已发布产物不会被原地覆盖。
- [ ] 新增或修改的 Pydantic/OpenAPI 契约已重新生成前端类型，CI 无差异。
- [ ] 用户可见状态同时使用文字和视觉标识，不仅依赖颜色。
- [ ] 新夹具包含固定哈希和预期结果，测试可重复。
- [ ] 任务涉及的范围、依赖、风险和未完成项已同步到本文件。

## 14. 每次合并前命令

命令以最终脚手架为准，M0 必须在 CI 配置中固化以下最小集合：

```powershell
uv run ruff check .
uv run pyright backend
uv run pytest
pnpm --dir frontend lint
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
pnpm --dir frontend exec playwright test
uv run alembic upgrade head
```

Office COM、Windows 启动器和真实模型 Provider 测试使用独立 smoke 任务，不得用普通 Linux CI 模拟结果替代。

## 15. 任务跟踪表

| 状态 | 含义 |
|---|---|
| 待开始 | 依赖未满足或尚未分配执行 |
| 进行中 | 已有负责人，正在实现 |
| 待评审 | 交付物和测试已完成，等待评审 |
| 阻塞 | 存在明确外部依赖或设计问题，需记录阻塞原因 |
| 完成 | 通过 Definition of Done 和对应门禁 |

建议每周同步以下数字：

| 指标 | 目标 |
|---|---|
| P0 任务完成率 | 按阶段门禁推进 |
| 关键路径延期数 | 0 个无处置的延期 |
| 跨模块契约变更数 | 每次变化都有评审和生成类型更新 |
| 失败测试或验收证据 | 0 个未登记 |
| P0 缺陷 | M5 前清零 |

## 16. 首批启动顺序

本轮可以直接启动的 11 人任务如下：

| 人员 | 首批任务 |
|---|---|
| FE1 | T05 |
| FE2 | 先参与 T06 评审，随后等待 T05、T11 启动 T12 |
| FE3 | 研读 T02、T15 契约，参与 T04 评审 |
| FE4 | 与 FE1 共同完成 T05 的主题和布局基线 |
| BE1 | T01、T02、T03 |
| BE2 | T02 契约评审、T17 设计准备 |
| BE3 | T06 数据需求评审、T32 Office Gate 设计准备 |
| BE4 | T06 数据需求评审、T20 设计准备 |
| DI1 | T06 |
| DI2 | T04、T07、T10 准备 |
| DI3 | 建立 AC 追踪表和 M1 端到端用例骨架 |


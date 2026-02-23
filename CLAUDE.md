# CLAUDE.md

仓库：`billsys`

## 项目上下文

<!-- BEGIN AUTO:PROJECT_CONTEXT -->
当前仓库使用 Node.js、Python、Vue。请在代码变更后同步更新目录文档和开发规范文档。
<!-- END AUTO:PROJECT_CONTEXT -->

## 架构概览

<!-- BEGIN AUTO:ARCHITECTURE -->
- `.claude`：Claude Code 配置目录（hooks、设置等），非业务代码。
- `backend`：FastAPI 后端，含路由、模型、服务。
- `frontend`：Vue 3 前端，含页面、路由、API 调用。
<!-- END AUTO:ARCHITECTURE -->

## 常用命令

<!-- BEGIN AUTO:COMMANDS -->
- `(cd backend && .venv/bin/uvicorn main:app --reload)`
- `(cd frontend && npm run build)`
- `(cd frontend && npm run dev)`
- `(cd frontend && npm run preview)`
<!-- END AUTO:COMMANDS -->

## 目录注释维护流程

<!-- BEGIN AUTO:TREE_COMMENT_WORKFLOW -->
1. 运行目录同步脚本。
2. 打开 `PROJECT_TREE.md`，定位以 `TODO_AI:` 开头的注释。
3. 将待补注释替换为简洁、准确的中文用途说明。
4. 补充完成后再次运行脚本，确认待办队列清零。

待补注释路径：
- 当前无待补注释路径。
<!-- END AUTO:TREE_COMMENT_WORKFLOW -->

## 手工规范（人工维护）

<!-- BEGIN MANUAL:NOTES -->
### 核心原则
- 全部使用中文回复。
- `CLAUDE.md` 是系统级配置，不是项目说明书；只保留高复用规则。
- 规则要短、稳、可执行；避免写一次性任务细节。
- 仅维护根目录 `CLAUDE.md`，不拆分子 `CLAUDE.md`。

### WHAT（项目事实）
- 后端：FastAPI + SQLAlchemy + Pydantic，入口 `backend/main.py`。
- 前端：Vue 3 + Vite + Element Plus，入口 `frontend/src/main.js`。
- 关键业务模块：
  - 资产：`backend/routers/assets.py`、`frontend/src/views/AssetList.vue`、`frontend/src/views/AssetForm.vue`
  - 衣柜：`backend/routers/clothing.py`、`frontend/src/views/ClothingList.vue`
  - 搭配：`backend/routers/outfits.py`、`frontend/src/views/OutfitEditor.vue`
  - 试穿：`backend/routers/tryon.py`、`frontend/src/views/TryOn.vue`
  - 媒体：`backend/routers/media.py`、`backend/services/storage.py`
- 前端路由入口：`frontend/src/router/index.js`（所有页面跳转均在此定义）
- 媒体存储：图片上传至 **Cloudflare R2**，通过 `backend/services/storage.py` 封装；本地不保留原始文件。相关环境变量：`CF_ACCOUNT_ID`、`R2_BUCKET`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY`、`R2_PUBLIC_BASE_URL`。
- AI 能力：图像/文本分析使用 **Google Gemini**，相关环境变量：`GEMINI_API_KEY`、`GEMINI_TEXT_MODEL`、`GEMINI_IMAGE_MODEL` 等（见 `backend/.env.example`）。
- `frontend/src/views/AssetDetail.vue` 当前无导航入口（已被 AssetForm 取代），待确认是否删除。

### WHY（决策优先级）
- 优先保证数据正确性，再追求交互速度。
- 优先最小改动闭环，不做无关重构。
- 前后端字段语义必须一致，避免“后端改了前端没生效”。

### HOW（执行方式）
- 改动前先定位“真实生效路径”（接口/页面最终计算点）。
- 默认流程：定位 -> 最小改动 -> 构建/校验 -> 再扩展优化。
- 任务涉及计算口径时，先统一口径定义，再改代码。

### 工作流清单
1. 新增或修改接口
   - 检查现有同类路由与 schema。
   - 同步更新前端调用与字段消费逻辑。
   - 至少验证一个真实页面路径。
2. 数据库字段/语义调整
   - 明确兼容策略（默认值、历史数据行为）。
   - 校验 `models.py`、`schemas.py`、路由返回是否一致。
3. 前端页面逻辑调整
   - 标注状态来源（本地计算/接口返回）。
   - 避免并发状态竞态（加载、保存、回填）。
   - 保证空态、加载态、错误态可区分。

### 文件边界
- 可直接修改：`frontend/src/**`、`backend/routers/**`、`backend/services/**`。
- 慎改：`backend/models.py`、`backend/schemas.py`（会影响全链路）、`frontend/src/router/index.js`（会影响所有页面跳转）。
- 禁止写入：任何密钥、令牌、生产凭证（含 R2 Access Key / Secret、Bucket 名）。

### 质量门禁
- 前端改动后至少执行：`(cd frontend && npm run build)`。
- 后端 Python 改动后至少执行：`python -m py_compile <changed_file>`。
- 性能相关改动需说明瓶颈点与验证方式。

### 文档与目录维护
- 新增/删除路径后，及时同步 `PROJECT_TREE.md` 与本文件。
- 目录注释要求：事实描述、简短、可验证。

### 渐进式读取策略
- 先读任务相关最小文件集，再扩展上下文。
- 当规则与代码冲突时，以“当前可运行代码 + 明确业务目标”为准，并同步修正规则。
<!-- END MANUAL:NOTES -->

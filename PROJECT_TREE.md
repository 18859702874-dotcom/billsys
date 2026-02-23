# 项目目录树

更新时间：2026-02-23 11:15:46 UTC

说明：出现 `TODO_AI:` 的路径，表示新增后尚未补齐业务注释。

## 多层级目录树（含注释）

```text
├── .claude/                        # [L1]AI 协作工具本地配置目录。
│   └── settings.local.json         # [F][F]设置相关配置文件。
├── backend/                        # [L1][L1][L1]后端服务代码。
│   ├── routers/                    # [L2][L2][L2]API 路由定义。
│   │   ├── __init__.py             # [F][F][F]路由模块初始化与导出。
│   │   ├── analytics.py            # [F][F][F]统计分析相关 API 路由与请求处理。
│   │   ├── assets.py               # [F][F][F]资产相关 API 路由与请求处理。
│   │   ├── categories.py           # [F][F][F]分类相关 API 路由与请求处理。
│   │   ├── clothing.py             # [F][F][F]衣物相关 API 路由与请求处理。
│   │   ├── media.py                # [F]R2 对象媒体代理访问路由。
│   │   ├── outfits.py              # [F][F][F]穿搭相关 API 路由与请求处理。
│   │   ├── snapshots.py            # [F][F][F]快照相关 API 路由与请求处理。
│   │   └── tryon.py                # [F][F][F]试穿相关 API 路由与请求处理。
│   ├── scripts/                    # [L2][L2][L2]自动化脚本。
│   │   ├── add_expected_days.py    # [F][F][F]批量补充预期天数的数据维护脚本。
│   │   └── reset_and_seed.py       # [F][F][F]重置并初始化示例数据脚本。
│   ├── services/                   # [L2][L2][L2]业务服务层。
│   │   ├── __init__.py             # [F][F][F]服务模块初始化与导出。
│   │   ├── analytics.py            # [F][F][F]统计分析相关业务服务逻辑。
│   │   ├── depreciation.py         # [F][F][F]资产折旧计算服务逻辑。
│   │   └── storage.py              # [F]本地与 R2 媒体存储服务。
│   ├── uploads/                    # [L2][L2][L2]上传媒体文件存储目录。
│   │   ├── clothing/               # [L3][L3][L3]服装图片上传存储目录。
│   │   └── tryon/                  # [L3][L3][L3]试穿图片存储目录。
│   ├── .env                        # [F][F][F]后端本地环境变量配置。
│   ├── .env.example                # [F][F][F]后端环境变量模板。
│   ├── billsys.db                  # [F][F][F]本地 SQLite 开发数据库文件。
│   ├── database.py                 # [F][F][F]数据库连接、会话与基础配置。
│   ├── main.py                     # [F][F][F]后端应用入口与路由挂载。
│   ├── models.py                   # [F][F][F]数据库 ORM 模型定义。
│   ├── requirements.txt            # [F][F][F]后端依赖与版本约束清单。
│   └── schemas.py                  # [F][F][F]接口请求与响应数据模型定义。
├── frontend/                       # [L1][L1][L1]前端应用代码。
│   ├── src/                        # [L2][L2][L2]前端源码根目录。
│   │   ├── api/                    # [L3][L3][L3]前端 API 请求封装目录。
│   │   │   └── index.js            # [F][F][F]统一封装后端接口请求。
│   │   ├── components/             # [L3][L3][L3]可复用 UI 组件。
│   │   │   ├── AssetCard.vue       # [F][F][F]资产卡片可复用展示组件。
│   │   │   ├── CategoryPie.vue     # [F][F][F]分类占比可复用展示组件。
│   │   │   ├── DailyCostChart.vue  # [F][F][F]每日成本可复用展示组件。
│   │   │   └── TrendChart.vue      # [F][F][F]趋势可复用展示组件。
│   │   ├── router/                 # [L3][L3][L3]前端路由配置目录。
│   │   │   └── index.js            # [F][F][F]前端路由表与导航守卫配置。
│   │   ├── views/                  # [L3][L3][L3]页面视图模块。
│   │   │   ├── Analytics.vue       # [F][F][F]统计分析页面组件。
│   │   │   ├── AssetDetail.vue     # [F][F][F]资产详情页面组件。
│   │   │   ├── AssetForm.vue       # [F][F][F]资产表单页面组件。
│   │   │   ├── AssetList.vue       # [F][F][F]资产列表页面组件。
│   │   │   ├── ClothingForm.vue    # [F][F][F]衣物表单页面组件。
│   │   │   ├── ClothingList.vue    # [F][F][F]衣物列表页面组件。
│   │   │   ├── OutfitEditor.vue    # [F][F][F]穿搭编辑页面组件。
│   │   │   ├── OutfitList.vue      # [F][F][F]穿搭列表页面组件。
│   │   │   ├── Settings.vue        # [F][F][F]设置页面组件。
│   │   │   └── TryOn.vue           # [F][F][F]试穿页面组件。
│   │   ├── App.vue                 # [F][F][F]前端根组件与全局布局。
│   │   └── main.js                 # [F][F][F]前端应用初始化与挂载入口。
│   ├── index.html                  # [F][F][F]前端页面入口模板。
│   ├── package-lock.json           # [F][F][F]前端依赖锁定文件。
│   ├── package.json                # [F][F][F]前端依赖、脚本与构建配置。
│   └── vite.config.js              # [F][F][F]Vite 构建与开发服务配置。
└── .gitignore                      # [F][F][F]Git 忽略规则清单。
```

## 变更摘要

新增路径：
- （无）

删除路径：
- （无）

## 待 AI 补注释路径

- （无）

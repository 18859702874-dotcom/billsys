# 计算规则说明（calrule）

本文档用于沉淀当前项目中“资产成本”相关的统一计算口径，便于后续排查与对齐。

## 1. 适用范围

- 资产列表页（`frontend/src/views/AssetList.vue`）
- 统计分析服务（`backend/services/analytics.py`）
- 折旧基础计算（`backend/services/depreciation.py`）

## 2. 基础字段定义

- `purchase_price`：购买价格
- `recovery_amount`：回收金额（可空）
- `purchase_date`：购买日期
- `disposed_date`：弃置日期（仅弃置资产）
- `status`：资产状态，常见为 `active` / `disposed`
- `expected_days`：预计使用天数（可空）

## 3. 基础计算（后端）

来源：`backend/services/depreciation.py`

### 3.1 使用天数 `days_used`

- 公式：`max((end_date - purchase_date).days, 1)`
- 其中：
  - 若资产为弃置且有 `disposed_date`，`end_date = disposed_date`
  - 否则 `end_date = target_date`（默认今天）

### 3.2 净成本 `net_cost`

- 公式：`purchase_price - recovery_amount`
- 下限：最小为 `0`
- 精度：保留两位小数，`ROUND_HALF_UP`

### 3.3 平均每日费用 `daily_cost`

- 公式：`net_cost / days_used`
- 精度：保留两位小数，`ROUND_HALF_UP`

### 3.4 预估每日费用 `estimated_daily_cost`

- 前提：`expected_days` 存在
- 公式：`net_cost / expected_days`
- 精度：保留两位小数，`ROUND_HALF_UP`

## 4. 综合日成本（核心规则）

综合日成本用于“资产列表展示”和“分析聚合”。

### 4.1 当前统一口径

1. **在用资产**（`status != disposed`）：
   - 若 `expected_days` 存在且 `days_used > expected_days`，综合日成本为 `0`
2. 其他情况：
   - 取 `daily_cost` 与 `estimated_daily_cost` 的较小值
   - 若无 `estimated_daily_cost`，则使用 `daily_cost`
3. **弃置资产**（`status == disposed`）：
   - 不触发“超预计天数归零”规则
   - 按第 2 条常规规则计算

## 5. 生效位置

### 5.1 前端资产列表（展示口径）

- 文件：`frontend/src/views/AssetList.vue`
- 函数：
  - `comprehensiveCost(row)`
  - `isEstimated(row)`

### 5.2 后端分析统计（报表口径）

- 文件：`backend/services/analytics.py`
- 函数：
  - `_comprehensive_daily_cost(asset, target_date)`
  - `get_category_distribution(...)`
  - `get_cost_summary(...)`
  - `get_total_daily_cost_trend(...)`

## 6. 对齐原则

- 若调整综合日成本规则，需同时修改：
  - `frontend/src/views/AssetList.vue`
  - `backend/services/analytics.py`
- 修改后至少执行：
  - 前端：`(cd frontend && npm run build)`
  - 后端：`python -m py_compile backend/services/analytics.py`

## 7. 备注

- 当前“资产列表页综合日成本”由前端本地函数计算，不是后端直接返回字段。
- 若后续需要彻底避免前后端口径漂移，建议将综合日成本下沉为后端统一字段并由前端直出。

<template>
  <div class="asset-list-page">
    <div class="toolbar">
      <div class="toolbar-filters">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input v-model="filters.search" placeholder="搜索资产名称..." @keyup.enter="load" />
        </div>
        <el-select v-model="filters.category_id" placeholder="全部分类" clearable @change="load" class="filter-select">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="全部状态" clearable @change="load" class="filter-select">
          <el-option label="使用中" value="active" />
          <el-option label="已弃用" value="disposed" />
        </el-select>
      </div>
      <button class="btn-primary" @click="$router.push('/assets/new')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        新增资产
      </button>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 18%">资产名称</th>
            <th>分类</th>
            <th>购买渠道</th>
            <th style="text-align: right">购买价格</th>
            <th style="text-align: right">回收金额</th>
            <th>购买日期</th>
            <th style="text-align: center">使用天数</th>
            <th style="text-align: right">平均每日费用</th>
            <th style="text-align: left">综合日成本</th>
            <th>弃用原因</th>
            <th style="text-align: center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in assets" :key="row.id" class="table-row">
            <td>
              <span class="asset-name" @click="$router.push(`/assets/${row.id}`)">
                {{ row.name }}
              </span>
            </td>
            <td><span class="cat-tag" :style="catTagStyle(row.category_name)">{{ row.category_name }}</span></td>
            <td><span class="channel-text">{{ row.purchase_channel || '-' }}</span></td>
            <td style="text-align: right; font-variant-numeric: tabular-nums">
              {{ formatMoney(row.purchase_price) }}
            </td>
            <td style="text-align: right; font-variant-numeric: tabular-nums">
              <span v-if="row.recovery_amount" class="net-cost recovery">{{ formatMoney(row.recovery_amount) }}</span>
              <span v-else>-</span>
            </td>
            <td style="font-variant-numeric: tabular-nums; color: var(--text-secondary)">{{ row.purchase_date }}</td>
            <td style="text-align: center; font-variant-numeric: tabular-nums">
              <div>{{ row.days_used }} 天</div>
              <div v-if="row.expected_days" class="days-sub">预计 {{ row.expected_days }} 天</div>
            </td>
            <td style="text-align: right">
              <span v-if="row.status === 'active'">
                {{ formatDailyCost(row.daily_cost) }}
              </span>
              <span v-else>-</span>
            </td>
            <td style="text-align: left">
              <span class="daily-cost" :class="{ 'cost-warn': row.expected_days && row.days_used < row.expected_days }" :title="isEstimated(row) ? '预估费用（基于预计使用天数）' : ''">
                {{ formatDailyCost(comprehensiveCost(row)) }}
              </span>
            </td>
            <td>{{ row.disposed_reason || '-' }}</td>
            <td style="text-align: center">
              <div class="action-btns">
                <button class="action-btn" title="编辑" @click="$router.push(`/assets/${row.id}/edit`)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                </button>
                <button class="action-btn warn" title="弃用" v-if="row.status === 'active'" @click="handleDispose(row)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" />
                  </svg>
                </button>
                <button class="action-btn success" title="还原" v-if="row.status === 'disposed'" @click="handleRestore(row)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <polyline points="23 4 23 10 17 10" />
                    <polyline points="1 20 1 14 7 14" />
                    <path d="M3.5 9a9 9 0 0114.2-3.4L23 10M1 14l5.3 4.4A9 9 0 0020.5 15" />
                  </svg>
                </button>
                <el-popconfirm title="确定要删除此资产吗？" @confirm="handleDelete(row.id)" width="220">
                  <template #reference>
                    <button class="action-btn danger" title="删除">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                      </svg>
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!assets.length" class="empty-table">
        <p>暂无匹配的资产数据</p>
      </div>
    </div>

    <el-dialog v-model="disposeVisible" title="弃用资产" width="440px" :close-on-click-modal="false">
      <div class="dispose-form">
        <div class="dispose-field">
          <label>弃用日期</label>
          <el-date-picker v-model="disposeForm.disposed_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </div>
        <div class="dispose-field">
          <label>弃用原因</label>
          <el-select v-model="disposeForm.disposed_reason" placeholder="选择原因" filterable allow-create style="width: 100%">
            <el-option label="坏了" value="坏了" />
            <el-option label="以旧换新" value="以旧换新" />
            <el-option label="卖了" value="卖了" />
            <el-option label="送人" value="送人" />
            <el-option label="丢了" value="丢了" />
            <el-option label="不需要了" value="不需要了" />
          </el-select>
        </div>
        <div class="dispose-field">
          <label>回收金额（可选）</label>
          <div class="input-with-prefix">
            <span class="input-prefix">¥</span>
            <input v-model.number="disposeForm.recovery_amount" type="number" min="0" step="0.01" class="form-input has-prefix" />
          </div>
        </div>
        <div class="dispose-field">
          <label>回收日期（可选）</label>
          <el-date-picker v-model="disposeForm.recovery_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" clearable />
        </div>
      </div>
      <template #footer>
        <el-button @click="disposeVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDispose">确认弃用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAssets, getCategories, deleteAsset, disposeAsset, restoreAsset } from '../api'

const assets = ref([])
const categories = ref([])
const filters = ref({ category_id: null, status: null, search: '' })
const disposeVisible = ref(false)
const disposeRow = ref(null)
const disposeForm = ref({
  disposed_date: new Date().toISOString().slice(0, 10),
  disposed_reason: '',
  recovery_amount: null,
  recovery_date: null,
})

const catColors = ['#4f6ef7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function catTagStyle(catName) {
  const idx = categories.value.findIndex((c) => c.name === catName)
  const color = catColors[idx % catColors.length] || '#4f6ef7'
  return { background: color + '18', color }
}

function comprehensiveCost(row) {
  const actual = Number(row.daily_cost || 0)
  const estimated = Number(row.estimated_daily_cost || 0)
  if (row.status === 'disposed' || !estimated || actual <= estimated) {
    return actual
  }
  return estimated
}

function isEstimated(row) {
  const actual = Number(row.daily_cost || 0)
  const estimated = Number(row.estimated_daily_cost || 0)
  return row.status !== 'disposed' && estimated && actual > estimated
}

function dailyCostClass(cost) {
  const v = Number(cost)
  if (v >= 5) return 'cost-high'
  if (v >= 3) return 'cost-mid'
  return 'cost-low'
}

function formatMoney(v) {
  return `¥${Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function formatDailyCost(cost) {
  return `¥${Number(cost || 0).toFixed(2)}/天`
}

async function load() {
  const params = {}
  if (filters.value.category_id) params.category_id = filters.value.category_id
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.search) params.search = filters.value.search
  const res = await getAssets(params)
  assets.value = res.data
}

async function handleDelete(id) {
  await deleteAsset(id)
  ElMessage.success('已删除')
  load()
}

function handleDispose(row) {
  disposeRow.value = row
  disposeForm.value = {
    disposed_date: new Date().toISOString().slice(0, 10),
    disposed_reason: '',
    recovery_amount: null,
    recovery_date: null,
  }
  disposeVisible.value = true
}

async function confirmDispose() {
  if (!disposeForm.value.disposed_reason) {
    ElMessage.warning('请选择弃用原因')
    return
  }

  const payload = {
    disposed_date: disposeForm.value.disposed_date,
    disposed_reason: disposeForm.value.disposed_reason,
    recovery_amount: disposeForm.value.recovery_amount === '' ? null : disposeForm.value.recovery_amount,
    recovery_date: disposeForm.value.recovery_date || null,
  }

  if (payload.recovery_amount !== null && payload.recovery_amount !== undefined && !payload.recovery_date) {
    payload.recovery_date = payload.disposed_date
  }

  await disposeAsset(disposeRow.value.id, payload)
  ElMessage.success('已弃用')
  disposeVisible.value = false
  load()
}

async function handleRestore(row) {
  try {
    await ElMessageBox.confirm('确定要恢复该资产为在用状态吗？', '还原资产', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  await restoreAsset(row.id)
  ElMessage.success('已还原为在用')
  load()
}

onMounted(async () => {
  const res = await getCategories()
  categories.value = res.data
  load()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.toolbar-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(180deg, #ffffff 0%, #fdfdff 100%);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
  height: 40px;
  width: 280px;
  transition: border-color var(--transition), box-shadow var(--transition);
  color: var(--text-secondary);
}
.search-box:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12), var(--shadow-sm);
}
.search-box input {
  border: none;
  outline: none;
  background: none;
  font-size: 13px;
  color: var(--text-primary);
  width: 100%;
}
.search-box input::placeholder {
  color: var(--text-muted);
}

.filter-select {
  width: 148px;
}

.asset-list-page :deep(.filter-select .el-select__wrapper) {
  min-height: 40px;
  border-radius: 10px;
  box-shadow: none;
  background: linear-gradient(180deg, #ffffff 0%, #fdfdff 100%);
  border: 1px solid var(--border-color);
  transition: border-color var(--transition), box-shadow var(--transition);
  font-size: 13px;
}

.asset-list-page :deep(.filter-select .el-select__wrapper.is-focused),
.asset-list-page :deep(.filter-select .el-select__wrapper:hover) {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12);
}

.asset-list-page :deep(.filter-select .el-select__placeholder),
.asset-list-page :deep(.filter-select .el-select__selected-item) {
  font-size: 13px;
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
  transition: none !important;
}

.asset-list-page :deep(.filter-select .el-select__placeholder) {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
}

.asset-list-page :deep(.filter-select .el-select__input),
.asset-list-page :deep(.filter-select .el-select__wrapper:hover .el-select__selected-item),
.asset-list-page :deep(.filter-select .el-select__wrapper.is-focused .el-select__selected-item),
.asset-list-page :deep(.filter-select .el-select__wrapper:hover .el-select__input),
.asset-list-page :deep(.filter-select .el-select__wrapper.is-focused .el-select__input) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
  transition: none !important;
}

.asset-list-page :deep(.dispose-form .el-select__wrapper),
.asset-list-page :deep(.dispose-form .el-date-editor),
.asset-list-page :deep(.dispose-form .el-date-editor .el-input__wrapper) {
  min-height: 40px;
  border-radius: 10px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0 20px;
  height: 38px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: filter var(--transition), transform var(--transition);
}
.btn-primary:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1360px;
}
.data-table thead {
  background: #f8f9fd;
}
.data-table th {
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}
.data-table td {
  padding: 14px 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
  white-space: nowrap;
}
.table-row {
  transition: background var(--transition);
}
.table-row:hover {
  background: #f8f9fd;
}
.table-row:last-child td {
  border-bottom: none;
}

.asset-name {
  cursor: pointer;
  font-weight: 500;
  transition: color var(--transition);
}
.asset-name:hover {
  color: var(--accent);
}

.cat-tag {
  display: inline-block;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}

.channel-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.days-sub {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.daily-cost {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.daily-cost.cost-warn {
  color: #f59e0b;
}
.daily-cost.cost-low {
  color: #10b981;
}
.daily-cost.cost-mid {
  color: #f59e0b;
}
.daily-cost.cost-high {
  color: #ef4444;
}

.net-cost {
  font-weight: 600;
  color: var(--text-primary);
}

.net-cost.recovery {
  color: #0f766e;
}

.action-btns {
  display: flex;
  gap: 6px;
  justify-content: center;
}
.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}
.action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}
.action-btn.warn:hover {
  border-color: var(--warning);
  color: var(--warning);
  background: var(--warning-light);
}
.action-btn.success:hover {
  border-color: var(--success);
  color: var(--success);
  background: var(--success-light);
}
.action-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: var(--danger-light);
}

.empty-table {
  text-align: center;
  padding: 60px 0;
  color: var(--text-muted);
  font-size: 14px;
}

.dispose-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.dispose-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.dispose-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-with-prefix {
  position: relative;
}
.input-prefix {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
}
.form-input {
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0 14px;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  background: var(--bg-card);
  width: 100%;
}
.form-input.has-prefix {
  padding-left: 30px;
}

@media (max-width: 900px) {
  .toolbar {
    align-items: stretch;
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-filters {
    width: 100%;
  }

  .search-box {
    width: 100%;
  }

  .filter-select {
    width: calc(50% - 6px);
    min-width: 140px;
  }
}
</style>

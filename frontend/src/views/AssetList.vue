<template>
  <div class="asset-list-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <div v-if="viewMode === 'table'" class="toolbar-filters">
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
        <div v-else class="cards-hint">综合日成本概览 · 仅统计在用资产</div>
      </div>
      <div class="toolbar-right">
        <div class="view-toggle">
          <button :class="['toggle-btn', { active: viewMode === 'table' }]" @click="switchView('table')" title="表格视图">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
              <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
            </svg>
            表格
          </button>
          <button :class="['toggle-btn', { active: viewMode === 'cards' }]" @click="switchView('cards')" title="卡片视图">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
              <rect x="2" y="3" width="20" height="5" rx="1" />
              <rect x="2" y="10" width="9" height="11" rx="1" />
              <rect x="13" y="10" width="9" height="11" rx="1" />
            </svg>
            卡片
          </button>
        </div>
        <button class="btn-primary" @click="$router.push('/assets/new')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          新增资产
        </button>
      </div>
    </div>

    <!-- Table view -->
    <div v-if="viewMode === 'table'" class="table-card">
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
              <span class="asset-name" @click="$router.push(`/assets/${row.id}/edit`)">
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

    <!-- Cards view -->
    <div v-else class="cards-view">
      <!-- Summary banner -->
      <div class="summary-banner" :class="{ 'over-budget': totalBudget > 0 && overallDailyCost > totalBudget }">
        <div class="summary-main">
          <div class="summary-block">
            <span class="summary-label">综合日成本</span>
            <span class="summary-value" :class="totalBudget > 0 && overallDailyCost > totalBudget ? 'val-danger' : 'val-primary'">
              ¥{{ overallDailyCost.toFixed(2) }}<span class="per-day">/天</span>
            </span>
          </div>
          <template v-if="totalBudget > 0">
            <div class="summary-sep">/</div>
            <div class="summary-block">
              <span class="summary-label">总预算</span>
              <span class="summary-value val-muted">¥{{ totalBudget.toFixed(2) }}<span class="per-day">/天</span></span>
            </div>
            <div class="summary-pct" :class="overallDailyCost > totalBudget ? 'pct-danger' : 'pct-ok'">
              {{ Math.round(overallDailyCost / totalBudget * 100) }}%
            </div>
          </template>
          <template v-else>
            <div class="summary-no-budget">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              前往「设置」为各分类配置预算
            </div>
          </template>
        </div>
        <div v-if="totalBudget > 0" class="summary-bar-wrap">
          <div class="summary-bar">
            <div
              class="summary-bar-fill"
              :class="overallDailyCost > totalBudget ? 'fill-danger' : 'fill-ok'"
              :style="{ width: Math.min(overallDailyCost / totalBudget * 100, 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Category cards grid -->
      <div v-if="cardLoading" class="cards-loading">加载中...</div>
      <div v-else-if="categoryStats.length" class="cat-grid">
        <div v-for="cat in categoryStats" :key="cat.id" class="cat-card">
          <div class="cat-card-header">
            <span class="cat-dot" :style="{ background: cat.allExceeded ? '#f59e0b' : '#4f6ef7' }"></span>
            <span class="cat-card-name">{{ cat.name }}</span>
            <span class="cat-card-badge">{{ cat.count }}件在用</span>
          </div>

          <div class="cat-cost-row">
            <span class="cat-cost-val">¥{{ cat.totalDailyCost.toFixed(2) }}</span>
            <span class="cat-cost-unit">/天</span>
          </div>

          <template v-if="cat.daily_budget">
            <div class="cat-budget-row">
              <span class="cat-budget-label">预算</span>
              <span class="cat-budget-val" @click.stop="handleSetBudgetFromCard(cat)" title="点击修改预算">
                ¥{{ Number(cat.daily_budget).toFixed(2) }}/天
              </span>
              <span class="cat-budget-pct" :class="cat.totalDailyCost > Number(cat.daily_budget) ? 'pct-danger' : 'pct-ok'">
                {{ Math.round(cat.totalDailyCost / Number(cat.daily_budget) * 100) }}%
              </span>
            </div>
            <div class="mini-bar">
              <div
                class="mini-bar-fill"
                :class="cat.totalDailyCost > Number(cat.daily_budget) ? 'fill-danger' : 'fill-ok'"
                :style="{ width: Math.min(cat.totalDailyCost / Number(cat.daily_budget) * 100, 100) + '%' }"
              ></div>
            </div>
          </template>
          <div v-else class="cat-budget-row">
            <span class="cat-budget-label">预算</span>
            <span class="cat-budget-val no-budget-inline" @click.stop="handleSetBudgetFromCard(cat)" title="点击设置预算">
              未设置，点击配置
            </span>
          </div>

          <div class="cat-assets-list">
            <div
              v-for="asset in cat.topAssets"
              :key="asset.id"
              class="cat-asset-item"
              @click="$router.push(`/assets/${asset.id}/edit?from=cards`)"
            >
              <div class="cat-asset-top">
                <span class="cat-asset-name">{{ asset.name }}</span>
                <span class="cat-asset-cost" :class="{ 'cost-estimated': isEstimated(asset) }">
                  ¥{{ comprehensiveCost(asset).toFixed(2) }}/天
                </span>
              </div>
              <div v-if="asset.expected_days" class="asset-prog-bar">
                <div class="asset-prog-track">
                  <div
                    class="asset-prog-fill"
                    :class="assetProgressClass(asset)"
                    :style="{ width: Math.min(asset.days_used / asset.expected_days * 100, 100) + '%' }"
                  ></div>
                </div>
                <span class="asset-prog-label">{{ asset.days_used }}/{{ asset.expected_days }}天</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-cards">
        <p>暂无在用资产</p>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAssets, getCategories, deleteAsset, disposeAsset, restoreAsset, updateCategory } from '../api'

const route = useRoute()

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

// Cards view state
const viewMode = ref('table')
const cardAssets = ref([])
const cardLoading = ref(false)

const catColors = ['#4f6ef7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function getCatColor(catName) {
  const idx = categories.value.findIndex((c) => c.name === catName)
  return catColors[idx % catColors.length] || '#4f6ef7'
}

function catTagStyle(catName) {
  const color = getCatColor(catName)
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

function assetProgressClass(asset) {
  if (!asset.expected_days) return ''
  const pct = asset.days_used / asset.expected_days
  if (pct >= 1) return 'prog-ok'   // exceeded expected — good, keep it green
  if (pct >= 0.8) return 'prog-warn'
  return 'prog-ok'
}

async function handleSetBudgetFromCard(cat) {
  const currentBudget = cat.daily_budget ? Number(cat.daily_budget).toFixed(2) : ''
  try {
    const { value } = await ElMessageBox.prompt(
      `为「${cat.name}」设置每日预算，留空表示不限制。`,
      '设置日预算',
      {
        inputValue: currentBudget,
        inputPlaceholder: '例如：10.00',
        inputType: 'number',
        confirmButtonText: '保存',
        cancelButtonText: '取消',
        inputValidator: (raw) => {
          if (raw === '' || raw === null || raw === undefined) return true
          const v = Number(raw)
          if (isNaN(v) || v < 0) return '请输入有效的非负数字'
          return true
        },
      }
    )
    const raw = (value || '').trim()
    const daily_budget = raw === '' ? null : Number(raw)
    await updateCategory(cat.id, { daily_budget })
    ElMessage.success('预算已更新')
    const res = await getCategories()
    categories.value = res.data
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.detail || '更新预算失败')
  }
}

function formatMoney(v) {
  return `¥${Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function formatDailyCost(cost) {
  return `¥${Number(cost || 0).toFixed(2)}/天`
}

// Cards view computed
const categoryStats = computed(() => {
  return categories.value
    .map((cat) => {
      const catAssets = cardAssets.value.filter((a) => a.category_id === cat.id)
      const totalDailyCost = catAssets.reduce((sum, row) => sum + comprehensiveCost(row), 0)
      const topAssets = [...catAssets]
        .sort((a, b) => comprehensiveCost(b) - comprehensiveCost(a))
      const allExceeded =
        catAssets.length > 0 &&
        catAssets.every((a) => a.expected_days && a.days_used >= a.expected_days)
      return { ...cat, count: catAssets.length, totalDailyCost, topAssets, allExceeded }
    })
    .filter((cat) => cat.count > 0)
})

const overallDailyCost = computed(() =>
  categoryStats.value.reduce((sum, cat) => sum + cat.totalDailyCost, 0)
)

const totalBudget = computed(() =>
  categories.value.reduce((sum, cat) => sum + (Number(cat.daily_budget) || 0), 0)
)

async function load() {
  const params = {}
  if (filters.value.category_id) params.category_id = filters.value.category_id
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.search) params.search = filters.value.search
  const res = await getAssets(params)
  assets.value = res.data
}

async function loadCards() {
  cardLoading.value = true
  try {
    const res = await getAssets({ status: 'active' })
    cardAssets.value = res.data
  } finally {
    cardLoading.value = false
  }
}

function switchView(mode) {
  viewMode.value = mode
  if (mode === 'cards') loadCards()
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
  if (route.query.view === 'cards') {
    viewMode.value = 'cards'
    loadCards()
  } else {
    load()
  }
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}
.toolbar-left {
  flex: 1;
  min-width: 0;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.toolbar-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.cards-hint {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 0;
}

.view-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
}
.toggle-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0 12px;
  height: 38px;
  font-size: 13px;
  background: var(--bg-card);
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
}
.toggle-btn:first-child {
  border-right: 1px solid var(--border-color);
}
.toggle-btn.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 600;
}
.toggle-btn:hover:not(.active) {
  background: #f5f6fa;
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

/* Table view */
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

/* Cards view */
.cards-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-banner {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px 24px;
}
.summary-banner.over-budget {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.03);
}

.summary-main {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.summary-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.summary-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.summary-value {
  font-size: 26px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}
.summary-value .per-day {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-secondary);
  margin-left: 2px;
}
.val-primary { color: var(--accent); }
.val-danger  { color: #ef4444; }
.val-muted   { color: var(--text-primary); }

.summary-sep {
  font-size: 24px;
  color: var(--text-muted);
  font-weight: 300;
}
.summary-pct {
  font-size: 15px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}
.pct-ok     { background: rgba(16, 185, 129, 0.1); color: #059669; }
.pct-danger { background: rgba(239, 68, 68, 0.1);  color: #ef4444; }

.summary-no-budget {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

.summary-bar-wrap {
  margin-top: 14px;
}
.summary-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}
.summary-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.fill-ok     { background: linear-gradient(90deg, #10b981, #34d399); }
.fill-danger { background: linear-gradient(90deg, #f59e0b, #ef4444); }

.cards-loading {
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
  font-size: 14px;
}

.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.cat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 280px;
  overflow: hidden;
  transition: box-shadow var(--transition), transform var(--transition);
}
.cat-card:hover {
  box-shadow: var(--shadow-md, 0 4px 16px rgba(0,0,0,0.08));
  transform: translateY(-2px);
}

.cat-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.cat-card-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cat-card-badge {
  font-size: 11px;
  padding: 2px 8px;
  background: #f1f2f8;
  color: var(--text-secondary);
  border-radius: 10px;
  white-space: nowrap;
}

.cat-cost-row {
  display: flex;
  align-items: baseline;
  gap: 3px;
}
.cat-cost-val {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}
.cat-cost-unit {
  font-size: 13px;
  color: var(--text-muted);
}

.cat-budget-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.cat-budget-label {
  color: var(--text-muted);
  font-weight: 500;
  min-width: 26px;
}
.cat-budget-val {
  color: var(--accent);
  font-variant-numeric: tabular-nums;
  flex: 1;
  cursor: pointer;
  text-decoration: underline dotted;
  text-underline-offset: 2px;
  transition: color var(--transition);
}
.cat-budget-val:hover {
  color: #3551cf;
}
.cat-budget-val.no-budget-inline {
  color: var(--text-muted);
  font-style: italic;
  text-decoration: underline dotted;
}
.cat-budget-pct {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 10px;
}

.mini-bar {
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}
.mini-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}

.cat-assets-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: 1px solid var(--border-color);
  padding-top: 8px;
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #d0d5e8 transparent;
}
.cat-assets-list::-webkit-scrollbar {
  width: 4px;
}
.cat-assets-list::-webkit-scrollbar-track {
  background: transparent;
}
.cat-assets-list::-webkit-scrollbar-thumb {
  background: #d0d5e8;
  border-radius: 2px;
}
.cat-assets-list::-webkit-scrollbar-thumb:hover {
  background: #a0aac8;
}

.cat-asset-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: background var(--transition);
}
.cat-asset-item:hover {
  background: #f5f6fc;
}
.cat-asset-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
}
.cat-asset-name {
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.cat-asset-cost {
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}
.cat-asset-cost.cost-estimated {
  color: #f59e0b;
}

.asset-prog-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}
.asset-prog-track {
  flex: 1;
  height: 3px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}
.asset-prog-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}
.prog-ok   { background: #10b981; }
.prog-warn { background: #f59e0b; }
.asset-prog-label {
  font-size: 10px;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}


.empty-cards {
  text-align: center;
  padding: 60px 0;
  color: var(--text-muted);
  font-size: 14px;
}

/* Dispose form */
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

  .toolbar-left, .toolbar-right {
    width: 100%;
  }

  .toolbar-right {
    justify-content: space-between;
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

  .cat-grid {
    grid-template-columns: 1fr;
  }
}
</style>

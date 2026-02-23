<template>
  <div class="settings-page">
    <!-- 分类管理模块 -->
    <div class="module-card">
      <div class="module-header">
        <div class="header-main">
          <span class="module-tag">Category</span>
          <h3 class="module-title">分类管理</h3>
          <p class="module-desc">维护资产分类，可为每个分类设置每日预算，供资产录入和筛选使用。</p>

          <div class="kpi-row">
            <div class="kpi-chip">
              <div class="kpi-icon-box" style="--kpi-color: #4f6ef7; --kpi-bg: rgba(79,110,247,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path d="M1 2.5A1.5 1.5 0 012.5 1h3A1.5 1.5 0 017 2.5v3A1.5 1.5 0 015.5 7h-3A1.5 1.5 0 011 5.5v-3zm8 0A1.5 1.5 0 0110.5 1h3A1.5 1.5 0 0115 2.5v3A1.5 1.5 0 0113.5 7h-3A1.5 1.5 0 019 5.5v-3zm-8 8A1.5 1.5 0 012.5 9h3A1.5 1.5 0 017 10.5v3A1.5 1.5 0 015.5 15h-3A1.5 1.5 0 011 13.5v-3zm8 0A1.5 1.5 0 0110.5 9h3a1.5 1.5 0 011.5 1.5v3a1.5 1.5 0 01-1.5 1.5h-3A1.5 1.5 0 019 13.5v-3z"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ totalCategoryCount }}</strong>
                <span class="kpi-label">分类总数</span>
              </div>
            </div>

            <div class="kpi-chip">
              <div class="kpi-icon-box" style="--kpi-color: #7c5cfc; --kpi-bg: rgba(124,92,252,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M4 1h8a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1zm1 3v1h6V4H5zm0 3v1h6V7H5zm0 3v1h4v-1H5z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ totalAssetLinkedCount }}</strong>
                <span class="kpi-label">已关联资产</span>
              </div>
            </div>

            <div class="kpi-chip">
              <div class="kpi-icon-box" style="--kpi-color: #10b981; --kpi-bg: rgba(16,185,129,0.1)">
                <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M8 1a7 7 0 100 14A7 7 0 008 1zm-.5 4.5a.5.5 0 011 0v.612c.61.152 1.25.586 1.25 1.388 0 .77-.574 1.23-1.25 1.4v1.6c.39-.102.625-.324.625-.625a.5.5 0 011 0c0 .905-.737 1.48-1.625 1.609V11.5a.5.5 0 01-1 0v-.516C6.637 10.83 6 10.264 6 9.5c0-.77.574-1.23 1.25-1.4V6.5c-.39.102-.625.324-.625.625a.5.5 0 01-1 0c0-.905.737-1.48 1.625-1.609V5.5z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="kpi-body">
                <strong class="kpi-num">{{ budgetConfiguredCount }}</strong>
                <span class="kpi-label">已设置预算</span>
              </div>
            </div>
          </div>
        </div>

        <button class="btn-primary" @click="handleAddCategory">
          <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14">
            <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/>
          </svg>
          新建分类
        </button>
      </div>

      <div class="table-wrap" v-loading="loading">
        <table class="data-table" v-if="categories.length">
          <thead>
            <tr>
              <th class="order-col">#</th>
              <th class="name-col">分类名称</th>
              <th class="qty-col">资产数量</th>
              <th class="budget-col">日预算（元/天）</th>
              <th class="actions-col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(cat, idx) in categories" :key="cat.id">
              <td class="order-col">
                <span class="order-badge">{{ idx + 1 }}</span>
              </td>
              <td class="name-col">
                <div class="cat-name-row">
                  <span class="cat-dot" :style="{ background: getCategoryColor(cat.name) }"></span>
                  <span class="cat-name">{{ cat.name }}</span>
                </div>
              </td>
              <td class="qty-col">
                <span class="count-badge" :class="{ active: usageCount(cat.id) > 0 }">
                  {{ usageCount(cat.id) }} 项
                </span>
              </td>
              <td class="budget-col">
                <span v-if="hasBudget(cat)" class="budget-badge">
                  ¥{{ formatBudget(cat.daily_budget) }}<span class="budget-unit">/天</span>
                </span>
                <span v-else class="no-budget">未设置</span>
              </td>
              <td class="actions-col">
                <div class="action-btns">
                  <button class="action-btn" @click="handleRenameCategory(cat)">
                    <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                      <path d="M9.5 1.5L12.5 4.5L5 12H2V9L9.5 1.5Z" stroke-linejoin="round"/>
                    </svg>
                    重命名
                  </button>
                  <button class="action-btn budget" @click="handleSetBudget(cat)">
                    <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                      <circle cx="7" cy="7" r="5.5"/>
                      <path d="M7 3.5v.5m0 6v.5M5.5 5.5C5.5 4.67 6.17 4 7 4s1.5.67 1.5 1.5S7.83 7 7 7s-1.5.67-1.5 1.5S6.17 10 7 10s1.5-.67 1.5-1.5" stroke-linecap="round"/>
                    </svg>
                    预算
                  </button>
                  <button class="action-btn danger" @click="handleDeleteCategory(cat)">
                    <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                      <path d="M2 3.5h10M5 3.5V2h4v1.5M3 3.5l.75 8h6.5L11 3.5" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M5.5 6v3.5M8.5 6v3.5" stroke-linecap="round"/>
                    </svg>
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">
          <div class="empty-visual">
            <svg viewBox="0 0 96 80" fill="none" width="96" height="80">
              <rect x="14" y="8" width="52" height="58" rx="5" fill="#eef1fb" stroke="#d0d8f3" stroke-width="1.5"/>
              <rect x="22" y="20" width="22" height="3" rx="1.5" fill="#bcc6ee"/>
              <rect x="22" y="29" width="34" height="3" rx="1.5" fill="#ccd3f0"/>
              <rect x="22" y="38" width="28" height="3" rx="1.5" fill="#ccd3f0"/>
              <rect x="22" y="47" width="18" height="3" rx="1.5" fill="#ccd3f0"/>
              <circle cx="68" cy="60" r="18" fill="#4f6ef7"/>
              <rect x="61" y="58.75" width="14" height="2.5" rx="1.25" fill="white"/>
              <rect x="66.75" y="52" width="2.5" height="16" rx="1.25" fill="white"/>
            </svg>
          </div>
          <p class="empty-title">暂无分类</p>
          <p class="empty-desc">点击右上角「新建分类」开始创建</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createCategory, deleteCategory, getAssets, getCategories, updateCategory } from '../api'

const categories = ref([])
const assetsByCategory = ref({})
const loading = ref(false)

const categoryNames = computed(() => new Set(categories.value.map((x) => x.name.trim())))
const totalCategoryCount = computed(() => categories.value.length)
const totalAssetLinkedCount = computed(() =>
  Object.values(assetsByCategory.value).reduce((sum, count) => sum + Number(count || 0), 0)
)
const budgetConfiguredCount = computed(() =>
  categories.value.filter((cat) => hasBudget(cat)).length
)

const CATEGORY_COLORS = ['#4f6ef7', '#7c5cfc', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899']

function getCategoryColor(name) {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return CATEGORY_COLORS[Math.abs(hash) % CATEGORY_COLORS.length]
}

function usageCount(categoryId) {
  return assetsByCategory.value[categoryId] || 0
}

function hasBudget(category) {
  return category.daily_budget !== null && category.daily_budget !== undefined && category.daily_budget !== ''
}

function formatBudget(value) {
  return Number(value).toFixed(2)
}

async function loadData() {
  loading.value = true
  try {
    const [categoryRes, assetsRes] = await Promise.all([getCategories(), getAssets()])
    categories.value = categoryRes.data
    const usage = {}
    for (const item of assetsRes.data) {
      usage[item.category_id] = (usage[item.category_id] || 0) + 1
    }
    assetsByCategory.value = usage
  } catch (error) {
    console.error(error)
    ElMessage.error('设置数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function handleAddCategory() {
  try {
    const { value } = await ElMessageBox.prompt('请输入分类名称', '新建分类', {
      inputPlaceholder: '例如：平板电脑',
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputValidator: (raw) => {
        const v = (raw || '').trim()
        if (!v) return '分类名称不能为空'
        if (v.length > 50) return '分类名称不能超过 50 个字符'
        if (categoryNames.value.has(v)) return '分类已存在'
        return true
      },
    })

    await createCategory({ name: value.trim() })
    ElMessage.success('分类已创建')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '创建分类失败')
  }
}

async function handleRenameCategory(category) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的分类名称', '重命名分类', {
      inputValue: category.name,
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValidator: (raw) => {
        const v = (raw || '').trim()
        if (!v) return '分类名称不能为空'
        if (v.length > 50) return '分类名称不能超过 50 个字符'
        if (v !== category.name && categoryNames.value.has(v)) return '分类已存在'
        return true
      },
    })

    const name = value.trim()
    if (name === category.name) return

    await updateCategory(category.id, { name })
    ElMessage.success('分类已更新')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '更新分类失败')
  }
}

async function handleSetBudget(category) {
  const currentBudget = category.daily_budget ? Number(category.daily_budget).toFixed(2) : ''
  try {
    const { value } = await ElMessageBox.prompt(
      `为「${category.name}」设置每日预算，留空表示不限制预算。`,
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
    await updateCategory(category.id, { daily_budget })
    ElMessage.success('预算已更新')
    await loadData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '更新预算失败')
  }
}

async function handleDeleteCategory(category) {
  const used = usageCount(category.id)
  if (used > 0) {
    ElMessage.warning(`该分类下还有 ${used} 条资产，无法删除`)
    return
  }

  try {
    await ElMessageBox.confirm(`确认删除分类"${category.name}"？`, '删除分类', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    await deleteCategory(category.id)
    ElMessage.success('分类已删除')
    await loadData()
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '删除分类失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
/* ── 页面整体布局 ── */
.settings-page {
  width: 100%;
  max-width: 1080px;
}

/* ── 模块卡片 ── */
.module-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.module-header {
  padding: 22px 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, rgba(79, 110, 247, 0.04) 0%, transparent 55%);
}

.header-main {
  min-width: 0;
  flex: 1;
}

.module-tag {
  display: inline-block;
  border: 1px solid rgba(79, 110, 247, 0.28);
  color: #3551cf;
  background: rgba(79, 110, 247, 0.07);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.9px;
  text-transform: uppercase;
  padding: 2px 8px;
  margin-bottom: 8px;
}

.module-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-primary);
}

.module-desc {
  margin-top: 5px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.55;
}

/* ── KPI 统计条 ── */
.kpi-row {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.kpi-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 12px;
  padding: 8px 14px 8px 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.kpi-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--kpi-bg);
  color: var(--kpi-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.kpi-num {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.kpi-label {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1;
}

/* ── 主按钮 ── */
.btn-primary {
  border: none;
  background: var(--accent-gradient);
  color: #fff;
  border-radius: var(--radius-sm);
  height: 38px;
  padding: 0 16px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: filter var(--transition), transform var(--transition), box-shadow var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(79, 110, 247, 0.28);
}

.btn-primary:hover {
  filter: brightness(1.07);
  transform: translateY(-1px);
  box-shadow: 0 5px 16px rgba(79, 110, 247, 0.38);
}

/* ── 表格 ── */
.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  min-width: 560px;
}

.data-table th {
  padding: 11px 16px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  background: #f8f9fd;
  text-transform: uppercase;
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background var(--transition);
}

.data-table tbody tr:hover {
  background: #f5f8ff;
}

.data-table tr:last-child td {
  border-bottom: none;
}

/* 列宽 */
.order-col  { width: 60px; text-align: center; }
.name-col   { width: auto; }
.qty-col    { width: 110px; }
.budget-col { width: 168px; }
.actions-col { width: 220px; }

.data-table th.order-col,
.data-table td.order-col {
  text-align: center;
  padding-left: 0;
  padding-right: 0;
}

.data-table th.actions-col,
.data-table td.actions-col {
  text-align: center;
}

/* ── 单元格元素 ── */
.order-badge {
  display: inline-flex;
  width: 26px;
  height: 26px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #eef2ff;
  color: #3f5bd0;
  font-size: 11px;
  font-weight: 700;
}

.cat-name-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.cat-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  flex-shrink: 0;
}

.cat-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  min-width: 58px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: #fff;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.count-badge.active {
  border-color: rgba(79, 110, 247, 0.22);
  background: rgba(79, 110, 247, 0.06);
  color: #3551cf;
}

.budget-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.08);
  color: #059669;
  border-radius: 999px;
  border: 1px solid rgba(16, 185, 129, 0.22);
  font-size: 13px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.budget-unit {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.65;
}

.no-budget {
  font-size: 13px;
  color: var(--text-muted);
}

/* ── 操作按钮 ── */
.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  border-radius: 8px;
  height: 28px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-light);
}

.action-btn.budget:hover {
  border-color: #059669;
  color: #059669;
  background: rgba(16, 185, 129, 0.07);
}

.action-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: var(--danger-light);
}

/* ── 空状态 ── */
.empty-state {
  padding: 56px 24px;
  text-align: center;
}

.empty-visual {
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-muted);
}

/* ── 响应式 ── */
@media (max-width: 860px) {
  .settings-page {
    width: 100%;
  }

  .module-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn-primary {
    align-self: stretch;
    justify-content: center;
  }

  .actions-col {
    width: 200px;
  }
}
</style>

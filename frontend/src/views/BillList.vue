<template>
  <div class="bill-list-page">
    <!-- 顶部：月份切换 + 收支合计 -->
    <div class="page-header">
      <div class="month-nav">
        <button class="nav-btn" @click="prevMonth">
          <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M9.78 12.78a.75.75 0 01-1.06 0L4.47 8.53a.75.75 0 010-1.06l4.25-4.25a.75.75 0 011.06 1.06L6.06 8l3.72 3.72a.75.75 0 010 1.06z"/></svg>
        </button>
        <span class="month-label">{{ currentYear }} 年 {{ currentMonth }} 月</span>
        <button class="nav-btn" @click="nextMonth" :disabled="isCurrentMonth">
          <svg viewBox="0 0 16 16" fill="currentColor" width="16" height="16"><path d="M6.22 3.22a.75.75 0 011.06 0l4.25 4.25a.75.75 0 010 1.06l-4.25 4.25a.75.75 0 01-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 010-1.06z"/></svg>
        </button>
      </div>

      <div class="summary-row">
        <div class="summary-chip expense">
          <span class="summary-label">支出</span>
          <span class="summary-amount">¥{{ formatAmount(summary.total_expense) }}</span>
        </div>
        <div class="summary-chip income">
          <span class="summary-label">收入</span>
          <span class="summary-amount">¥{{ formatAmount(summary.total_income) }}</span>
        </div>
        <div class="summary-chip net">
          <span class="summary-label">结余</span>
          <span class="summary-amount" :class="netAmount >= 0 ? 'pos' : 'neg'">
            {{ netAmount >= 0 ? '+' : '' }}¥{{ formatAmount(Math.abs(netAmount)) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 交易列表 -->
    <div class="list-card" v-loading="loading">
      <div v-if="groupedTransactions.length === 0 && !loading" class="empty-state">
        <svg viewBox="0 0 80 60" fill="none" width="80" height="60">
          <rect x="8" y="4" width="48" height="52" rx="4" fill="#eef1fb" stroke="#d0d8f3" stroke-width="1.5"/>
          <rect x="16" y="14" width="20" height="2.5" rx="1.25" fill="#bcc6ee"/>
          <rect x="16" y="21" width="30" height="2.5" rx="1.25" fill="#ccd3f0"/>
          <rect x="16" y="28" width="24" height="2.5" rx="1.25" fill="#ccd3f0"/>
          <circle cx="60" cy="46" r="14" fill="#4f6ef7"/>
          <rect x="53" y="45.25" width="14" height="1.5" rx="0.75" fill="white"/>
          <rect x="59.25" y="39" width="1.5" height="14" rx="0.75" fill="white"/>
        </svg>
        <p class="empty-title">本月暂无记账</p>
        <p class="empty-desc">点击右下角按钮添加一笔</p>
      </div>

      <div v-for="group in groupedTransactions" :key="group.date" class="date-group">
        <div class="date-header">
          <span class="date-label">{{ formatDate(group.date) }}</span>
          <span class="date-total" :class="group.netExpense > 0 ? 'expense' : 'income'">
            {{ group.netExpense > 0 ? '-' : '+' }}¥{{ formatAmount(Math.abs(group.netExpense)) }}
          </span>
        </div>

        <div v-for="tx in group.items" :key="tx.id" class="tx-row">
          <div class="tx-cat">
            <span class="cat-dot" :style="{ background: getCategoryColor(tx.category_name || '其他') }"></span>
            <div class="tx-cat-labels">
              <span class="tx-cat-main">{{ tx.parent_category_name || tx.category_name || '未分类' }}</span>
              <span v-if="tx.parent_category_name && tx.category_name" class="tx-cat-sub">{{ tx.category_name }}</span>
            </div>
          </div>
          <div class="tx-notes">{{ tx.notes || '' }}</div>
          <div class="tx-right">
            <span class="tx-method" v-if="tx.payment_method">{{ tx.payment_method }}</span>
            <span class="tx-amount" :class="tx.type === 'expense' ? 'expense' : 'income'">
              {{ tx.type === 'expense' ? '-' : '+' }}¥{{ formatAmount(tx.amount) }}
            </span>
            <div class="tx-actions">
              <button class="icon-btn" @click="editTransaction(tx)" title="编辑">
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                  <path d="M9.5 1.5L12.5 4.5L5 12H2V9L9.5 1.5Z" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="icon-btn danger" @click="handleDelete(tx)" title="删除">
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" width="12" height="12">
                  <path d="M2 3.5h10M5 3.5V2h4v1.5M3 3.5l.75 8h6.5L11 3.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FAB -->
    <button class="fab" @click="addTransaction" title="新增记账">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="22" height="22">
        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTransactions, getTransactionSummary, deleteTransaction } from '../api'

const router = useRouter()

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)

const transactions = ref([])
const summary = ref({ total_expense: 0, total_income: 0 })
const loading = ref(false)

const isCurrentMonth = computed(() => {
  const n = new Date()
  return currentYear.value === n.getFullYear() && currentMonth.value === n.getMonth() + 1
})

const netAmount = computed(() => Number(summary.value.total_income) - Number(summary.value.total_expense))

// Group transactions by date
const groupedTransactions = computed(() => {
  const map = {}
  for (const tx of transactions.value) {
    const d = tx.date
    if (!map[d]) map[d] = { date: d, items: [], netExpense: 0 }
    map[d].items.push(tx)
    if (tx.type === 'expense') map[d].netExpense += Number(tx.amount)
    else map[d].netExpense -= Number(tx.amount)
  }
  return Object.values(map).sort((a, b) => b.date.localeCompare(a.date))
})

const CATEGORY_COLORS = ['#4f6ef7', '#7c5cfc', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899']
function getCategoryColor(name) {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return CATEGORY_COLORS[Math.abs(hash) % CATEGORY_COLORS.length]
}

function formatAmount(val) {
  return Number(val || 0).toFixed(2)
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  const month = d.getMonth() + 1
  const day = d.getDate()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${month}月${day}日 周${weekdays[d.getDay()]}`
}

async function loadData() {
  loading.value = true
  try {
    const params = { year: currentYear.value, month: currentMonth.value }
    const [txRes, sumRes] = await Promise.all([
      getTransactions(params),
      getTransactionSummary(params),
    ])
    transactions.value = txRes.data
    summary.value = sumRes.data
  } catch (e) {
    console.error(e)
    ElMessage.error('加载记账数据失败')
  } finally {
    loading.value = false
  }
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value -= 1
  } else {
    currentMonth.value -= 1
  }
}

function nextMonth() {
  if (isCurrentMonth.value) return
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value += 1
  } else {
    currentMonth.value += 1
  }
}

function addTransaction() {
  router.push('/bills/new')
}

function editTransaction(tx) {
  router.push(`/bills/${tx.id}/edit`)
}

async function handleDelete(tx) {
  try {
    await ElMessageBox.confirm('确认删除该条记账？', '删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch { return }

  try {
    await deleteTransaction(tx.id)
    ElMessage.success('已删除')
    await loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

watch([currentYear, currentMonth], loadData)
onMounted(loadData)
</script>

<style scoped>
.bill-list-page {
  width: 100%;
  max-width: 860px;
  padding-bottom: 80px;
  position: relative;
}

.page-header {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}

.month-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.month-label {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 120px;
  text-align: center;
}

.nav-btn {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition);
}
.nav-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.nav-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.summary-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-chip {
  flex: 1;
  min-width: 120px;
  padding: 12px 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-chip.expense { background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.15); }
.summary-chip.income  { background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.15); }
.summary-chip.net     { background: rgba(79,110,247,0.06); border: 1px solid rgba(79,110,247,0.15); }

.summary-label { font-size: 12px; color: var(--text-muted); font-weight: 500; }
.summary-amount { font-size: 20px; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--text-primary); }
.summary-chip.expense .summary-amount { color: var(--danger); }
.summary-chip.income  .summary-amount { color: var(--success); }
.pos { color: var(--success) !important; }
.neg { color: var(--danger) !important; }

.list-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.date-group { }

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #f8f9fd;
  border-bottom: 1px solid var(--border-color);
}

.date-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); }
.date-total { font-size: 13px; font-weight: 600; }
.date-total.expense { color: var(--danger); }
.date-total.income  { color: var(--success); }

.tx-row {
  display: flex;
  align-items: center;
  padding: 13px 20px;
  border-bottom: 1px solid var(--border-color);
  gap: 12px;
  transition: background var(--transition);
}
.tx-row:last-child { border-bottom: none; }
.tx-row:hover { background: #f8f9fd; }

.tx-cat {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 110px;
}

.cat-dot { width: 9px; height: 9px; border-radius: 999px; flex-shrink: 0; }

.tx-cat-labels { display: flex; flex-direction: column; }
.tx-cat-main { font-size: 13.5px; font-weight: 600; color: var(--text-primary); }
.tx-cat-sub  { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

.tx-notes {
  flex: 1;
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tx-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.tx-method {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 5px;
  background: var(--bg-primary);
  color: var(--text-muted);
  border: 1px solid var(--border-color);
}

.tx-amount {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  min-width: 80px;
  text-align: right;
}
.tx-amount.expense { color: var(--danger); }
.tx-amount.income  { color: var(--success); }

.tx-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition);
}
.tx-row:hover .tx-actions { opacity: 1; }

.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 5px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  transition: color var(--transition), background var(--transition);
}
.icon-btn:hover { color: var(--accent); background: var(--accent-light); }
.icon-btn.danger:hover { color: var(--danger); background: var(--danger-light); }

.empty-state {
  padding: 60px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.empty-title { font-size: 15px; font-weight: 600; color: var(--text-secondary); }
.empty-desc  { font-size: 13px; color: var(--text-muted); }

/* FAB */
.fab {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 52px;
  height: 52px;
  border-radius: 999px;
  background: var(--accent-gradient);
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.45);
  transition: transform var(--transition), box-shadow var(--transition);
  z-index: 50;
}
.fab:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 26px rgba(79, 110, 247, 0.55);
}
</style>

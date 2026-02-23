<template>
  <div v-if="asset" class="detail-page">
    <div class="detail-header">
      <button class="back-btn" @click="$router.push('/assets')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
      </button>
      <div class="header-info">
        <div class="header-avatar" :style="{ background: 'var(--accent)' }">{{ asset.name.charAt(0) }}</div>
        <div>
          <h2>{{ asset.name }}</h2>
          <div class="header-meta">
            <span class="cat-tag">{{ asset.category_name }}</span>
            <span class="status-badge" :class="asset.status">
              {{ { active: '使用中', disposed: '已弃用' }[asset.status] || asset.status }}
            </span>
            <span class="channel-tag" v-if="asset.purchase_channel">{{ asset.purchase_channel }}</span>
          </div>
        </div>
      </div>
      <button class="btn-edit" @click="$router.push(`/assets/${asset.id}/edit`)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
        编辑
      </button>
    </div>

    <div class="value-grid">
      <div class="value-card primary">
        <span class="value-label">购买价格</span>
        <span class="value-amount">{{ formatMoney(asset.purchase_price) }}</span>
      </div>
      <div class="value-card">
        <span class="value-label">回收金额</span>
        <span class="value-amount">{{ asset.recovery_amount !== null ? formatMoney(asset.recovery_amount) : '-' }}</span>
      </div>
      <div class="value-card">
        <span class="value-label">实际费用</span>
        <span class="value-amount net">{{ formatMoney(asset.net_cost) }}</span>
      </div>
      <div class="value-card">
        <span class="value-label">日均费用</span>
        <span class="value-amount" :class="dailyCostClass">{{ formatDaily(asset.daily_cost) }}</span>
      </div>
    </div>

    <div class="section-card">
      <h3 class="section-title">资产详情</h3>
      <div class="info-list">
        <div class="info-row"><span class="info-label">购买日期</span><span>{{ asset.purchase_date }}</span></div>
        <div class="info-row" v-if="asset.purchase_channel"><span class="info-label">购买渠道</span><span>{{ asset.purchase_channel }}</span></div>
        <div class="info-row"><span class="info-label">使用状态</span><span>{{ asset.status === 'active' ? '使用中' : '已弃用' }}</span></div>
        <div class="info-row"><span class="info-label">使用天数</span><span>{{ asset.days_used }} 天</span></div>
        <div class="info-row" v-if="asset.disposed_date"><span class="info-label">弃用日期</span><span>{{ asset.disposed_date }}</span></div>
        <div class="info-row" v-if="asset.disposed_reason"><span class="info-label">弃用原因</span><span>{{ asset.disposed_reason }}</span></div>
        <div class="info-row" v-if="asset.recovery_date"><span class="info-label">回收日期</span><span>{{ asset.recovery_date }}</span></div>
        <div class="info-row" v-if="asset.notes"><span class="info-label">备注</span><span>{{ asset.notes }}</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAsset } from '../api'

const route = useRoute()
const asset = ref(null)

function formatMoney(v) {
  return `¥${Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function formatDaily(v) {
  return `¥${Number(v || 0).toFixed(2)}/天`
}

const dailyCostClass = computed(() => {
  if (!asset.value) return ''
  const v = Number(asset.value.daily_cost)
  if (v >= 5) return 'danger'
  if (v >= 3) return 'warn'
  return ''
})

onMounted(async () => {
  const res = await getAsset(route.params.id)
  asset.value = res.data
})
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.back-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  flex-shrink: 0;
  transition: var(--transition);
}
.back-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
}
.header-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 18px;
}
.header-info h2 {
  font-size: 20px;
  font-weight: 700;
}
.header-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  align-items: center;
}

.cat-tag {
  padding: 2px 10px;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}
.channel-tag {
  padding: 2px 10px;
  background: #f0f9ff;
  color: #0284c7;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}
.status-badge {
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
}
.status-badge.active {
  background: var(--success-light);
  color: var(--success);
}
.status-badge.disposed {
  background: #f3f4f6;
  color: var(--text-secondary);
}

.btn-edit {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.btn-edit:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.value-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.value-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.value-card.primary {
  background: var(--accent);
  border-color: var(--accent);
}
.value-card.primary .value-label {
  color: rgba(255, 255, 255, 0.75);
}
.value-card.primary .value-amount {
  color: #fff;
}
.value-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}
.value-amount {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.value-amount.net {
  color: #0f766e;
}
.value-amount.warn {
  color: var(--warning);
}
.value-amount.danger {
  color: var(--danger);
}

.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 20px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.info-list {
  display: flex;
  flex-direction: column;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}
.info-row:last-child {
  border-bottom: none;
}
.info-label {
  color: var(--text-secondary);
  font-weight: 500;
}

@media (max-width: 1000px) {
  .value-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 700px) {
  .value-grid {
    grid-template-columns: 1fr;
  }
}
</style>
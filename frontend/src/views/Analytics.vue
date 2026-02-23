<template>
  <div class="analytics-page">
    <!-- Summary Cards -->
    <div class="summary-grid">
      <div class="summary-card" v-for="(item, i) in summaryCards" :key="i">
        <span class="summary-label">{{ item.label }}</span>
        <span class="summary-value" :style="{ color: item.color }">{{ item.value }}</span>
      </div>
    </div>

    <!-- Trend Chart -->
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">月度日均费用趋势</h3>
        <p class="section-desc">展示各月末在用资产的日均总费用变化</p>
      </div>
      <TrendChart :data="trendData" height="400px" />
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">分类每日成本</h3>
        </div>
        <CategoryPie :data="categoryData" height="340px" />
      </div>
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">日均费用排行 Top 10</h3>
        </div>
        <DailyCostChart :assets="assets" height="340px" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDailyCostTrend, getCategoryDistribution, getCostSummary, getAssets } from '../api'
import TrendChart from '../components/TrendChart.vue'
import CategoryPie from '../components/CategoryPie.vue'
import DailyCostChart from '../components/DailyCostChart.vue'

const trendData = ref([])
const categoryData = ref([])
const summary = ref({ total_purchase: 0, total_daily_cost: 0, avg_daily_cost: 0, active_count: 0, disposed_count: 0 })
const assets = ref([])

const fmt = (v) => Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const summaryCards = computed(() => [
  { label: '使用中资产购入总额', value: '¥' + fmt(summary.value.total_purchase), color: 'var(--text-primary)' },
  { label: '日均总费用', value: '¥' + fmt(summary.value.total_daily_cost), color: 'var(--accent)' },
  { label: '平均日费用', value: '¥' + fmt(summary.value.avg_daily_cost), color: 'var(--warning)' },
  { label: '在用/已弃用', value: `${summary.value.active_count} / ${summary.value.disposed_count}`, color: 'var(--text-secondary)' },
])

async function load() {
  const [t, c, s, a] = await Promise.all([
    getDailyCostTrend(),
    getCategoryDistribution(),
    getCostSummary(),
    getAssets({ status: 'active' }),
  ])
  trendData.value = t.data
  categoryData.value = c.data
  summary.value = s.data
  assets.value = a.data
}

onMounted(load)
</script>

<style scoped>
.summary-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  margin-bottom: 24px;
}
.summary-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: var(--radius); padding: 20px 24px;
  display: flex; flex-direction: column; gap: 8px;
  transition: box-shadow var(--transition);
}
.summary-card:hover { box-shadow: var(--shadow-md); }
.summary-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.summary-value { font-size: 24px; font-weight: 700; font-variant-numeric: tabular-nums; }

.section-card {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: var(--radius); padding: 24px; margin-bottom: 24px;
  transition: box-shadow var(--transition);
}
.section-card:hover { box-shadow: var(--shadow-md); }
.section-header { margin-bottom: 20px; }
.section-title { font-size: 16px; font-weight: 600; }
.section-desc { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

.charts-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px;
}
.charts-grid .section-card { margin-bottom: 0; }

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>

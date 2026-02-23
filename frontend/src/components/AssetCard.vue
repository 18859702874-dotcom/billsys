<template>
  <div class="asset-card" @click="$router.push(`/assets/${asset.id}`)">
    <div class="card-left">
      <div class="card-avatar">{{ asset.name.charAt(0) }}</div>
      <div class="card-info">
        <span class="card-name">{{ asset.name }}</span>
        <span class="card-cat">{{ asset.category_name }}</span>
      </div>
    </div>
    <div class="card-right">
      <span class="card-price">¥{{ Number(asset.purchase_price).toLocaleString('zh-CN', {minimumFractionDigits:2}) }}</span>
      <span class="card-daily" :class="dailyCostClass">
        ¥{{ Number(asset.daily_cost).toFixed(2) }}/天
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ asset: { type: Object, required: true } })

const dailyCostClass = computed(() => {
  const v = Number(props.asset.daily_cost)
  if (v >= 5) return 'high'
  if (v >= 3) return 'mid'
  return 'low'
})
</script>

<style scoped>
.asset-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition);
  border: 1px solid transparent;
}
.asset-card:hover {
  background: var(--bg-primary);
  border-color: var(--border-color);
}

.card-left { display: flex; align-items: center; gap: 12px; }
.card-avatar {
  width: 34px; height: 34px; border-radius: 9px;
  background: var(--accent-light); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 13px; flex-shrink: 0;
}
.card-info { display: flex; flex-direction: column; }
.card-name { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.card-cat { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

.card-right { text-align: right; display: flex; flex-direction: column; }
.card-price { font-size: 14px; font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.card-daily { font-size: 11px; font-weight: 500; margin-top: 1px; }
.card-daily.low { color: var(--success); }
.card-daily.mid { color: var(--warning); }
.card-daily.high { color: var(--danger); }
</style>

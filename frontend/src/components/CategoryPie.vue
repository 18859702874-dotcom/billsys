<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '300px' },
})

const colors = ['#4f6ef7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
const chartRef = ref(null)
let chart = null

const fmt = (v) => Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function render() {
  if (!chart || !props.data.length) return

  const sorted = [...props.data].sort((a, b) => Number(b.total_daily_cost) - Number(a.total_daily_cost))
  const categories = sorted.map(d => d.category_name)
  const values = sorted.map(d => Number(d.total_daily_cost))

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(26,29,46,.92)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 13 },
      formatter(params) {
        const p = params[0]
        const cat = sorted[p.dataIndex]
        if (!cat) return ''
        let html = `<div style="font-weight:600;margin-bottom:6px">${cat.category_name}` +
          `<span style="float:right;margin-left:20px">¥${fmt(cat.total_daily_cost)}/天</span></div>`
        if (cat.assets && cat.assets.length) {
          html += '<div style="border-top:1px solid rgba(255,255,255,.15);padding-top:6px">'
          for (const item of cat.assets) {
            html += `<div style="display:flex;justify-content:space-between;gap:16px;line-height:1.8">`
              + `<span style="color:rgba(255,255,255,.8)">${item.name}</span>`
              + `<span>¥${fmt(item.daily_cost)}</span></div>`
          }
          html += '</div>'
        }
        return html
      },
    },
    grid: {
      left: 12,
      right: 24,
      top: 12,
      bottom: 0,
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: '#9ca3af',
        fontSize: 12,
        formatter: v => '¥' + v,
      },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,.06)' } },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true,
      axisLabel: {
        color: '#4b5563',
        fontSize: 13,
        fontWeight: 500,
      },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: colors[i % colors.length] },
            { offset: 1, color: colors[i % colors.length] + 'aa' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barMaxWidth: 28,
      label: {
        show: true,
        position: 'right',
        color: '#6b7280',
        fontSize: 12,
        formatter: p => '¥' + fmt(p.value) + '/天',
      },
    }],
  })
}

const resizeHandler = () => chart?.resize()

onMounted(() => {
  chart = echarts.init(chartRef.value)
  render()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeHandler)
  chart?.dispose()
})

watch(() => props.data, render, { deep: true })
</script>

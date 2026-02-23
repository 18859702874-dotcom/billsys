<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  assets: { type: Array, default: () => [] },
  height: { type: String, default: '300px' },
})

const chartRef = ref(null)
let chart = null

function render() {
  if (!chart || !props.assets.length) return
  const sorted = [...props.assets].sort((a, b) => Number(b.daily_cost) - Number(a.daily_cost)).slice(0, 10)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,29,46,.92)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 13 },
      formatter: (p) => `${p[0].name}<br/>日均费用: ¥${Number(p[0].value).toFixed(2)}/天`,
    },
    xAxis: {
      type: 'category',
      data: sorted.map(a => a.name),
      axisLabel: { rotate: 30, fontSize: 11, color: '#9ca3af' },
      axisLine: { lineStyle: { color: '#e8ecf1' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v) => '¥' + v.toFixed(1), fontSize: 11, color: '#9ca3af' },
      splitLine: { lineStyle: { color: '#f0f2f5', type: 'dashed' } },
    },
    series: [{
      type: 'bar',
      data: sorted.map(a => Number(a.daily_cost)),
      barWidth: '60%',
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: (p) => {
          const v = p.value
          if (v >= 5) return new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#ef4444' }, { offset: 1, color: '#fca5a5' }])
          if (v >= 3) return new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f59e0b' }, { offset: 1, color: '#fcd34d' }])
          return new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#6ee7b7' }])
        },
      },
    }],
    grid: { left: 56, right: 16, bottom: 56, top: 12 },
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

watch(() => props.assets, render, { deep: true })
</script>

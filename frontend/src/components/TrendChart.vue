<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '350px' },
})

const chartRef = ref(null)
let chart = null

function render() {
  if (!chart || !props.data.length) return
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,29,46,.92)',
      borderColor: 'transparent',
      textStyle: { color: '#fff', fontSize: 13 },
      formatter: (p) => {
        const d = props.data[p[0].dataIndex]?.date || p[0].axisValue
        const [y, m] = d.split('-')
        return `<div style="font-weight:600;margin-bottom:4px">${y}年${parseInt(m)}月</div>日均费用: ¥${Number(p[0].value).toLocaleString('zh-CN', {minimumFractionDigits:2})}`
      },
    },
    xAxis: {
      type: 'category',
      data: props.data.map(d => {
        const [y, m] = d.date.split('-')
        return `${y.slice(2)}${m.padStart(2, '0')}`
      }),
      axisLabel: { fontSize: 11, color: '#9ca3af' },
      axisLine: { lineStyle: { color: '#e8ecf1' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v) => '¥' + (v >= 10000 ? (v/10000).toFixed(1) + 'w' : v.toFixed(1)), fontSize: 11, color: '#9ca3af' },
      splitLine: { lineStyle: { color: '#f0f2f5', type: 'dashed' } },
    },
    series: [{
      type: 'line',
      data: props.data.map(d => Number(d.value)),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      showSymbol: false,
      lineStyle: { width: 3, color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
        { offset: 0, color: '#4f6ef7' },
        { offset: 1, color: '#7c5cfc' },
      ])},
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79,110,247,.2)' },
          { offset: 1, color: 'rgba(79,110,247,.01)' },
        ]),
      },
      itemStyle: { color: '#4f6ef7', borderWidth: 2 },
    }],
    dataZoom: [{
      type: 'slider',
      start: props.data.length > 72 ? (1 - 72 / props.data.length) * 100 : 0,
      end: 100,
      height: 20,
      bottom: 8,
      borderColor: 'transparent',
      backgroundColor: '#f5f5f5',
      fillerColor: 'rgba(79,110,247,.15)',
      handleStyle: { color: '#4f6ef7', borderColor: '#4f6ef7' },
      textStyle: { fontSize: 11, color: '#9ca3af' },
      dataBackground: { lineStyle: { color: '#ddd' }, areaStyle: { color: '#f0f0f0' } },
    }],
    grid: { left: 70, right: 24, bottom: 48, top: 16 },
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

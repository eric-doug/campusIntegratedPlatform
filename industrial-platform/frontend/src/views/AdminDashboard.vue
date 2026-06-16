<template>
  <div>
    <el-row :gutter="24">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <el-statistic :title="stat.label" :value="stat.value" />
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top: 24px">
      <template #header><span>数据概览</span></template>
      <div ref="chartRef" style="height: 400px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
const stats = ref([
  { label: '商品总数', value: 0 },
  { label: '今日订单', value: 0 },
  { label: '活跃供应商', value: 0 },
  { label: '待处理询价', value: 0 },
])

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value' },
    series: [
      { name: '订单数', type: 'line', data: [120, 200, 150, 80, 70, 110] },
      { name: '交易额', type: 'bar', data: [22000, 38000, 29000, 15000, 13000, 21000] },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>

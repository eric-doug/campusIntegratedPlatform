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
      <template #header><span>库存概览</span></template>
      <div ref="chartRef" style="height: 400px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getInventorySummary } from '@/api/inventory'

const chartRef = ref(null)
const stats = ref([
  { label: '仓库数', value: 0 },
  { label: 'SKU总数', value: 0 },
  { label: '库存总量', value: 0 },
  { label: '可用库存', value: 0 },
])

onMounted(async () => {
  try {
    const res = await getInventorySummary()
    if (res.data) {
      stats.value[1].value = res.data.total_skus || 0
      stats.value[2].value = res.data.total_qty || 0
      stats.value[3].value = res.data.total_available || 0
    }
  } catch (e) {}

  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value' },
    series: [
      { name: '入库量', type: 'bar', data: [300, 280, 350, 400, 380, 420] },
      { name: '出库量', type: 'bar', data: [250, 260, 300, 350, 320, 380] },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>

<template>
  <div>
    <el-row :gutter="24">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <el-statistic :title="stat.label" :value="stat.value" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="24" style="margin-top: 24px">
      <el-col :span="12">
        <el-card>
          <template #header><span>能源消耗趋势</span></template>
          <div ref="energyChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>环保排放监测</span></template>
          <div ref="emissionChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const stats = ref([
  { label: '入驻企业', value: 0 },
  { label: '能源记录', value: 0 },
  { label: '安全记录', value: 0 },
  { label: '排放预警', value: 0 },
])
const energyChartRef = ref(null)
const emissionChartRef = ref(null)

onMounted(() => {
  const energyChart = echarts.init(energyChartRef.value)
  energyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value', name: 'kWh' },
    series: [
      { name: '用电', type: 'line', data: [12000, 13000, 11000, 14000, 15000, 13500] },
      { name: '用水', type: 'line', data: [800, 850, 780, 900, 920, 870] },
    ],
  })

  const emissionChart = echarts.init(emissionChartRef.value)
  emissionChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['SO2', 'NOx', 'PM2.5', 'COD', 'VOCs'] },
    yAxis: { type: 'value', name: 'mg/m³' },
    series: [
      { name: '排放值', type: 'bar', data: [45, 62, 38, 55, 28], itemStyle: { color: '#e6a23c' } },
      { name: '限值', type: 'line', data: [60, 80, 50, 70, 40], itemStyle: { color: '#f56c6c' } },
    ],
  })

  window.addEventListener('resize', () => { energyChart.resize(); emissionChart.resize() })
})
</script>

<template>
  <div v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-card style="margin-top: 16px" v-if="report">
      <el-descriptions :column="2">
        <el-descriptions-item label="报表ID">{{ report.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ report.status }}</el-descriptions-item>
        <el-descriptions-item label="周期">{{ report.period }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <h4>填报数据</h4>
      <el-input v-model="reportData" type="textarea" :rows="10" placeholder="JSON格式的填报数据" style="margin-top: 12px" />
      <div style="margin-top: 16px">
        <el-button type="primary" @click="handleSave">保存</el-button>
        <el-button type="success" @click="handleSubmit">提交</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { updateReport } from '@/api/reports'
import { createSubmission } from '@/api/submissions'

const router = useRouter()
const route = useRoute()
const report = ref(null)
const reportData = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    // Fetch report detail from the reports list
    const { getReports } = await import('@/api/reports')
    const res = await getReports({ enterprise_id: undefined })
    const found = res.data?.items?.find(r => r.id === parseInt(route.params.id))
    if (found) {
      report.value = found
      reportData.value = JSON.stringify(found.data || {}, null, 2)
    }
  } finally { loading.value = false }
})

const handleSave = async () => {
  try {
    await updateReport(report.value.id, { data: JSON.parse(reportData.value) })
    ElMessage.success('已保存')
  } catch (e) { ElMessage.error('保存失败') }
}

const handleSubmit = async () => {
  try {
    await updateReport(report.value.id, { data: JSON.parse(reportData.value), status: 'submitted' })
    await createSubmission({ form_id: report.value.id, department: '默认部门' })
    ElMessage.success('已提交')
    router.back()
  } catch (e) { ElMessage.error('提交失败') }
}
</script>

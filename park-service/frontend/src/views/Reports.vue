<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>报表中心</span>
          <el-button type="primary" @click="showCreateDialog = true">新建报表</el-button>
        </div>
      </template>
      <el-table :data="reports" v-loading="loading" stripe>
        <el-table-column prop="template_name" label="报表模板" width="200" />
        <el-table-column prop="period" label="填报周期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/reports/${row.id}`)">填报</el-button>
            <el-button text type="success" @click="handleAiFill(row)">AI填报</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showCreateDialog" title="新建报表" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="企业ID"><el-input-number v-model="createForm.enterprise_id" /></el-form-item>
        <el-form-item label="报表模板">
          <el-select v-model="createForm.template_id">
            <el-option v-for="t in templates" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期"><el-input v-model="createForm.period" placeholder="如：2026-06" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReports, createReport, getReportTemplates } from '@/api/reports'
import { autoFill } from '@/api/ai'

const router = useRouter()
const reports = ref([])
const templates = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showCreateDialog = ref(false)
const creating = ref(false)
const statusMap = { draft: '草稿', submitted: '已提交', approved: '已审核' }
const statusType = { draft: 'info', submitted: 'warning', approved: 'success' }
const createForm = reactive({ enterprise_id: null, template_id: null, period: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getReports({ page: page.value })
    reports.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createReport(createForm)
    ElMessage.success('报表已创建')
    showCreateDialog.value = false
    loadData()
  } finally { creating.value = false }
}

const handleAiFill = async (row) => {
  try {
    const res = await autoFill({ template_id: row.template_id, enterprise_id: row.enterprise_id, period: row.period })
    ElMessage.success('AI填报完成')
  } catch (e) {}
}

onMounted(async () => {
  loadData()
  try {
    const res = await getReportTemplates()
    templates.value = res.data || []
  } catch (e) {}
})
</script>

<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>安全生产</span>
          <el-button type="primary" @click="showDialog = true">录入记录</el-button>
        </div>
      </template>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="enterprise_id" label="企业ID" width="100" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="incident_date" label="发生日期" width="120" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType[row.severity] || 'info'">{{ row.severity || '--' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showDialog" title="录入安全记录" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="企业ID"><el-input-number v-model="form.enterprise_id" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="form.type" /></el-form-item>
        <el-form-item label="发生日期"><el-date-picker v-model="form.incident_date" type="date" /></el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="form.severity">
            <el-option value="low" label="低" /><el-option value="medium" label="中" /><el-option value="high" label="高" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="措施"><el-input v-model="form.measures" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">录入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSafetyRecords, createSafetyRecord } from '@/api/safety'

const records = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showDialog = ref(false)
const creating = ref(false)
const severityType = { low: 'success', medium: 'warning', high: 'danger' }
const form = reactive({ enterprise_id: null, type: '', incident_date: '', severity: 'low', description: '', measures: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSafetyRecords({ page: page.value })
    records.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createSafetyRecord(form)
    ElMessage.success('记录已录入')
    showDialog.value = false
    loadData()
  } finally { creating.value = false }
}

onMounted(() => loadData())
</script>

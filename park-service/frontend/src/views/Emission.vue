<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>环保排放</span>
          <el-button type="primary" @click="showDialog = true">录入数据</el-button>
        </div>
      </template>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="enterprise_id" label="企业ID" width="100" />
        <el-table-column prop="type" label="排放类型" width="120" />
        <el-table-column prop="period" label="周期" width="120" />
        <el-table-column prop="value" label="排放值" width="120" />
        <el-table-column prop="limit_value" label="限值" width="120" />
        <el-table-column prop="is_exceeding" label="是否超标" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_exceeding ? 'danger' : 'success'">{{ row.is_exceeding ? '超标' : '达标' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showDialog" title="录入排放数据" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="企业ID"><el-input-number v-model="form.enterprise_id" /></el-form-item>
        <el-form-item label="排放类型"><el-input v-model="form.type" /></el-form-item>
        <el-form-item label="周期"><el-date-picker v-model="form.period" type="date" /></el-form-item>
        <el-form-item label="排放值"><el-input-number v-model="form.value" /></el-form-item>
        <el-form-item label="限值"><el-input-number v-model="form.limit_value" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
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
import { getEmissionRecords, createEmissionRecord } from '@/api/emission'

const records = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showDialog = ref(false)
const creating = ref(false)
const form = reactive({ enterprise_id: null, type: '', period: '', value: 0, limit_value: 0, unit: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getEmissionRecords({ page: page.value })
    records.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createEmissionRecord(form)
    ElMessage.success('数据已录入')
    showDialog.value = false
    loadData()
  } finally { creating.value = false }
}

onMounted(() => loadData())
</script>

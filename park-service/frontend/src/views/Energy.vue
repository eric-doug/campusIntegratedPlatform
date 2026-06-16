<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>能源监控</span>
          <el-button type="primary" @click="showDialog = true">录入数据</el-button>
        </div>
      </template>
      <el-select v-model="enterpriseId" placeholder="选择企业" clearable style="width: 200px; margin-bottom: 16px" @change="loadData">
        <el-option :value="1" label="示例企业1" />
      </el-select>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="enterprise_id" label="企业ID" width="100" />
        <el-table-column prop="type" label="能源类型" width="120">
          <template #default="{ row }">{{ energyTypeMap[row.type] || row.type }}</template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="120" />
        <el-table-column prop="value" label="消耗值" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="reported" label="已报送" width="100">
          <template #default="{ row }"><el-tag :type="row.reported ? 'success' : 'warning'">{{ row.reported ? '是' : '否' }}</el-tag></template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showDialog" title="录入能源数据" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="企业ID"><el-input-number v-model="form.enterprise_id" /></el-form-item>
        <el-form-item label="能源类型">
          <el-select v-model="form.type">
            <el-option value="electric" label="电力" />
            <el-option value="gas" label="天然气" />
            <el-option value="water" label="用水" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期"><el-date-picker v-model="form.period" type="date" /></el-form-item>
        <el-form-item label="消耗值"><el-input-number v-model="form.value" /></el-form-item>
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
import { getEnergyRecords, createEnergyRecord } from '@/api/energy'

const records = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const enterpriseId = ref(null)
const showDialog = ref(false)
const creating = ref(false)
const energyTypeMap = { electric: '电力', gas: '天然气', water: '用水' }
const form = reactive({ enterprise_id: null, type: 'electric', period: '', value: 0, unit: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getEnergyRecords({ page: page.value, enterprise_id: enterpriseId.value })
    records.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createEnergyRecord(form)
    ElMessage.success('数据已录入')
    showDialog.value = false
    loadData()
  } finally { creating.value = false }
}

onMounted(() => loadData())
</script>

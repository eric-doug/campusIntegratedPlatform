<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>入库管理</span>
          <el-button type="primary" @click="showDialog = true">新建入库单</el-button>
        </div>
      </template>
      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="入库单号" width="200" />
        <el-table-column prop="warehouse_id" label="仓库ID" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }"><el-tag>{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="total_qty" label="总数量" width="100" />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showDialog" title="新建入库单" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="仓库ID"><el-input-number v-model="form.warehouse_id" /></el-form-item>
        <el-form-item label="供应商ID"><el-input-number v-model="form.supplier_id" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getInboundOrders, createInboundOrder } from '@/api/inbound'

const orders = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showDialog = ref(false)
const creating = ref(false)
const form = reactive({ warehouse_id: null, supplier_id: null, remark: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getInboundOrders({ page: page.value })
    orders.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createInboundOrder(form)
    ElMessage.success('入库单已创建')
    showDialog.value = false
    loadData()
  } finally { creating.value = false }
}

onMounted(() => loadData())
</script>

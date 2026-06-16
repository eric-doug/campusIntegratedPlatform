<template>
  <div>
    <el-card>
      <template #header><span>订单管理</span></template>
      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="payment_status" label="支付状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 'paid' ? 'success' : 'warning'">{{ row.payment_status === 'paid' ? '已支付' : '未支付' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/orders/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadOrders" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getOrders } from '@/api/orders'

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const statusMap = { pending: '待处理', confirmed: '已确认', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
const statusType = { pending: 'info', confirmed: '', shipped: 'warning', completed: 'success', cancelled: 'danger' }

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders({ page: page.value })
    orders.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => loadOrders())
</script>

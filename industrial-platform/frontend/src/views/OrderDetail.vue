<template>
  <div v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-card style="margin-top: 16px" v-if="order">
      <el-descriptions title="订单信息" :column="2">
        <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ order.status }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ order.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="支付状态">{{ order.payment_status }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ order.created_at }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <h4>订单明细</h4>
      <el-table :data="order.items" stripe style="margin-top: 12px">
        <el-table-column prop="product_sku_id" label="SKU ID" />
        <el-table-column prop="qty" label="数量" />
        <el-table-column prop="unit_price" label="单价">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getOrder } from '@/api/orders'

const router = useRouter()
const route = useRoute()
const order = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getOrder(route.params.id)
    order.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

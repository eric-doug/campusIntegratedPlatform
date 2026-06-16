<template>
  <div v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-card style="margin-top: 16px" v-if="shipment">
      <el-descriptions title="物流详情" :column="2">
        <el-descriptions-item label="运单号">{{ shipment.tracking_no }}</el-descriptions-item>
        <el-descriptions-item label="承运商">{{ shipment.carrier }}</el-descriptions-item>
        <el-descriptions-item label="始发地">{{ shipment.origin }}</el-descriptions-item>
        <el-descriptions-item label="目的地">{{ shipment.destination }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ shipment.status }}</el-descriptions-item>
        <el-descriptions-item label="预计到达">{{ shipment.eta }}</el-descriptions-item>
        <el-descriptions-item label="当前位置">{{ shipment.current_location?.address || '--' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getShipment } from '@/api/shipments'

const router = useRouter()
const route = useRoute()
const shipment = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getShipment(route.params.id)
    shipment.value = res.data
  } finally { loading.value = false }
})
</script>

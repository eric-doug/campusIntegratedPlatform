<template>
  <div>
    <el-card>
      <template #header><span>物流追踪</span></template>
      <el-table :data="shipments" v-loading="loading" stripe>
        <el-table-column prop="tracking_no" label="运单号" width="200" />
        <el-table-column prop="origin" label="始发地" width="150" />
        <el-table-column prop="destination" label="目的地" width="150" />
        <el-table-column prop="carrier" label="承运商" width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }"><el-tag>{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="eta" label="预计到达" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/shipments/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getShipments } from '@/api/shipments'

const router = useRouter()
const shipments = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getShipments({ page: page.value })
    shipments.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

onMounted(() => loadData())
</script>

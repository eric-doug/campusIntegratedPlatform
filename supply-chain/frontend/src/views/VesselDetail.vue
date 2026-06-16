<template>
  <div v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-card style="margin-top: 16px" v-if="vessel">
      <el-descriptions title="船舶详情" :column="2">
        <el-descriptions-item label="船名">{{ vessel.vessel_name }}</el-descriptions-item>
        <el-descriptions-item label="IMO">{{ vessel.imo }}</el-descriptions-item>
        <el-descriptions-item label="港口">{{ vessel.port }}</el-descriptions-item>
        <el-descriptions-item label="预计到港">{{ vessel.eta }}</el-descriptions-item>
        <el-descriptions-item label="实际到港">{{ vessel.ata || '--' }}</el-descriptions-item>
        <el-descriptions-item label="靠泊状态">{{ vessel.berth_status }}</el-descriptions-item>
        <el-descriptions-item label="装卸进度">
          <el-progress :percentage="vessel.cargo_progress || 0" />
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getVessel } from '@/api/vessels'

const router = useRouter()
const route = useRoute()
const vessel = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getVessel(route.params.id)
    vessel.value = res.data
  } finally { loading.value = false }
})
</script>

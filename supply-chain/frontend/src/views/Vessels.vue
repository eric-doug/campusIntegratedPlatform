<template>
  <div>
    <el-card>
      <template #header><span>船舶动态</span></template>
      <el-table :data="vessels" v-loading="loading" stripe>
        <el-table-column prop="vessel_name" label="船名" width="150" />
        <el-table-column prop="imo" label="IMO" width="120" />
        <el-table-column prop="port" label="港口" width="120" />
        <el-table-column prop="eta" label="预计到港" width="180" />
        <el-table-column prop="berth_status" label="靠泊状态" width="120">
          <template #default="{ row }">
            <el-tag :type="berthStatusType[row.berth_status] || 'info'">{{ row.berth_status || '--' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cargo_progress" label="装卸进度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.cargo_progress || 0" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/vessels/${row.id}`)">详情</el-button>
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
import { getVessels } from '@/api/vessels'

const router = useRouter()
const vessels = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const berthStatusType = { arrived: 'success', berthing: 'warning', loading: '', departed: 'info' }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getVessels({ page: page.value })
    vessels.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

onMounted(() => loadData())
</script>

<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>询价管理</span>
          <el-button type="primary" @click="router.push('/inquiries/create')">发起询价</el-button>
        </div>
      </template>
      <el-table :data="inquiries" v-loading="loading" stripe>
        <el-table-column prop="id" label="询价单号" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag>{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_items" label="询价项数" width="100" />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadInquiries" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getInquiries } from '@/api/inquiries'

const router = useRouter()
const inquiries = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const statusMap = { pending: '待报价', quoted: '已报价', closed: '已关闭' }

const loadInquiries = async () => {
  loading.value = true
  try {
    const res = await getInquiries({ page: page.value })
    inquiries.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => loadInquiries())
</script>

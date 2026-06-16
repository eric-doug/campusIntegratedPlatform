<template>
  <div>
    <el-card>
      <template #header><span>报送管理</span></template>
      <el-table :data="submissions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="form_id" label="表单ID" width="100" />
        <el-table-column prop="department" label="报送部门" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="subStatusType[row.status]">{{ subStatusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="报送时间" width="180" />
        <el-table-column prop="feedback" label="反馈" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.status === 'submitted'" text type="success" @click="handleReview(row.id, 'approved')">通过</el-button>
            <el-button v-if="row.status === 'submitted'" text type="danger" @click="handleReview(row.id, 'rejected')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSubmissions, reviewSubmission } from '@/api/submissions'

const submissions = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const subStatusMap = { submitted: '已报送', approved: '已通过', rejected: '已驳回' }
const subStatusType = { submitted: 'warning', approved: 'success', rejected: 'danger' }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSubmissions({ page: page.value })
    submissions.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleReview = async (id, action) => {
  try {
    await reviewSubmission(id, { action, feedback: '' })
    ElMessage.success(`已${action === 'approved' ? '通过' : '驳回'}`)
    loadData()
  } catch (e) {}
}

onMounted(() => loadData())
</script>

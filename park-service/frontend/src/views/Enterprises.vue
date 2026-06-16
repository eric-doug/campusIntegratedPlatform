<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>企业管理</span>
          <el-button type="primary" @click="showDialog = true">添加企业</el-button>
        </div>
      </template>
      <el-input v-model="keyword" placeholder="搜索企业名称/统一编码" style="width: 300px; margin-bottom: 16px" clearable @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-table :data="enterprises" v-loading="loading" stripe>
        <el-table-column prop="name" label="企业名称" min-width="200" />
        <el-table-column prop="unified_code" label="统一编码" width="150" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/enterprises/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="showDialog" title="添加企业" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="企业名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="统一编码"><el-input v-model="form.unified_code" /></el-form-item>
        <el-form-item label="行业"><el-input v-model="form.industry" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.contact_phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getEnterprises, createEnterprise } from '@/api/enterprises'

const router = useRouter()
const enterprises = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const keyword = ref('')
const showDialog = ref(false)
const creating = ref(false)
const form = reactive({ name: '', unified_code: '', industry: '', contact_person: '', contact_phone: '', address: '' })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getEnterprises({ page: page.value, keyword: keyword.value })
    enterprises.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await createEnterprise(form)
    ElMessage.success('企业已创建')
    showDialog.value = false
    loadData()
  } finally { creating.value = false }
}

onMounted(() => loadData())
</script>

<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>供应商管理</span>
          <el-button type="primary" @click="showApplyDialog = true">供应商入驻</el-button>
        </div>
      </template>
      <el-table :data="suppliers" v-loading="loading" stripe>
        <el-table-column prop="name" label="供应商名称" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="audit_status" label="审核状态" width="120">
          <template #default="{ row }">
            <el-tag :type="auditStatusType[row.audit_status]">{{ auditStatusMap[row.audit_status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadSuppliers" />
    </el-card>

    <el-dialog v-model="showApplyDialog" title="供应商入驻申请" width="500px">
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="供应商名称"><el-input v-model="applyForm.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="applyForm.code" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="applyForm.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="applyForm.contact_phone" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="applyForm.address" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApplyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleApply" :loading="applying">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSuppliers, createSupplier } from '@/api/suppliers'

const suppliers = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showApplyDialog = ref(false)
const applying = ref(false)
const applyForm = reactive({ name: '', code: '', contact_person: '', contact_phone: '', address: '' })
const auditStatusMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
const auditStatusType = { pending: 'warning', approved: 'success', rejected: 'danger' }

const loadSuppliers = async () => {
  loading.value = true
  try {
    const res = await getSuppliers({ page: page.value })
    suppliers.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const handleApply = async () => {
  applying.value = true
  try {
    await createSupplier(applyForm)
    ElMessage.success('申请已提交')
    showApplyDialog.value = false
    loadSuppliers()
  } finally {
    applying.value = false
  }
}

onMounted(() => loadSuppliers())
</script>

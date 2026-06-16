<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>商品管理</span>
          <el-button type="primary" @click="showCreateDialog = true">添加商品</el-button>
        </div>
      </template>
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.status" active-value="active" inactive-value="inactive" @change="handleStatusChange(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="editProduct(row)">编辑</el-button>
            <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadProducts" />
    </el-card>

    <el-dialog v-model="showCreateDialog" :title="editingProduct ? '编辑商品' : '添加商品'" width="600px">
      <el-form :model="productForm" label-width="100px">
        <el-form-item label="商品名称"><el-input v-model="productForm.name" /></el-form-item>
        <el-form-item label="分类"><el-input-number v-model="productForm.category_id" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="productForm.unit" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="productForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProducts, createProduct, updateProduct, deleteProduct } from '@/api/products'

const products = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const showCreateDialog = ref(false)
const saving = ref(false)
const editingProduct = ref(null)
const productForm = reactive({ name: '', category_id: null, unit: '', description: '' })

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await getProducts({ page: page.value, per_page: 20 })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const editProduct = (row) => {
  editingProduct.value = row
  Object.assign(productForm, { name: row.name, category_id: row.category_id, unit: row.unit, description: row.description })
  showCreateDialog.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    if (editingProduct.value) {
      await updateProduct(editingProduct.value.id, productForm)
    } else {
      await createProduct(productForm)
    }
    ElMessage.success('保存成功')
    showCreateDialog.value = false
    editingProduct.value = null
    loadProducts()
  } finally {
    saving.value = false
  }
}

const handleStatusChange = async (row) => {
  await updateProduct(row.id, { status: row.status })
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('已删除')
  loadProducts()
}

onMounted(() => loadProducts())
</script>

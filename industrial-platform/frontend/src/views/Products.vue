<template>
  <div class="products-page">
    <el-card>
      <div class="filter-bar">
        <el-input v-model="keyword" placeholder="搜索商品" style="width: 300px" clearable @keyup.enter="loadProducts">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="categoryId" placeholder="商品分类" clearable style="width: 200px; margin-left: 12px" @change="loadProducts">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" style="margin-left: 12px" @click="loadProducts">搜索</el-button>
      </div>
      <el-table :data="products" v-loading="loading" stripe style="margin-top: 16px">
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '在售' : '下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上架时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="router.push(`/products/${row.id}`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="perPage"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="loadProducts"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '@/api/products'
import { getCategories } from '@/api/categories'

const router = useRouter()
const products = ref([])
const categories = ref([])
const loading = ref(false)
const keyword = ref('')
const categoryId = ref(null)
const page = ref(1)
const perPage = ref(20)
const total = ref(0)

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await getProducts({ page: page.value, per_page: perPage.value, keyword: keyword.value, category_id: categoryId.value })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loadProducts()
  try {
    const res = await getCategories()
    categories.value = res.data || []
  } catch (e) {}
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
}
</style>

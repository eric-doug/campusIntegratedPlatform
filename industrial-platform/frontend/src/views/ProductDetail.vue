<template>
  <div class="product-detail" v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-row :gutter="24" style="margin-top: 24px" v-if="product">
      <el-col :span="12">
        <el-card>
          <div class="product-images">
            <el-icon :size="120" color="#909399"><Box /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <h2>{{ product.name }}</h2>
          <el-descriptions :column="1" style="margin-top: 16px">
            <el-descriptions-item label="单位">{{ product.unit }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="product.status === 'active' ? 'success' : 'info'">{{ product.status === 'active' ? '在售' : '下架' }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <el-divider />
          <h4>规格列表</h4>
          <el-table :data="product.skus" stripe style="margin-top: 12px">
            <el-table-column prop="sku_code" label="SKU编码" />
            <el-table-column prop="price" label="价格">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column prop="stock" label="库存" />
            <el-table-column label="操作" width="120">
              <template #default>
                <el-button text type="primary">加入询价</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" size="large" style="margin-top: 16px" @click="router.push('/inquiries/create')">立即询价</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getProduct } from '@/api/products'

const router = useRouter()
const route = useRoute()
const product = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getProduct(route.params.id)
    product.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.product-images {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>

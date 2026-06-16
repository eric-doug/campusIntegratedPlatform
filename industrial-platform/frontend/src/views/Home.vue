<template>
  <div class="home-page">
    <el-row :gutter="24">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>热门商品</span>
              <el-button text @click="router.push('/products')">查看更多</el-button>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="product in hotProducts" :key="product.id">
              <el-card shadow="hover" class="product-card" @click="router.push(`/products/${product.id}`)">
                <div class="product-image">
                  <el-icon :size="48" color="#909399"><Box /></el-icon>
                </div>
                <div class="product-info">
                  <h4>{{ product.name }}</h4>
                  <p class="price">¥{{ product.specs?.price || '--' }}</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>AI 智能助手</span></template>
          <div class="ai-section">
            <el-input v-model="aiQuery" placeholder="描述您需要的工业品..." :rows="3" type="textarea" />
            <el-button type="primary" style="margin-top: 12px; width: 100%" @click="handleAiSearch" :loading="aiLoading">
              AI 智能搜索
            </el-button>
            <div v-if="aiResult" class="ai-result">
              <p>{{ aiResult }}</p>
            </div>
          </div>
        </el-card>
        <el-card style="margin-top: 16px">
          <template #header><span>快捷入口</span></template>
          <el-space direction="vertical" fill style="width: 100%">
            <el-button style="width: 100%" @click="router.push('/inquiries/create')">发起询价</el-button>
            <el-button style="width: 100%" @click="router.push('/orders')">我的订单</el-button>
            <el-button style="width: 100%" @click="router.push('/suppliers')">供应商入驻</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts } from '@/api/products'
import { smartSearch } from '@/api/ai'

const router = useRouter()
const hotProducts = ref([])
const aiQuery = ref('')
const aiResult = ref('')
const aiLoading = ref(false)

onMounted(async () => {
  try {
    const res = await getProducts({ per_page: 6 })
    hotProducts.value = res.data?.items || []
  } catch (e) {}
})

const handleAiSearch = async () => {
  if (!aiQuery.value.trim()) return
  aiLoading.value = true
  aiResult.value = ''
  try {
    const res = await smartSearch(aiQuery.value)
    aiResult.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    aiResult.value = '搜索失败，请稍后重试'
  } finally {
    aiLoading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.product-card {
  cursor: pointer;
  margin-bottom: 16px;
}
.product-image {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 120px;
  background: #f5f7fa;
  border-radius: 4px;
}
.product-info h4 {
  margin: 8px 0 4px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.price {
  color: #f56c6c;
  font-size: 16px;
  font-weight: bold;
}
.ai-result {
  margin-top: 12px;
  padding: 12px;
  background: #f0f2f5;
  border-radius: 4px;
  font-size: 13px;
  white-space: pre-wrap;
}
</style>

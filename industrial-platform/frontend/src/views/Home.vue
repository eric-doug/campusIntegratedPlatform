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
                  <p class="price">
                    <template v-if="product.min_price != null">
                      ¥{{ product.min_price }}<template v-if="product.max_price != null && product.max_price > product.min_price"> - ¥{{ product.max_price }}</template>
                    </template>
                    <template v-else>¥--</template>
                  </p>
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
            <div v-if="searchProducts.length" class="search-results">
              <div class="search-results-header">
                <span>搜索结果（{{ searchProducts.length }} 件）</span>
                <el-button text size="small" @click="searchProducts = []">清除</el-button>
              </div>
              <div class="search-list">
                <div v-for="item in searchProducts" :key="item.id" class="search-item" @click="router.push(`/products/${item.id}`)">
                  <div class="search-item-icon">
                    <el-icon :size="32" color="#909399"><Box /></el-icon>
                  </div>
                  <div class="search-item-info">
                    <div class="search-item-name">{{ item.name }}</div>
                    <div class="search-item-desc">{{ item.description || '暂无描述' }}</div>
                  </div>
                  <div class="search-item-price">
                    <template v-if="item.min_price != null">
                      ¥{{ item.min_price }}<template v-if="item.max_price != null && item.max_price > item.min_price"> - ¥{{ item.max_price }}</template>
                    </template>
                    <template v-else>¥--</template>
                  </div>
                  <div class="search-item-meta">
                    <el-tag size="small" type="info">{{ item.sku_count || 0 }} SKU</el-tag>
                  </div>
                </div>
              </div>
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
const searchProducts = ref([])

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
  searchProducts.value = []
  try {
    const res = await smartSearch(aiQuery.value)
    const cond = res.data || {}
    const keywords = cond.keywords || []
    const priceRange = cond.price_range || {}
    const params = { per_page: 20 }
    if (keywords.length) params.keyword = keywords.join(' ')
    if (priceRange.min != null) params.min_price = priceRange.min
    if (priceRange.max != null) params.max_price = priceRange.max
    if (cond.category) params.category = cond.category
    const prodRes = await getProducts(params)
    searchProducts.value = prodRes.data?.items || []
    aiResult.value = `已解析条件：${keywords.length ? '关键词[' + keywords.join(', ') + ']' : '无'}${cond.category ? ' / 分类[' + cond.category + ']' : ''}${priceRange.min != null || priceRange.max != null ? ' / 价格[' + (priceRange.min ?? '*') + '-' + (priceRange.max ?? '*') + ']' : ''}`
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
.search-results {
  margin-top: 12px;
}
.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}
.search-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 360px;
  overflow-y: auto;
}
.search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.search-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
}
.search-item-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
}
.search-item-info {
  flex: 1;
  min-width: 0;
}
.search-item-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.search-item-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.search-item-price {
  flex-shrink: 0;
  color: #f56c6c;
  font-weight: bold;
  font-size: 14px;
}
.search-item-meta {
  flex-shrink: 0;
}
</style>

<template>
  <div>
    <el-card>
      <template #header><span>库存管理</span></template>
      <el-select v-model="warehouseId" placeholder="选择仓库" clearable style="width: 200px; margin-bottom: 16px" @change="loadData">
        <el-option :value="1" label="仓库1" />
        <el-option :value="2" label="仓库2" />
      </el-select>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="warehouse_id" label="仓库ID" width="100" />
        <el-table-column prop="product_sku_id" label="SKU ID" width="120" />
        <el-table-column prop="qty" label="库存量" width="100" />
        <el-table-column prop="locked_qty" label="锁定量" width="100" />
        <el-table-column prop="available_qty" label="可用量" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.available_qty < 10 ? '#f56c6c' : '' }">{{ row.available_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="batch_no" label="批次号" width="150" />
        <el-table-column prop="updated_at" label="更新时间" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventory } from '@/api/inventory'

const items = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const warehouseId = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getInventory({ page: page.value, warehouse_id: warehouseId.value })
    items.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally { loading.value = false }
}

onMounted(() => loadData())
</script>

<template>
  <div>
    <el-card>
      <template #header><span>发起询价</span></template>
      <el-form :model="form" label-width="100px">
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入询价备注" />
        </el-form-item>
        <el-form-item label="询价商品">
          <el-button type="primary" @click="addItem">添加商品</el-button>
        </el-form-item>
        <el-table :data="form.items" stripe style="margin-bottom: 16px">
          <el-table-column label="SKU ID" width="150">
            <template #default="{ row }">
              <el-input v-model="row.product_sku_id" placeholder="SKU ID" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.qty" :min="1" />
            </template>
          </el-table-column>
          <el-table-column label="目标价格" width="150">
            <template #default="{ row }">
              <el-input v-model="row.target_price" placeholder="选填" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button text type="danger" @click="form.items.splice($index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交询价</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createInquiry } from '@/api/inquiries'

const router = useRouter()
const submitting = ref(false)
const form = reactive({ remark: '', items: [] })

const addItem = () => {
  form.items.push({ product_sku_id: '', qty: 1, target_price: '' })
}

const handleSubmit = async () => {
  if (form.items.length === 0) {
    ElMessage.warning('请至少添加一个询价商品')
    return
  }
  submitting.value = true
  try {
    await createInquiry({ remark: form.remark, items: form.items })
    ElMessage.success('询价已提交')
    router.push('/inquiries')
  } finally {
    submitting.value = false
  }
}
</script>

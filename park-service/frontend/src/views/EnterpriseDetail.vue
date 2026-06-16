<template>
  <div v-loading="loading">
    <el-page-header @back="router.back()" title="返回" />
    <el-card style="margin-top: 16px" v-if="enterprise">
      <el-descriptions title="企业信息" :column="2">
        <el-descriptions-item label="企业名称">{{ enterprise.name }}</el-descriptions-item>
        <el-descriptions-item label="统一编码">{{ enterprise.unified_code }}</el-descriptions-item>
        <el-descriptions-item label="行业">{{ enterprise.industry }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ enterprise.contact_person }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ enterprise.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="地址">{{ enterprise.address }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getEnterprise } from '@/api/enterprises'

const router = useRouter()
const route = useRoute()
const enterprise = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getEnterprise(route.params.id)
    enterprise.value = res.data
  } finally { loading.value = false }
})
</script>

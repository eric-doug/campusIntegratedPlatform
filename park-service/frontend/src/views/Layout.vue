<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <h1 class="logo">园区服务平台</h1>
        <el-menu mode="horizontal" :default-active="currentRoute" router class="nav-menu">
          <el-menu-item index="/home">首页</el-menu-item>
          <el-menu-item index="/enterprises">企业管理</el-menu-item>
          <el-menu-item index="/energy">能源监控</el-menu-item>
          <el-menu-item index="/safety">安全生产</el-menu-item>
          <el-menu-item index="/emission">环保排放</el-menu-item>
          <el-menu-item index="/reports">报表中心</el-menu-item>
          <el-menu-item index="/submissions">报送管理</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-button text @click="logout">退出</el-button>
      </div>
    </el-header>
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()
const currentRoute = computed(() => route.path)
const logout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}
</script>

<style scoped>
.layout-container { min-height: 100vh; }
.layout-header { display: flex; justify-content: space-between; align-items: center; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 0 24px; height: 60px; }
.header-left { display: flex; align-items: center; }
.logo { font-size: 18px; color: #e65100; margin-right: 32px; white-space: nowrap; }
.nav-menu { border-bottom: none; }
.layout-main { background: #f5f7fa; padding: 24px; }
</style>

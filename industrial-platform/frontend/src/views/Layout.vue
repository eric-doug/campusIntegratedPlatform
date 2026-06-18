<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <h1 class="logo">工业品交易平台</h1>
        <el-menu mode="horizontal" :default-active="currentRoute" router :ellipsis="false" class="nav-menu">
          <el-menu-item index="/home">首页</el-menu-item>
          <el-menu-item index="/products">商品中心</el-menu-item>
          <el-menu-item index="/inquiries">询价管理</el-menu-item>
          <el-menu-item index="/orders">订单管理</el-menu-item>
          <el-menu-item index="/suppliers">供应商</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore.userInfo?.username || '用户' }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/admin/products')">后台管理</el-dropdown-item>
              <el-dropdown-item @click="router.push('/supplier/products')">供应商商品录入</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentRoute = computed(() => '/' + route.path.split('/')[1])

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
  height: 60px;
}
.header-left {
  display: flex;
  align-items: center;
}
.logo {
  font-size: 18px;
  color: #1a237e;
  margin-right: 32px;
  white-space: nowrap;
}
.nav-menu {
  border-bottom: none;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #606266;
}
.layout-main {
  background: #f5f7fa;
  padding: 24px;
}
</style>

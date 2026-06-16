import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/home',
    children: [
      { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'products', name: 'Products', component: () => import('@/views/Products.vue') },
      { path: 'products/:id', name: 'ProductDetail', component: () => import('@/views/ProductDetail.vue') },
      { path: 'inquiries', name: 'Inquiries', component: () => import('@/views/Inquiries.vue') },
      { path: 'inquiries/create', name: 'CreateInquiry', component: () => import('@/views/CreateInquiry.vue') },
      { path: 'orders', name: 'Orders', component: () => import('@/views/Orders.vue') },
      { path: 'orders/:id', name: 'OrderDetail', component: () => import('@/views/OrderDetail.vue') },
      { path: 'suppliers', name: 'Suppliers', component: () => import('@/views/Suppliers.vue') },
      { path: 'admin/products', name: 'AdminProducts', component: () => import('@/views/AdminProducts.vue') },
      { path: 'admin/dashboard', name: 'AdminDashboard', component: () => import('@/views/AdminDashboard.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router

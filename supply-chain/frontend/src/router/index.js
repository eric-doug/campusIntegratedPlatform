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
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'inbound', name: 'Inbound', component: () => import('@/views/Inbound.vue') },
      { path: 'outbound', name: 'Outbound', component: () => import('@/views/Outbound.vue') },
      { path: 'inventory', name: 'Inventory', component: () => import('@/views/Inventory.vue') },
      { path: 'vessels', name: 'Vessels', component: () => import('@/views/Vessels.vue') },
      { path: 'vessels/:id', name: 'VesselDetail', component: () => import('@/views/VesselDetail.vue') },
      { path: 'shipments', name: 'Shipments', component: () => import('@/views/Shipments.vue') },
      { path: 'shipments/:id', name: 'ShipmentDetail', component: () => import('@/views/ShipmentDetail.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/supply/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) next('/login')
  else next()
})

export default router

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
      { path: 'enterprises', name: 'Enterprises', component: () => import('@/views/Enterprises.vue') },
      { path: 'enterprises/:id', name: 'EnterpriseDetail', component: () => import('@/views/EnterpriseDetail.vue') },
      { path: 'energy', name: 'Energy', component: () => import('@/views/Energy.vue') },
      { path: 'safety', name: 'Safety', component: () => import('@/views/Safety.vue') },
      { path: 'emission', name: 'Emission', component: () => import('@/views/Emission.vue') },
      { path: 'reports', name: 'Reports', component: () => import('@/views/Reports.vue') },
      { path: 'reports/:id', name: 'ReportFill', component: () => import('@/views/ReportFill.vue') },
      { path: 'submissions', name: 'Submissions', component: () => import('@/views/Submissions.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/park/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) next('/login')
  else next()
})

export default router

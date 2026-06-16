import { defineStore } from 'pinia'
import { login as loginApi, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    userInfo: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    async login(credentials) {
      const res = await loginApi(credentials)
      this.token = res.data.access_token
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      await this.fetchUserInfo()
    },
    async fetchUserInfo() {
      const res = await getCurrentUser()
      this.userInfo = res.data
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})

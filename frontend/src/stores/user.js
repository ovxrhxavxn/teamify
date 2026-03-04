import { defineStore } from 'pinia'
import api from '@/api'
import router from '@/router'

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null,
    isLoading: false,
    isSaving: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.profile,
  },

  actions: {
    async fetchUser() {
      const token = localStorage.getItem('user_token')
      if (!token || this.profile) return

      this.isLoading = true
      try {
        const response = await api.get('/profiles/me')
        this.profile = response.data
      } catch (error) {
        console.error('Auth error, invalid token:', error)
        this.logout()
      } finally {
        this.isLoading = false
      }
    },

    async updateProfileDescription(newDescription) {
      this.isSaving = true
      try {
        await api.put('/profiles/me', { description: newDescription })
        if (this.profile) {
          this.profile.profile.description = newDescription
        }
      } catch (error) {
        console.error('Error updating profile:', error)
      } finally {
        this.isSaving = false
      }
    },

    async updateProfileRoles(roleIds) {
      this.isSaving = true
      try {
        const response = await api.put('/profiles/me', { role_ids: roleIds })
        const updatedProfile = response.data
        if (this.profile) {
          this.profile.profile.roles = updatedProfile.roles
        }
        return updatedProfile.roles
      } catch (error) {
        console.error('Error updating roles:', error)
        return null
      } finally {
        this.isSaving = false
      }
    },

    async logout() {
      // Удаляем refresh cookie через бэкенд
      try {
        await api.post('/auth/logout')
      } catch {
        // Игнорируем ошибки при логауте
      }
      this.profile = null
      localStorage.removeItem('user_token')
      if (router.currentRoute.value.name !== 'home') {
        router.push({ name: 'home' })
      }
    },
  },
})

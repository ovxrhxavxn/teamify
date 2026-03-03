import { defineStore } from 'pinia'
import axios from 'axios'
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
    async updateProfileRoles(roleIds) {
      this.isSaving = true
      try {
        const token = localStorage.getItem('user_token')
        const response = await axios.put(
          'https://teamify.pro/api/profiles/me',
          { role_ids: roleIds },
          { headers: { Authorization: `Bearer ${token}` } },
        )
        const updatedProfile = response.data
        // Обновляем состояние в сторе
        if (this.profile) {
          this.profile.profile.roles = updatedProfile.roles
        }
        // --- ВОЗВРАЩАЕМ ОБНОВЛЕННЫЕ ДАННЫЕ ---
        return updatedProfile.roles
      } catch (error) {
        console.error('Ошибка при обновлении ролей:', error)
        // В случае ошибки возвращаем null или выбрасываем ошибку
        return null
      } finally {
        this.isSaving = false
      }
    },

    async fetchUser() {
      const token = localStorage.getItem('user_token')
      if (!token) {
        return
      }
      if (this.profile) {
        return
      }
      this.isLoading = true
      try {
        const response = await axios.get('https://teamify.pro/api/profiles/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        this.profile = response.data
      } catch (error) {
        console.error('Ошибка аутентификации, токен невалиден:', error)
        this.logout()
      } finally {
        this.isLoading = false
      }
    },

    async updateProfileDescription(newDescription) {
      this.isSaving = true
      try {
        const token = localStorage.getItem('user_token')
        await axios.put(
          'https://teamify.pro/api/profiles/me',
          { description: newDescription },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        )
        // При успехе обновляем состояние локально, без перезагрузки
        if (this.profile) {
          this.profile.profile.description = newDescription
        }
      } catch (error) {
        console.error('Ошибка при обновлении профиля:', error)
        // Здесь можно показать уведомление об ошибке
      } finally {
        this.isSaving = false
      }
    },

    logout() {
      this.profile = null // Очищаем данные
      localStorage.removeItem('user_token')
      if (router.currentRoute.value.name !== 'home') {
        router.push({ name: 'home' })
      }
    },
  },
})

import { defineStore } from 'pinia'
import axios from 'axios'
const PAGE_SIZE = 3
export const useLfgStore = defineStore('lfg', {
  state: () => ({
    activePlayers: [],
    isSearching: false,
    socket: null,
    isLoading: true,
    isLoadingMore: false,
    hasMorePlayers: true,
    currentPage: 0,
  }),
  actions: {
    async fetchMyStatus() {
      try {
        const token = localStorage.getItem('user_token')
        const response = await axios.get('https://teamify.pro/api/lfg/status', {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.isSearching = response.data.is_active
      } catch (error) {
        console.error('Ошибка при получении своего LFG статуса:', error)
      }
    },
    async fetchInitialPlayers() {
      this.isLoading = true
      this.activePlayers = []
      this.currentPage = 0
      this.hasMorePlayers = true
      try {
        const token = localStorage.getItem('user_token')
        const response = await axios.get('https://teamify.pro/api/lfg/active', {
          headers: { Authorization: `Bearer ${token}` },
          params: {
            limit: PAGE_SIZE,
            offset: 0,
          },
        })
        this.activePlayers = response.data
        this.currentPage = 1
        if (response.data.length < PAGE_SIZE) {
          this.hasMorePlayers = false
        }
      } catch (error) {
        console.error('Ошибка при загрузке LFG игроков:', error)
      } finally {
        this.isLoading = false
      }
    },
    async fetchMorePlayers() {
      if (this.isLoadingMore || !this.hasMorePlayers) return
      this.isLoadingMore = true
      try {
        const token = localStorage.getItem('user_token')
        const response = await axios.get('https://teamify.pro/api/lfg/active', {
          headers: { Authorization: `Bearer ${token}` },
          params: {
            limit: PAGE_SIZE,
            offset: this.currentPage * PAGE_SIZE,
          },
        })
        if (response.data.length > 0) {
          this.activePlayers.push(...response.data)
          this.currentPage++
        }
        if (response.data.length < PAGE_SIZE) {
          this.hasMorePlayers = false
        }
      } catch (error) {
        console.error('Ошибка при подгрузке игроков:', error)
      } finally {
        this.isLoadingMore = false
      }
    },
    connectWebSocket() {
      const token = localStorage.getItem('user_token')
      if (!token || this.socket) return
      // Используем wss для безопасного соединения
      const socketUrl = `wss://teamify.pro/api/lfg/ws?token=${token}`
      this.socket = new WebSocket(socketUrl)
      this.socket.onopen = () => {
        console.log('WebSocket-соединение установлено.')
      }
      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data)
        if (message.type === 'status_update') {
          const userProfile = message.user_profile
          const userId = userProfile.profile.user_id
          if (message.is_active) {
            const playerExists = this.activePlayers.some((p) => p.profile.user_id === userId)
            if (!playerExists) {
              this.activePlayers.unshift(userProfile)
            }
          } else {
            this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)
          }
        }
      }
      this.socket.onclose = () => {
        console.log('WebSocket-соединение закрыто.')
        this.socket = null
      }
    },
    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close()
      }
    },
    async toggleSearchStatus(newStatus) {
      this.isSearching = newStatus
      try {
        const token = localStorage.getItem('user_token')
        await axios.post(
          'https://teamify.pro/api/lfg/status',
          { is_active: newStatus },
          { headers: { Authorization: `Bearer ${token}` } },
        )
      } catch (error) {
        console.error('Ошибка при обновлении LFG статуса:', error)
        // Возвращаем переключатель в исходное состояние
        this.isSearching = !newStatus
      }
    },
  },
})

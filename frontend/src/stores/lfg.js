// frontend/src/stores/lfg.js
import { defineStore } from 'pinia'
import api from '@/api'

const PAGE_SIZE = 3

function serializeParams(params) {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined) continue
    if (Array.isArray(value)) {
      value.forEach((item) => searchParams.append(key, item))
    } else {
      searchParams.append(key, value)
    }
  }
  return searchParams
}

export const useLfgStore = defineStore('lfg', {
  state: () => ({
    activePlayers: [],
    isSearching: false,
    socket: null,
    isLoading: true,
    isLoadingMore: false,
    hasMorePlayers: true,
    currentPage: 0,
    currentFilters: {},

    // --- Уведомления ---
    notifications: [],
    currentNotification: null,
    showNotification: false,
    _notificationTimer: null,
    _notificationQueue: [],
  }),

  actions: {
    async fetchMyStatus() {
      try {
        const response = await api.get('/lfg/status')
        this.isSearching = response.data.is_active
      } catch (error) {
        console.error('Error fetching LFG status:', error)
      }
    },

    async fetchInitialPlayers(filters = {}) {
      this.isLoading = true
      // НЕ обнуляем activePlayers сразу — ждём ответа
      this.currentPage = 0
      this.hasMorePlayers = true
      this.currentFilters = filters

      try {
        const response = await api.get('/lfg/active', {
          params: { limit: PAGE_SIZE, offset: 0, ...this.currentFilters },
          paramsSerializer: (params) => serializeParams(params).toString(),
        })
        this.activePlayers = response.data // Перезаписываем только когда есть данные
        this.currentPage = 1
        if (response.data.length < PAGE_SIZE) {
          this.hasMorePlayers = false
        }
      } catch (error) {
        console.error('Error loading LFG players:', error)
      } finally {
        this.isLoading = false
      }
    },

    async fetchMorePlayers() {
      if (this.isLoadingMore || !this.hasMorePlayers) return
      this.isLoadingMore = true
      try {
        const response = await api.get('/lfg/active', {
          params: {
            limit: PAGE_SIZE,
            offset: this.currentPage * PAGE_SIZE,
            ...this.currentFilters,
          },
          paramsSerializer: (params) => serializeParams(params).toString(),
        })
        if (response.data.length > 0) {
          // Фильтруем дубликаты
          const existingIds = new Set(this.activePlayers.map((p) => p.profile.user_id))
          const newPlayers = response.data.filter((p) => !existingIds.has(p.profile.user_id))
          this.activePlayers.push(...newPlayers)
          this.currentPage++
        }
        if (response.data.length < PAGE_SIZE) {
          this.hasMorePlayers = false
        }
      } catch (error) {
        console.error('Error loading more players:', error)
      } finally {
        this.isLoadingMore = false
      }
    },

    async toggleSearchStatus(newStatus) {
      this.isSearching = newStatus
      try {
        await api.post('/lfg/status', { is_active: newStatus })
      } catch (error) {
        console.error('Error toggling LFG status:', error)
        this.isSearching = !newStatus
      }
    },

    connectWebSocket() {
      const token = localStorage.getItem('user_token')
      if (!token || this.socket) return

      const wsBase = import.meta.env.VITE_WS_BASE_URL || 'wss://teamify.pro/api'
      this.socket = new WebSocket(`${wsBase}/lfg/ws?token=${token}`)

      this.socket.onopen = () => {
        console.log('WebSocket connected.')
      }

      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data)
        this._handleSocketMessage(message)
      }

      this.socket.onclose = () => {
        console.log('WebSocket closed.')
        this.socket = null
      }
    },

    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close()
      }
      this._clearNotificationTimer()
    },

    _handleSocketMessage(message) {
      switch (message.type) {
        case 'status_update':
          this._handleStatusUpdate(message)
          break

        case 'lfg_response':
          this._handleLfgResponse(message)
          break

        default:
          console.warn('Unknown WS message type:', message.type)
      }
    },

    _handleStatusUpdate(message) {
      const userProfile = message.user_profile
      const userId = userProfile.profile.user_id

      if (message.is_active) {
        // Удаляем старую версию (если есть) и добавляем новую
        this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)
        this.activePlayers.unshift(userProfile)
      } else {
        this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)
      }
    },

    _handleLfgResponse(message) {
      // Сохраняем в историю
      this.notifications.unshift({
        ...message,
        read: false,
        receivedAt: Date.now(),
      })

      if (this.showNotification) {
        this._notificationQueue.push(message)
        return
      }

      this._showNotification(message)
    },

    _showNotification(notification) {
      this.currentNotification = notification
      this.showNotification = true

      // Автоскрытие через 12 секунд
      this._clearNotificationTimer()
      this._notificationTimer = setTimeout(() => {
        this.dismissNotification()
      }, 12000)
    },

    dismissNotification() {
      this.showNotification = false
      this._clearNotificationTimer()

      // Через 400мс (время анимации) показываем следующее из очереди
      setTimeout(() => {
        this.currentNotification = null

        if (this._notificationQueue.length > 0) {
          const next = this._notificationQueue.shift()
          this._showNotification(next)
        }
      }, 400)
    },

    markAllNotificationsRead() {
      this.notifications.forEach((n) => (n.read = true))
    },

    _clearNotificationTimer() {
      if (this._notificationTimer) {
        clearTimeout(this._notificationTimer)
        this._notificationTimer = null
      }
    },
  },

  getters: {
    unreadCount: (state) => state.notifications.filter((n) => !n.read).length,
  },
})

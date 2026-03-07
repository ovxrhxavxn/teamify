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
      if (!token) return

      // Закрываем старый сокет, если есть
      if (this.socket) {
        this.socket.close()
        this.socket = null
      }

      const wsBase = import.meta.env.VITE_WS_BASE_URL || 'wss://teamify.pro/api'
      const url = `${wsBase}/lfg/ws?token=${token}`

      console.log('WebSocket connecting to:', url)
      this.socket = new WebSocket(url)

      this.socket.onopen = () => {
        console.log('WebSocket connected.')
        this._reconnectAttempts = 0
      }

      this.socket.onmessage = (event) => {
        if (event.data === 'ping') {
          this.socket.send('pong')
          return
        }

        try {
          const message = JSON.parse(event.data)
          this._handleSocketMessage(message)
        } catch (e) {
          console.error('Failed to parse WS message:', e)
        }
      }

      // Клиентский keepalive
      this._pingInterval = setInterval(() => {
        if (this.socket?.readyState === WebSocket.OPEN) {
          this.socket.send('ping')
        }
      }, 30000)

      this.socket.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.socket = null

        // Реконнект только если не было явного отключения
        if (!this._intentionalDisconnect) {
          this._scheduleReconnect()
        }
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      this._intentionalDisconnect = false
    },

    disconnectWebSocket() {
      this._intentionalDisconnect = true
      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer)
      }
      if (this._pingInterval) {
        clearInterval(this._pingInterval)
        this._pingInterval = null
      }
      if (this.socket) {
        this.socket.close()
        this.socket = null
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

    _scheduleReconnect() {
      if (!this._reconnectAttempts) this._reconnectAttempts = 0
      if (this._reconnectAttempts >= 5) {
        console.warn('Max reconnect attempts reached')
        return
      }

      const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts), 30000)
      this._reconnectAttempts++

      console.log(`Reconnecting in ${delay}ms (attempt ${this._reconnectAttempts})`)

      this._reconnectTimer = setTimeout(() => {
        const token = localStorage.getItem('user_token')
        if (token) {
          this.connectWebSocket()
        }
      }, delay)
    },
  },

  getters: {
    unreadCount: (state) => state.notifications.filter((n) => !n.read).length,
  },
})

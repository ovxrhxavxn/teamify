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

    // --- Reconnect ---
    _reconnectAttempts: 0,
    _reconnectTimer: null,
    _pingInterval: null,
    _intentionalDisconnect: false,
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
      this.currentPage = 0
      this.hasMorePlayers = true
      this.currentFilters = filters

      try {
        const response = await api.get('/lfg/active', {
          params: { limit: PAGE_SIZE, offset: 0, ...this.currentFilters },
          paramsSerializer: (params) => serializeParams(params).toString(),
        })
        this.activePlayers = response.data
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
      const previousStatus = this.isSearching
      this.isSearching = newStatus

      try {
        await api.post('/lfg/status', { is_active: newStatus })
      } catch (error) {
        console.error('Error toggling LFG status:', error)
        this.isSearching = previousStatus
      }
    },

    connectWebSocket() {
      const token = localStorage.getItem('user_token')
      if (!token) return

      if (this.socket) {
        this._intentionalDisconnect = true
        this.socket.close()
        this.socket = null
      }
      this._intentionalDisconnect = false

      const wsBase = import.meta.env.VITE_WS_BASE_URL || 'wss://teamify.pro/api'
      const url = `${wsBase}/lfg/ws?token=${token}`
      console.log('[WS] Connecting to:', url)

      this.socket = new WebSocket(url)

      this.socket.onopen = () => {
        console.log('[WS] Connected.')
        this._reconnectAttempts = 0

        this._syncAfterReconnect()
      }

      this.socket.onmessage = (event) => {
        // Keepalive
        if (event.data === 'ping') {
          this.socket.send('pong')
          return
        }
        if (event.data === 'pong') {
          return
        }

        try {
          const message = JSON.parse(event.data)
          this._handleSocketMessage(message)
        } catch (e) {
          console.error('[WS] Failed to parse message:', e)
        }
      }

      this._clearPingInterval()
      this._pingInterval = setInterval(() => {
        if (this.socket?.readyState === WebSocket.OPEN) {
          this.socket.send('ping')
        }
      }, 30000)

      this.socket.onclose = (event) => {
        console.log('[WS] Closed:', event.code, event.reason)
        this.socket = null
        this._clearPingInterval()

        if (event.code === 4001) return

        if (!this._intentionalDisconnect) {
          this._scheduleReconnect()
        }
      }

      this.socket.onerror = (error) => {
        console.error('[WS] Error:', error)
      }
    },

    disconnectWebSocket() {
      this._intentionalDisconnect = true

      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer)
        this._reconnectTimer = null
      }
      this._clearPingInterval()
      this._clearNotificationTimer()

      if (this.socket) {
        this.socket.close()
        this.socket = null
      }
    },

    _handleSocketMessage(message) {
      console.log('[WS] Received:', message.type)

      switch (message.type) {
        case 'player_joined':
          this._handlePlayerJoined(message)
          break
        case 'player_left':
          this._handlePlayerLeft(message)
          break
        case 'lfg_response':
          this._handleLfgResponse(message)
          break
        default:
          console.warn('[WS] Unknown message type:', message.type)
      }
    },

    _handlePlayerJoined(message) {
      const player = message.player
      if (!player) return

      const userId = player.profile.user_id

      if (!this._matchesCurrentFilters(player)) {
        return
      }

      this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)

      this.activePlayers.unshift(player)
    },

    _handlePlayerLeft(message) {
      const userId = message.user_id
      if (!userId) return

      this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)
    },

    /**
     * Проверяет, подходит ли игрок под текущие клиентские фильтры.
     * Это клиентская фильтрация — серверная остаётся для REST-запросов.
     */
    _matchesCurrentFilters(player) {
      const filters = this.currentFilters
      const elo = player.faceit_data?.elo ?? 0
      const rating = player.rating ?? 0
      const roleIds = (player.profile?.roles || []).map((r) => r.id)

      if (filters.min_elo != null && elo < filters.min_elo) return false
      if (filters.max_elo != null && elo > filters.max_elo) return false

      if (filters.min_rating != null && rating < filters.min_rating) return false

      if (filters.role_ids != null && filters.role_ids.length > 0) {
        const hasMatchingRole = filters.role_ids.some((id) => roleIds.includes(id))
        if (!hasMatchingRole) return false
      }

      return true
    },

    async _syncAfterReconnect() {
      if (this._reconnectAttempts > 0 || this.activePlayers.length === 0) {
        try {
          const response = await api.get('/lfg/active', {
            params: { limit: PAGE_SIZE, offset: 0, ...this.currentFilters },
            paramsSerializer: (params) => serializeParams(params).toString(),
          })
          this.activePlayers = response.data
          this.currentPage = 1
          this.hasMorePlayers = response.data.length >= PAGE_SIZE
        } catch (error) {
          console.error('[WS] Sync after reconnect failed:', error)
        }
      }
    },

    _handleLfgResponse(message) {
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

      this._clearNotificationTimer()
      this._notificationTimer = setTimeout(() => {
        this.dismissNotification()
      }, 12000)
    },

    dismissNotification() {
      this.showNotification = false
      this._clearNotificationTimer()

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

    _clearPingInterval() {
      if (this._pingInterval) {
        clearInterval(this._pingInterval)
        this._pingInterval = null
      }
    },

    _scheduleReconnect() {
      if (this._reconnectAttempts >= 10) {
        console.warn('[WS] Max reconnect attempts reached.')
        return
      }

      const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts), 30000)
      this._reconnectAttempts++
      console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this._reconnectAttempts})`)

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

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
      this.activePlayers = []
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
          this.activePlayers.push(...response.data)
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
        if (message.type === 'status_update') {
          const userProfile = message.user_profile
          const userId = userProfile.profile.user_id

          if (message.is_active) {
            const exists = this.activePlayers.some((p) => p.profile.user_id === userId)
            if (!exists) {
              this.activePlayers.unshift(userProfile)
            }
          } else {
            this.activePlayers = this.activePlayers.filter((p) => p.profile.user_id !== userId)
          }
        }
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
  },
})

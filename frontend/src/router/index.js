import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import Home from '../pages/Home.vue'
import Profile from '../pages/Profile.vue'
import AuthCallback from '../pages/AuthCallback.vue'
import LFGLobby from '@/pages/LFGLobby.vue'
import { isTokenExpired } from '../utils.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true },
    },
    {
      path: '/users/:id',
      name: 'user-profile',
      component: Profile,
      meta: { requiresAuth: true },
    },
    {
      path: '/auth/callback',
      name: 'authCallback',
      component: AuthCallback,
    },
    {
      path: '/lobby',
      name: 'lfg-lobby',
      component: LFGLobby,
      meta: { requiresAuth: true },
    },
  ],
})

/**
 * Пытается обновить access token через refresh cookie.
 * Возвращает true если удалось, false если нет.
 */
async function tryRefreshToken() {
  try {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'https://teamify.pro/api'
    const response = await axios.post(`${baseURL}/auth/refresh`, {}, { withCredentials: true })
    localStorage.setItem('user_token', response.data.access_token)
    return true
  } catch {
    localStorage.removeItem('user_token')
    return false
  }
}

router.beforeEach(async (to, from, next) => {
  const needsAuth = to.meta.requiresAuth || to.name === 'home'

  // Если токен истёк — пытаемся обновить через refresh cookie
  if (needsAuth && isTokenExpired()) {
    await tryRefreshToken()
  }

  const isAuthenticated = !isTokenExpired()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'home' })
  } else if (to.name === 'home' && isAuthenticated) {
    next({ name: 'profile' })
  } else {
    next()
  }
})

export default router

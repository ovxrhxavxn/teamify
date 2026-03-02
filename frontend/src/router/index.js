import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Profile from '../pages/Profile.vue'
import AuthCallback from '../pages/AuthCallback.vue'
import LFGLobby from '@/pages/LFGLobby.vue'
// 1. Импортируем нашу новую функцию
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
      path: '/lfg',
      name: 'lfg-lobby',
      component: LFGLobby,
      meta: { requiresAuth: true },
    },
  ],
})

// 3. Добавляем навигационный страж
router.beforeEach((to, from, next) => {
  const tokenExpired = isTokenExpired()

  // Логика для защищенных маршрутов
  if (to.meta.requiresAuth) {
    if (tokenExpired) {
      // Если токен просрочен, а пользователь пытается зайти на защищенную страницу,
      // удаляем старый токен и перенаправляем на главную.
      localStorage.removeItem('user_token')
      next({ name: 'home' })
    } else {
      // Если токен валиден, разрешаем переход.
      next()
    }
  }
  // Логика для страницы входа (Home.vue)
  else if (to.name === 'home') {
    if (!tokenExpired) {
      // Если пользователь с валидным токеном пытается зайти на главную,
      // перенаправляем его сразу в профиль.
      next({ name: 'profile' })
    } else {
      // Если токена нет или он просрочен, показываем главную страницу.
      next()
    }
  }
  // Для всех остальных маршрутов (например, /auth/callback)
  else {
    next()
  }
})

export default router

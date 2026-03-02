<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Spinner from '@/components/Spinner.vue'
import axios from 'axios'
// 1. Импортируем наше хранилище
import { useUserStore } from '@/stores/user'

onMounted(async () => {
  const route = useRoute()
  const router = useRouter()

  const userStore = useUserStore()

  const code = route.query.code
  const codeVerifier = localStorage.getItem('pkce_code_verifier')

  if (code && codeVerifier) {
    try {
      localStorage.removeItem('pkce_code_verifier')
      const response = await axios.post('https://teamify.pro/api/faceit/oauth2/callback', {
        code: code,
        code_verifier: codeVerifier,
      })

      const accessToken = response.data.access_token
      localStorage.setItem('user_token', accessToken)

      await userStore.fetchUser()

      router.push('/profile')
    } catch (error) {
      console.error('Ошибка авторизации:', error)

      userStore.logout()
      router.push('/')
    }
  } else {
    console.error('Код авторизации или verifier не найдены.')
    router.push('/')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <Spinner text="Выполняется авторизация..." />
  </div>
</template>

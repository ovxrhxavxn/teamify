<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Spinner from '@/components/Spinner.vue'
import api from '@/api'
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

      const response = await api.post('/faceit/oauth2/callback', {
        code: code,
        code_verifier: codeVerifier,
      })

      localStorage.setItem('user_token', response.data.access_token)
      await userStore.fetchUser()
      router.push('/profile')
    } catch (error) {
      console.error('Auth error:', error)
      userStore.logout()
      router.push('/')
    }
  } else {
    console.error('Auth code or verifier not found.')
    router.push('/')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <Spinner text="Выполняется авторизация..." />
  </div>
</template>

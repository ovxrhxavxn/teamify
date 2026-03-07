<script setup>
import { onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useLfgStore } from '@/stores/lfg'
import LFGNotification from '@/components/LFGNotification.vue'

const userStore = useUserStore()
const lfgStore = useLfgStore()

const theme = {
  token: {
    colorPrimary: '#000000',
  },
}

onMounted(async () => {
  await userStore.fetchUser()
})

watch(
  () => userStore.isAuthenticated,
  (isAuth, wasAuth) => {
    if (isAuth && !lfgStore.socket) {
      lfgStore.connectWebSocket()
    } else if (!isAuth && wasAuth) {
      lfgStore.disconnectWebSocket()
    }
  },
  { immediate: true },
)
</script>

<template>
  <a-config-provider :theme="theme">
    <router-view />
    <LFGNotification />
  </a-config-provider>
</template>

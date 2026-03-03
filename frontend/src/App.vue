<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const theme = {
  token: {
    colorPrimary: '#000000',
  },
}

onMounted(() => {
  userStore.fetchUser()
})
</script>

<template>
  <a-config-provider :theme="theme">
    <router-view />
  </a-config-provider>
</template>

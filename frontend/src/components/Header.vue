<script setup>
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

function goToProfile() {
  router.push({ name: 'profile' })
}

function goToHome() {
  router.push({ name: 'home' })
}

function goToLFG() {
  router.push({ name: 'lfg-lobby' })
}
</script>

<template>
  <header
    class="h-20 border-b-2 border-black bg-white flex items-center justify-between px-6 lg:px-12 sticky top-0 z-50"
  >
    <a @click="goToHome" class="flex items-center gap-3 group cursor-pointer">
      <div class="relative w-10 h-10">
        <img src="/img/logo.png" />
      </div>
      <span class="text-2xl font-black uppercase tracking-tighter">Teamify</span>
    </a>
    <div class="flex items-center gap-6">
      <!-- Ссылка №1: LFG-лента -->
      <a
        @click="goToLFG"
        class="hidden md:flex items-center gap-2 hover:opacity-70 transition-opacity cursor-pointer"
      >
        <img src="/img/lfg_icon.svg" width="21" height="21" />
        <span
          class="font-black uppercase text-sm tracking-tight border-b-2 border-transparent hover:border-black transition-all"
        >
          LFG-лента
        </span>
      </a>

      <div class="h-8 w-[2px] bg-gray-200 hidden md:block"></div>

      <div v-if="userStore.isAuthenticated && userStore.profile">
        <a @click="goToProfile">
          <div class="flex items-center gap-3 hover:opacity-70 transition-opacity cursor-pointer">
            <div class="text-right hidden sm:block">
              <div class="font-bold text-sm uppercase">
                {{ userStore.profile.faceit_data.nickname }}
              </div>
              <div class="text-xs font-mono bg-black text-white px-1 inline-block">
                {{ userStore.profile.faceit_data.elo }} ELO
              </div>
            </div>

            <div
              class="w-10 h-10 border-2 border-black bg-gray-100 flex items-center justify-center overflow-hidden"
            >
              <img
                v-if="userStore.profile.faceit_data.avatar"
                :src="userStore.profile.faceit_data.avatar"
                alt="Аватар пользователя"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-xl font-black text-gray-400">
                {{ userStore.profile.faceit_data.nickname.charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>
        </a>
      </div>
      <div class="h-8 w-[2px] bg-gray-200 hidden md:block"></div>
      <!-- Если нет - показываем кнопку "Выйти" или ничего (пока что) -->
      <div v-if="userStore.isAuthenticated">
        <button @click="userStore.logout()" class="text-sm uppercase font-bold hover:opacity-70">
          <img src="/img/logout.svg" width="21" height="21" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useLfgStore } from '@/stores/lfg'

const lfgStore = useLfgStore()
const notification = computed(() => lfgStore.currentNotification)
const visible = computed(() => lfgStore.showNotification)
</script>

<template>
  <Transition name="slide-in">
    <div
      v-if="visible && notification"
      class="fixed z-[100] border-2 border-black bg-white shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] bottom-4 left-4 right-4 sm:bottom-auto sm:left-auto sm:top-24 sm:right-6 sm:w-[380px]"
    >
      <!-- Заголовок -->
      <div
        class="bg-[#FF5500] text-white px-3 py-2 sm:px-4 flex justify-between items-center border-b-2 border-black"
      >
        <span class="font-black uppercase text-xs sm:text-sm tracking-wide">
          🔔 Новый отклик!
        </span>
        <button
          @click="lfgStore.dismissNotification()"
          class="text-white hover:opacity-70 font-bold text-lg leading-none ml-2"
        >
          ×
        </button>
      </div>

      <!-- Контент -->
      <div class="p-3 sm:p-4">
        <div class="flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
          <!-- Аватар -->
          <div
            class="w-10 h-10 sm:w-14 sm:h-14 border-2 border-black bg-gray-100 flex items-center justify-center overflow-hidden flex-shrink-0"
          >
            <img
              v-if="notification.responder_avatar"
              :src="notification.responder_avatar"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-lg sm:text-2xl font-black text-gray-400">
              {{ notification.responder_nickname.charAt(0).toUpperCase() }}
            </span>
          </div>

          <!-- Инфо -->
          <div class="flex-1 min-w-0">
            <div class="font-black text-base sm:text-lg uppercase tracking-tight truncate">
              {{ notification.responder_nickname }}
            </div>
            <div class="flex items-center gap-2 sm:gap-3 mt-1">
              <span
                class="text-[10px] sm:text-xs font-mono bg-black text-white px-1 sm:px-1.5 py-0.5"
              >
                LVL {{ notification.responder_lvl }}
              </span>
              <span
                class="text-[10px] sm:text-xs font-mono bg-gray-100 px-1 sm:px-1.5 py-0.5 border border-black"
              >
                {{ notification.responder_elo }} ELO
              </span>
            </div>
          </div>
        </div>

        <p class="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          Хочет играть с тобой! Добавь в друзья на Faceit:
        </p>

        <a
          :href="notification.responder_faceit_url"
          target="_blank"
          rel="noopener noreferrer"
          class="block w-full py-2.5 sm:py-3 text-center font-black uppercase text-xs sm:text-sm border-2 border-black bg-[#FF5500] text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all"
        >
          Открыть профиль на Faceit ↗
        </a>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Desktop: слайд справа */
@media (min-width: 640px) {
  .slide-in-enter-active {
    animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .slide-in-leave-active {
    animation: slideInRight 0.3s ease-in reverse;
  }
}

/* Mobile: слайд снизу */
@media (max-width: 639px) {
  .slide-in-enter-active {
    animation: slideInUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .slide-in-leave-active {
    animation: slideInUp 0.3s ease-in reverse;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    transform: translateY(120%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>

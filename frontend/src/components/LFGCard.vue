<!-- LFGCard.vue -->
<script setup>
import { computed, ref } from 'vue'
import RatingStars from '@/components/RatingStars.vue'
import { formatStat } from '@/utils'
import api from '@/api'

const props = defineProps({
  profileData: {
    type: Object,
    required: true,
  },
})

const userId = computed(() => props.profileData.profile.user_id)
const faceitData = computed(() => props.profileData.faceit_data)
const rating = computed(() => props.profileData.rating)
const roles = computed(() => props.profileData.profile.roles || [])

const hasResponded = ref(false)
const isResponding = ref(false)
const cooldownMessage = ref('')
const showSuccessAnimation = ref(false)

async function respondToPlayer(event) {
  event.preventDefault()
  event.stopPropagation()
  if (hasResponded.value || isResponding.value) return

  isResponding.value = true
  cooldownMessage.value = ''

  try {
    await api.post('/lfg/responses', {
      target_user_id: userId.value,
    })
    // Показываем анимацию успеха
    showSuccessAnimation.value = true
    setTimeout(() => {
      hasResponded.value = true
      showSuccessAnimation.value = false
    }, 600)
  } catch (error) {
    if (error.response?.status === 409) {
      hasResponded.value = true
    } else if (error.response?.status === 429) {
      hasResponded.value = true
      cooldownMessage.value = error.response.data.detail
    } else {
      console.error('Error responding:', error)
    }
  } finally {
    isResponding.value = false
  }
}
</script>

<template>
  <div
    class="bg-white border-2 border-black p-0 flex flex-col hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-shadow duration-200"
  >
    <router-link :to="{ name: 'user-profile', params: { id: userId } }" class="flex-1">
      <div class="bg-gray-50 border-b-2 border-black p-4 flex justify-between items-center h-20">
        <div class="flex flex-col items-center justify-center min-w-[60px]">
          <div class="font-black text-xl leading-none">
            {{ formatStat(faceitData.lvl) }}
          </div>
          <div class="text-[10px] uppercase font-bold text-gray-500">LVL</div>
        </div>
        <div class="h-full w-[2px] bg-gray-200 mx-4"></div>
        <div class="flex flex-col items-center justify-center min-w-[60px]">
          <div class="font-black text-xl leading-none">
            {{ formatStat(faceitData.elo) }}
          </div>
          <div class="text-[10px] uppercase font-bold text-gray-500">ELO</div>
        </div>
        <div class="h-full w-[2px] bg-gray-200 mx-4"></div>
        <div class="flex flex-col items-center justify-center min-w-[60px]">
          <div class="font-black text-xl leading-none">
            {{ formatStat(faceitData.k_d_ratio) }}
          </div>
          <div class="text-[10px] uppercase font-bold text-gray-500">K/D</div>
        </div>
      </div>

      <div class="p-5 flex-1 flex flex-col items-center text-center">
        <div
          class="w-20 h-20 border-2 border-black mb-3 flex items-center justify-center bg-gray-100 overflow-hidden"
        >
          <img
            v-if="faceitData.avatar"
            :src="faceitData.avatar"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-3xl font-black text-gray-400">
            {{ faceitData.nickname.charAt(0).toUpperCase() }}
          </span>
        </div>

        <h3 class="font-black text-xl uppercase tracking-tight mb-1">
          {{ faceitData.nickname }}
        </h3>

        <div class="mb-3">
          <RatingStars :rating="rating" />
        </div>

        <div class="flex flex-wrap justify-center gap-2 mt-auto pt-4" v-if="roles.length > 0">
          <span
            v-for="role in roles"
            :key="role.id"
            class="bg-black text-white font-mono text-xs uppercase px-2 py-1"
          >
            {{ role.name }}
          </span>
        </div>
      </div>
    </router-link>

    <div class="border-t-2 border-black">
      <!-- Успешный отклик -->
      <button v-if="hasResponded" disabled class="respond-btn respond-btn--success group">
        <div class="respond-btn__bg bg-green-500"></div>
        <div class="respond-btn__content">
          <svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
          <span>Отклик отправлен</span>
        </div>
      </button>

      <button
        v-else-if="showSuccessAnimation"
        disabled
        class="respond-btn respond-btn--success-anim"
      >
        <div class="respond-btn__bg bg-green-500 animate-expand-right"></div>
        <div class="respond-btn__content">
          <svg class="w-5 h-5 animate-scale-in" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </button>

      <button v-else-if="isResponding" disabled class="respond-btn respond-btn--loading">
        <div class="respond-btn__bg bg-[#FF5500] animate-pulse-slow"></div>
        <div class="respond-btn__content">
          <div class="flex items-center gap-2">
            <span class="respond-dots">
              <span class="respond-dot"></span>
              <span class="respond-dot"></span>
              <span class="respond-dot"></span>
            </span>
            <span>Отправляем</span>
          </div>
        </div>
      </button>

      <button v-else @click="respondToPlayer" class="respond-btn respond-btn--default group">
        <div class="respond-btn__bg bg-[#FF5500] group-hover:bg-[#e04b00]"></div>
        <!-- Полоска-заливка при наведении -->
        <div class="respond-btn__hover-fill"></div>
        <div class="respond-btn__content">
          <span class="respond-btn__icon">
            <!-- Иконка рукопожатия / стрелка -->
            <svg
              class="w-5 h-5 transition-transform duration-300 group-hover:rotate-12 group-hover:scale-110"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
          <span class="respond-btn__text">
            <span class="group-hover:hidden">Откликнуться</span>
            <span class="hidden group-hover:inline font-black tracking-wider">Го играть! 🔥</span>
          </span>
        </div>

        <div class="respond-btn__corner"></div>
      </button>

      <div v-if="cooldownMessage" class="bg-yellow-50 border-t border-yellow-200 px-3 py-2">
        <p
          class="text-[11px] text-yellow-700 font-bold text-center flex items-center justify-center gap-1"
        >
          <span>⏳</span>
          {{ cooldownMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.respond-btn {
  position: relative;
  width: 100%;
  height: 52px;
  overflow: hidden;
  cursor: pointer;
  border: none;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.respond-btn:disabled {
  cursor: default;
}

.respond-btn__bg {
  position: absolute;
  inset: 0;
  transition: background-color 0.3s ease;
}

.respond-btn__content {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 900;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: transform 0.2s ease;
}

.respond-btn--default {
  border-top: 0;
}

.respond-btn--default:hover .respond-btn__content {
  transform: translateX(4px);
}

.respond-btn__hover-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: rgba(0, 0, 0, 0.15);
  transition: width 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 5;
}

.respond-btn--default:hover .respond-btn__hover-fill {
  width: 100%;
}

.respond-btn__corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 24px 24px 0;
  border-color: transparent rgba(0, 0, 0, 0.1) transparent transparent;
  z-index: 5;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.respond-btn--default:hover .respond-btn__corner {
  opacity: 1;
}

.respond-btn--default:active .respond-btn__content {
  transform: translateX(2px) scale(0.97);
}

.respond-btn--success {
  cursor: default;
}

@keyframes expand-right {
  from {
    clip-path: inset(0 100% 0 0);
  }
  to {
    clip-path: inset(0 0 0 0);
  }
}

.animate-expand-right {
  animation: expand-right 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

@keyframes scale-in {
  0% {
    transform: scale(0) rotate(-180deg);
    opacity: 0;
  }
  60% {
    transform: scale(1.2) rotate(10deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

.animate-scale-in {
  animation: scale-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s both;
}

@keyframes pulse-slow {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 1.5s ease-in-out infinite;
}

.respond-dots {
  display: inline-flex;
  gap: 3px;
}

.respond-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: dot-bounce 1.2s ease-in-out infinite;
}

.respond-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.respond-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes dot-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}
</style>

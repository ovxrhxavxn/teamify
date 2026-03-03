<script setup>
import { computed } from 'vue'
import RatingStars from '@/components/RatingStars.vue'
import { getLevelColorClass, formatStat, getKDColorClass } from '@/utils'

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
const levelColor = computed(() => getLevelColorClass(faceitData.value.lvl))
</script>

<template>
  <router-link
    :to="{ name: 'user-profile', params: { id: userId } }"
    class="bg-white border-2 border-black p-0 flex flex-col hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-shadow duration-200"
  >
    <div class="bg-gray-50 border-b-2 border-black p-4 flex justify-between items-center h-20">
      <div class="flex flex-col items-center justify-center min-w-[60px]">
        <div :class="levelColor" class="font-black text-xl leading-none">
          {{ formatStat(faceitData.lvl) }}
        </div>
        <div class="text-[10px] uppercase font-bold text-gray-500">LVL</div>
      </div>
      <div class="h-full w-[2px] bg-gray-200 mx-4"></div>
      <div class="flex flex-col items-center justify-center min-w-[60px]">
        <div class="font-black text-xl leading-none">{{ formatStat(faceitData.elo) }}</div>
        <div class="text-[10px] uppercase font-bold text-gray-500">ELO</div>
      </div>
      <div class="h-full w-[2px] bg-gray-200 mx-4"></div>
      <div class="flex flex-col items-center justify-center min-w-[60px]">
        <div :class="getKDColorClass(faceitData.k_d_ratio)" class="font-black text-xl leading-none">
          {{ formatStat(faceitData.k_d_ratio) }}
        </div>
        <div class="text-[10px] uppercase font-bold text-gray-500">K/D</div>
      </div>
    </div>
    <div class="p-5 flex-1 flex flex-col items-center text-center">
      <div
        class="w-20 h-20 border-2 border-black mb-3 flex items-center justify-center bg-gray-100 overflow-hidden"
      >
        <img v-if="faceitData.avatar" :src="faceitData.avatar" class="w-full h-full object-cover" />
        <span v-else class="text-3xl font-black text-gray-400">
          {{ faceitData.nickname.charAt(0).toUpperCase() }}
        </span>
      </div>
      <h3 class="font-black text-xl uppercase tracking-tight mb-1">{{ faceitData.nickname }}</h3>
      <div class="mb-3">
        <RatingStars :rating="rating" />
      </div>
      <div class="flex flex-wrap justify-center gap-2 mt-auto pt-4" v-if="roles.length > 0">
        <span
          v-for="role in roles"
          :key="role.id"
          class="border border-gray-400 text-gray-800 text-xs font-bold uppercase px-3 py-1"
        >
          {{ role.name }}
        </span>
      </div>
    </div>
  </router-link>
</template>

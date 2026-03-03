<script setup>
import { computed } from 'vue'

const props = defineProps({
  review: {
    type: Object,
    required: true,
  },
})

const formattedDate = computed(() => {
  return new Date(props.review.created_at).toLocaleDateString()
})
</script>

<template>
  <div
    class="border border-black p-4 mb-4 bg-white hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all"
  >
    <div class="flex justify-between items-start mb-3">
      <div class="flex items-center gap-3">
        <div
          class="w-8 h-8 bg-gray-100 border border-black flex items-center justify-center overflow-hidden"
        >
          <img
            v-if="review.author.avatar"
            :src="review.author.avatar"
            class="w-full h-full object-cover"
          />
          <span v-else class="font-bold text-xs">{{ review.author.nickname.charAt(0) }}</span>
        </div>
        <div>
          <div class="font-bold text-sm uppercase">{{ review.author.nickname }}</div>
          <div class="text-xs text-gray-500">{{ formattedDate }}</div>
        </div>
      </div>

      <div class="flex items-center gap-1 text-yellow-500">
        <img
          v-for="star in 5"
          :key="star"
          :src="star <= review.rating ? '/img/star-fill.svg' : '/img/star.svg'"
          width="14"
          height="14"
        />
      </div>
    </div>
    <div class="relative pl-6">
      <img src="/img/quote.svg" width="12" height="12" class="absolute left-0 top-1 opacity-50" />
      <div class="text-sm font-medium italic text-gray-800">
        {{ review.content }}
      </div>
    </div>
  </div>
</template>

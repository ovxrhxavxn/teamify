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
  <router-link
    :to="{ name: 'user-profile', params: { id: review.author_id } }"
    class="block border border-black p-3 sm:p-4 mb-3 sm:mb-4 bg-white hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all cursor-pointer"
  >
    <div
      class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 sm:gap-0 mb-2 sm:mb-3"
    >
      <div class="flex items-center gap-2 sm:gap-3">
        <div
          class="w-7 h-7 sm:w-8 sm:h-8 bg-gray-100 border border-black flex items-center justify-center overflow-hidden flex-shrink-0"
        >
          <img
            v-if="review.author.avatar"
            :src="review.author.avatar"
            class="w-full h-full object-cover"
          />
          <span v-else class="font-bold text-[10px] sm:text-xs">
            {{ review.author.nickname.charAt(0) }}
          </span>
        </div>
        <div class="min-w-0">
          <div class="font-bold text-xs sm:text-sm uppercase truncate">
            {{ review.author.nickname }}
          </div>
          <div class="text-[10px] sm:text-xs text-gray-500">{{ formattedDate }}</div>
        </div>
      </div>
      <div class="flex items-center gap-0.5 text-yellow-500 flex-shrink-0">
        <img
          v-for="star in 5"
          :key="star"
          :src="star <= review.rating ? '/img/star-fill.svg' : '/img/star.svg'"
          width="12"
          height="12"
          class="sm:w-[14px] sm:h-[14px]"
        />
      </div>
    </div>

    <!-- Текст отзыва -->
    <div class="relative pl-4 sm:pl-6">
      <img
        src="/img/quote.svg"
        width="10"
        height="10"
        class="absolute left-0 top-1 opacity-50 sm:w-[12px] sm:h-[12px]"
      />
      <div class="text-xs sm:text-sm font-medium italic text-gray-800 break-words">
        {{ review.content }}
      </div>
    </div>
  </router-link>
</template>

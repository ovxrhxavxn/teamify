<!-- frontend/src/components/RatingStars.vue -->
<script setup>
import { computed } from 'vue'

const props = defineProps({
  rating: {
    type: Number,
    required: true,
  },
})

const fullStars = computed(() => Math.round(props.rating))

const ratingColorClass = computed(() => {
  if (props.rating >= 4.0) return 'text-green-500'
  if (props.rating >= 2.5) return 'text-yellow-500'
  return 'text-red-500'
})
</script>

<!-- frontend/src/components/RatingStars.vue -->
<template>
  <div class="flex items-center gap-2">
    <!-- Звезды -->
    <div class="flex items-center gap-0.5 text-yellow-400">
      <img
        v-for="star in 5"
        :key="star"
        :src="star <= fullStars ? '/img/star-fill.svg' : '/img/star.svg'"
        width="16"
        height="16"
      />
    </div>

    <!-- Числовое значение рейтинга -->
    <!-- 
      Теперь скобки серого цвета, а само число внутри них
      получает динамический цвет из computed свойства.
    -->
    <span class="text-gray-400 font-medium text-sm">
      (
      <span :class="ratingColorClass" class="font-bold">
        {{ rating.toFixed(1) }}
      </span>
      )
    </span>
  </div>
</template>

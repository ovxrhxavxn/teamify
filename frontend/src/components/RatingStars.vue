<script setup>
import { computed } from 'vue'
import { getRatingColorClass } from '@/utils'

const props = defineProps({
  rating: {
    type: Number,
    required: true,
  },
})

const hasRating = computed(() => props.rating > 0)
const fullStars = computed(() => Math.round(props.rating))
const ratingColorClass = computed(() => getRatingColorClass(props.rating))
</script>

<template>
  <div class="flex items-center gap-2">
    <template v-if="hasRating">
      <div class="flex items-center gap-0.5 text-yellow-400">
        <img
          v-for="star in 5"
          :key="star"
          :src="star <= fullStars ? '/img/star-fill.svg' : '/img/star.svg'"
          width="16"
          height="16"
        />
      </div>
      <span class="text-gray-400 font-medium text-sm">
        (
        <span :class="ratingColorClass" class="font-bold">
          {{ rating.toFixed(1) }}
        </span>
        )
      </span>
    </template>
    <span v-else class="text-gray-400 font-medium text-sm">Нет оценок</span>
  </div>
</template>

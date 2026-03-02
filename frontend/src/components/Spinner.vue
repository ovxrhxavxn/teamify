<template>
  <div class="flex flex-col items-center justify-center gap-4">
    <div
      :class="spinnerClasses"
      class="animate-spin rounded-full border-solid border-black border-r-transparent"
      role="status"
    >
      <span class="sr-only">Загрузка...</span>
    </div>
    <p v-if="text" class="text-sm font-medium text-gray-600">{{ text }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md', // 'sm', 'md', 'lg'
  },
})

const spinnerClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-6 w-6 border-2'
    case 'lg':
      return 'h-16 w-16 border-4'
    default: // md
      return 'h-12 w-12 border-4'
  }
})
</script>

<style scoped>
/* 
  `sr-only` - это стандартный класс для скрытия элемента визуально, 
  но оставления его доступным для скринридеров (для людей с ограниченными возможностями).
  Tailwind CSS уже включает этот класс, но на всякий случай можно добавить его здесь,
  если у вас кастомная сборка.
*/
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

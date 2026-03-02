<script setup>
import { onMounted, onUnmounted, computed, ref, watch } from 'vue'
import Header from '@/components/Header.vue'
import LFGCard from '@/components/LFGCard.vue'
import Spinner from '@/components/Spinner.vue'
import { useLfgStore } from '@/stores/lfg'

const lfgStore = useLfgStore()
// Состояния для фильтров
const eloRange = ref([0, 4500])
const minRating = ref(1)
const selectedRoles = ref([])
// Отфильтрованный список игроков
const filteredPlayers = computed(() => {
  return lfgStore.activePlayers.filter((player) => {
    const elo = player.faceit_data.elo
    const inEloRange = elo >= eloRange.value[0] && elo <= eloRange.value[1]
    // TODO: Добавить фильтрацию по рейтингу и ролям, когда эти данные будут
    return inEloRange
  })
})
// --- Логика для Intersection Observer ---
const observerTarget = ref(null)
let observer = null
// Следим за элементом-триггером. Когда он появляется/исчезает,
// мы создаем/отключаем наблюдатель.
watch(observerTarget, (newEl) => {
  if (newEl) {
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          lfgStore.fetchMorePlayers()
        }
      },
      { threshold: 0.1 },
    )
    observer.observe(newEl)
  } else if (observer) {
    observer.disconnect()
    observer = null
  }
})
onMounted(() => {
  lfgStore.fetchMyStatus()
  lfgStore.fetchInitialPlayers()
  lfgStore.connectWebSocket()
})
onUnmounted(() => {
  lfgStore.disconnectWebSocket()
  if (observer) {
    observer.disconnect()
  }
})
</script>
<template>
  <Header></Header>
  <div class="min-h-screen bg-gray-100">
    <main class="max-w-[1600px] mx-auto px-6 py-8">
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- ASIDE / САЙДБАР -->
        <aside class="w-full lg:w-80 flex-shrink-0">
          <div class="sticky top-24 space-y-8">
            <!-- Блок "Поиск активен" -->
            <div class="bg-white p-4 border-2 border-black space-y-3">
              <div class="flex items-center justify-between">
                <span class="font-black uppercase tracking-tight text-md">ПОИСК АКТИВЕН</span>
                <a-switch :checked="lfgStore.isSearching" @change="lfgStore.toggleSearchStatus" />
              </div>
            </div>
            <!-- Блок Фильтров -->
            <div class="bg-white p-6 border-2 border-black">
              <div class="flex items-center gap-2 mb-6 border-b-2 border-black pb-2">
                <img src="/img/funnel.svg" height="22" width="22" />
                <h3 class="font-black text-lg uppercase">Фильтры</h3>
              </div>
              <div class="mb-6">
                <div class="flex items-center justify-between mb-2">
                  <label class="text-xs font-bold uppercase flex items-center gap-1">
                    <img src="/img/trophy.svg" height="16" width="16" />
                    ELO Range
                  </label>
                  <span class="text-xs font-mono"
                    >{{ eloRange[0] }} - {{ eloRange[1] >= 4500 ? '4500+' : eloRange[1] }}</span
                  >
                </div>
                <a-slider v-model:value="eloRange" range :min="0" :max="4500" />
              </div>
              <div class="mb-6">
                <label class="block text-xs font-bold uppercase flex items-center gap-1 mb-2">
                  <img src="/img/star.svg" height="16" width="16" />
                  Min. Rating
                </label>
                <a-select v-model:value="minRating" class="w-full">
                  <a-select-option :value="1">1+ Stars</a-select-option>
                  <a-select-option :value="2">2+ Stars</a-select-option>
                  <a-select-option :value="3">3+ Stars</a-select-option>
                  <a-select-option :value="4">4+ Stars</a-select-option>
                  <a-select-option :value="5">5 Stars</a-select-option>
                </a-select>
              </div>
              <div>
                <label class="block text-xs font-bold uppercase flex items-center gap-1 mb-3">
                  <img src="/img/people.svg" height="16" width="16" />
                  Roles
                </label>
                <a-checkbox-group v-model:value="selectedRoles" class="w-full">
                  <div class="grid grid-cols-2 gap-2">
                    <a-checkbox value="AWP">AWP</a-checkbox>
                    <a-checkbox value="RIFLER">RIFLER</a-checkbox>
                    <a-checkbox value="ENTRY">ENTRY</a-checkbox>
                    <a-checkbox value="SUPPORT">SUPPORT</a-checkbox>
                    <a-checkbox value="IGL">IGL</a-checkbox>
                    <a-checkbox value="LURKER">LURKER</a-checkbox>
                  </div>
                </a-checkbox-group>
              </div>
            </div>
          </div>
        </aside>
        <!-- Основной контент -->
        <div class="flex-1">
          <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-black uppercase flex items-center gap-2">
              Игроки в поиске
              <span class="bg-black text-white px-2 text-sm py-1 rounded-sm">{{
                filteredPlayers.length
              }}</span>
            </h1>
          </div>
          <!-- Состояние первоначальной загрузки -->
          <div v-if="lfgStore.isLoading" class="flex justify-center py-10">
            <Spinner text="Загрузка игроков..." />
          </div>
          <!-- Есть игроки для отображения -->
          <div v-else-if="filteredPlayers.length > 0">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
              <LFGCard
                v-for="player in filteredPlayers"
                :key="player.profile.id"
                :profileData="player"
              />
            </div>
            <!-- Индикатор подгрузки следующих -->
            <div v-if="lfgStore.isLoadingMore" class="mt-12 flex justify-center">
              <Spinner size="sm" />
            </div>
            <!-- Элемент-триггер для подгрузки -->
            <div v-if="lfgStore.hasMorePlayers" ref="observerTarget" style="height: 50px"></div>
          </div>
          <!-- Игроки не найдены -->
          <div v-else class="text-center py-10 text-gray-500">
            В данный момент нет игроков, соответствующих вашим фильтрам.
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

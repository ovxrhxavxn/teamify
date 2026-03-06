<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Header from '@/components/Header.vue'
import RatingStars from '@/components/RatingStars.vue'
import Review from '@/components/Review.vue'
import Spinner from '@/components/Spinner.vue'
import {
  formatStat,
  getKDColorClass,
  getKRColorClass,
  getWinRateColorClass,
  getHeadshotColorClass,
  getADRColorClass,
  getMatchesColorClass,
  getWinStreakColorClass,
} from '@/utils'
import api from '@/api'

const route = useRoute()
const userStore = useUserStore()

const viewedProfile = ref(null)
const isLoadingProfile = ref(true)

const REVIEWS_PAGE_SIZE = 10
const reviews = ref([])
const reviewsCurrentPage = ref(0)
const reviewsLoading = ref(true)
const isReviewsLoadingMore = ref(false)
const hasMoreReviews = ref(true)
const reviewsObserverTarget = ref(null)
let observer = null

const isEditing = ref(false)
const editableDescription = ref('')
const newReviewContent = ref('')
const newReviewRating = ref(0)
const isSubmittingReview = ref(false)
const hoverRating = ref(0)

const allRoles = ref([])
const isEditingRoles = ref(false)
const selectedRoleIds = ref([])

const isOwnProfile = computed(() => {
  if (!userStore.isAuthenticated || !viewedProfile.value) return false
  return userStore.profile.profile.user_id === viewedProfile.value.profile.user_id
})

const targetUserId = computed(() => {
  if (route.params.id) return route.params.id
  if (userStore.profile) return userStore.profile.profile.user_id
  return null
})

function getLevelBgClass(level) {
  if (!level) return 'bg-gray-400'
  if (level >= 10) return 'bg-red-500'
  if (level >= 8) return 'bg-orange-500'
  if (level >= 5) return 'bg-yellow-500'
  return 'bg-green-500'
}

onMounted(async () => {
  try {
    const response = await api.get('/profiles/roles')
    allRoles.value = response.data
  } catch (error) {
    console.error('Error loading roles:', error)
  }
})

const loadMoreReviews = async () => {
  if (isReviewsLoadingMore.value || !hasMoreReviews.value || !viewedProfile.value) return
  if (reviewsCurrentPage.value === 0) {
    reviewsLoading.value = true
  } else {
    isReviewsLoadingMore.value = true
  }
  try {
    const response = await api.get(`/reviews/${viewedProfile.value.profile.id}`, {
      params: {
        limit: REVIEWS_PAGE_SIZE,
        offset: reviewsCurrentPage.value * REVIEWS_PAGE_SIZE,
      },
    })
    if (response.data.length > 0) {
      reviews.value.push(...response.data)
      reviewsCurrentPage.value++
    }
    if (response.data.length < REVIEWS_PAGE_SIZE) {
      hasMoreReviews.value = false
      if (observer) observer.disconnect()
    }
  } catch (error) {
    console.error('Error loading reviews:', error)
  } finally {
    reviewsLoading.value = false
    isReviewsLoadingMore.value = false
  }
}

const loadProfile = async (userId) => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
  isLoadingProfile.value = true
  viewedProfile.value = null
  reviews.value = []
  reviewsCurrentPage.value = 0
  hasMoreReviews.value = true
  try {
    const profileResponse = await api.get(`/profiles/${userId}`)
    viewedProfile.value = profileResponse.data
    await loadMoreReviews()
  } catch (error) {
    console.error('Error loading profile:', error)
  } finally {
    isLoadingProfile.value = false
  }
}

watch(
  targetUserId,
  (newUserId) => {
    if (newUserId) loadProfile(newUserId)
  },
  { immediate: true },
)

watch(reviewsObserverTarget, (newEl, oldEl) => {
  if (newEl) {
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMoreReviews()
      },
      { threshold: 0.1 },
    )
    observer.observe(newEl)
  } else if (oldEl && observer) {
    observer.disconnect()
    observer = null
  }
})

async function submitReview() {
  if (newReviewContent.value.trim() === '' || newReviewRating.value === 0) {
    alert('Пожалуйста, напишите отзыв и поставьте оценку.')
    return
  }
  isSubmittingReview.value = true
  try {
    const response = await api.post(`/reviews/${viewedProfile.value.profile.id}`, {
      content: newReviewContent.value,
      rating: newReviewRating.value,
    })
    if (viewedProfile.value) {
      viewedProfile.value.rating = response.data.new_average_rating
      viewedProfile.value.total_reviews += 1
    }
    reviews.value = []
    reviewsCurrentPage.value = 0
    hasMoreReviews.value = true
    await loadMoreReviews()
    newReviewContent.value = ''
    newReviewRating.value = 0
  } catch (error) {
    console.error('Error submitting review:', error)
    alert(error.response?.data?.detail || 'Не удалось добавить отзыв.')
  } finally {
    isSubmittingReview.value = false
  }
}

function startEditing() {
  editableDescription.value = viewedProfile.value.profile.description || ''
  isEditing.value = true
}

function cancelEditing() {
  isEditing.value = false
}

async function saveProfile() {
  await userStore.updateProfileDescription(editableDescription.value)
  if (viewedProfile.value) {
    viewedProfile.value.profile.description = editableDescription.value
  }
  isEditing.value = false
}

function startEditingRoles() {
  selectedRoleIds.value = (viewedProfile.value.profile.roles || []).map((role) => role.id)
  isEditingRoles.value = true
}

function cancelEditingRoles() {
  isEditingRoles.value = false
}

async function saveRoles() {
  const newRoles = await userStore.updateProfileRoles(selectedRoleIds.value)
  if (newRoles !== null && viewedProfile.value) {
    viewedProfile.value.profile.roles = newRoles
  }
  isEditingRoles.value = false
}
</script>

<template>
  <Header />

  <div v-if="isLoadingProfile" class="text-center py-20">
    <Spinner />
  </div>

  <main v-else-if="viewedProfile" class="max-w-5xl mx-auto px-4 py-12">
    <div class="flex flex-col md:flex-row gap-12">
      <!-- Sidebar -->
      <div class="w-full md:w-1/3">
        <div
          class="relative border-2 border-black p-6 text-center sticky top-24 hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all"
        >
          <!-- Стикер уровня -->
          <div
            v-if="viewedProfile.faceit_data.lvl >= 10"
            class="absolute -top-3 -right-3 bg-red-500 text-white text-[10px] font-black uppercase px-2 py-1 rotate-12 border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] z-10"
          >
            🔥 LVL 10
          </div>
          <div
            v-else-if="viewedProfile.faceit_data.lvl >= 8"
            class="absolute -top-3 -right-3 bg-orange-400 text-white text-[10px] font-black uppercase px-2 py-1 -rotate-6 border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] z-10"
          >
            ⚡ PRO
          </div>

          <!-- Аватар с аннотацией -->
          <div class="relative mx-auto mb-6">
            <div
              class="absolute -left-16 top-1/2 -translate-y-1/2 -rotate-6 hidden md:flex items-center gap-1 z-10 select-none pointer-events-none"
            >
              <span
                class="bg-[#FF5500] text-white text-[10px] font-black uppercase px-2 py-1 tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
              >
                faceit ↗
              </span>
              <span class="text-black text-lg leading-none">→</span>
            </div>

            <a
              :href="`https://www.faceit.com/en/players/${viewedProfile.faceit_data.nickname}`"
              target="_blank"
              rel="noopener noreferrer"
              class="block w-32 h-32 border-2 border-black bg-gray-200 mx-auto flex items-center justify-center overflow-hidden cursor-pointer hover:border-4 transition-all"
            >
              <img
                v-if="viewedProfile.faceit_data.avatar"
                :src="viewedProfile.faceit_data.avatar"
                alt="Avatar"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-5xl font-black text-gray-500">
                {{ viewedProfile.faceit_data.nickname.charAt(0).toUpperCase() }}
              </span>
            </a>

            <a
              :href="`https://www.faceit.com/en/players/${viewedProfile.faceit_data.nickname}`"
              target="_blank"
              rel="noopener noreferrer"
              class="md:hidden inline-block mt-2 bg-[#FF5500] text-white text-[10px] font-black uppercase px-2 py-1 tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all"
            >
              faceit профиль ↗
            </a>
          </div>

          <h1 class="text-3xl font-black uppercase tracking-tighter mb-1">
            {{ viewedProfile.faceit_data.nickname }}
          </h1>

          <div class="mb-4 flex justify-center">
            <RatingStars :rating="viewedProfile.rating" />
          </div>

          <!-- Уровень и ELO -->
          <div class="grid grid-cols-2 gap-4 border-t-2 border-black pt-6 mb-6">
            <div class="text-center">
              <div
                class="inline-flex items-center justify-center w-12 h-12 border-2 border-black font-black text-xl text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"
                :class="getLevelBgClass(viewedProfile.faceit_data.lvl)"
              >
                {{ viewedProfile.faceit_data.lvl }}
              </div>
              <div class="text-[10px] uppercase font-bold text-gray-500 mt-1">Уровень</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-black leading-none">
                {{ formatStat(viewedProfile.faceit_data.elo) }}
              </div>
              <div class="text-[10px] uppercase font-bold text-gray-500">Очки ELO</div>
              <div class="w-full h-2 bg-gray-200 border border-black mt-2">
                <div
                  class="h-full transition-all"
                  :class="getLevelBgClass(viewedProfile.faceit_data.lvl)"
                  :style="{
                    width: Math.min((viewedProfile.faceit_data.elo / 4500) * 100, 100) + '%',
                  }"
                />
              </div>
            </div>
          </div>

          <!-- Статы в сайдбаре -->
          <div class="space-y-2 mb-6 text-left">
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">K/D</span>
              <span
                class="font-mono font-bold"
                :class="getKDColorClass(viewedProfile.faceit_data.k_d_ratio)"
              >
                {{ formatStat(viewedProfile.faceit_data.k_d_ratio) }}
              </span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">Винрейт</span>
              <span
                class="font-mono font-bold"
                :class="getWinRateColorClass(viewedProfile.faceit_data.win_rate_percentage)"
              >
                {{ formatStat(viewedProfile.faceit_data.win_rate_percentage, '%') }}
              </span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">Матчи</span>
              <span
                class="font-mono font-bold"
                :class="getMatchesColorClass(viewedProfile.faceit_data.matches)"
              >
                {{ formatStat(viewedProfile.faceit_data.matches) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="w-full md:w-2/3 space-y-12">
        <!-- About -->
        <section>
          <div class="flex justify-between items-center mb-6 border-b-2 border-black pb-2">
            <h3 class="font-black text-xl uppercase">Обо мне</h3>
            <button
              v-if="isOwnProfile && !isEditing"
              @click="startEditing"
              class="font-bold uppercase text-blue-600 hover:text-blue-800 cursor-pointer"
            >
              <img src="/img/pencil-square.svg" width="18" height="18" />
            </button>
          </div>

          <div v-if="isOwnProfile && isEditing">
            <textarea
              v-model="editableDescription"
              rows="5"
              class="w-full p-3 border-2 border-black focus:outline-none focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-shadow resize-none"
              placeholder="Расскажи о себе..."
            />
            <div class="flex justify-end gap-3 mt-4">
              <button
                @click="cancelEditing"
                class="px-2 py-2 text-sm uppercase border-2 border-black bg-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                Отмена
              </button>
              <button
                @click="saveProfile"
                :disabled="userStore.isSaving"
                class="px-2 py-2 text-sm uppercase border-2 border-black bg-black !text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ userStore.isSaving ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>
          </div>

          <div v-else>
            <p v-if="viewedProfile.profile.description" class="text-gray-700 whitespace-pre-wrap">
              {{ viewedProfile.profile.description }}
            </p>
            <p v-else class="text-gray-400 italic">Тайна за семью смоками</p>
          </div>
        </section>

        <!-- Roles -->
        <section>
          <div class="flex justify-between items-center mb-6 border-b-2 border-black pb-2">
            <h3 class="font-black text-xl uppercase">Роли</h3>
            <button
              v-if="isOwnProfile && !isEditingRoles"
              @click="startEditingRoles"
              class="text-sm font-bold uppercase text-blue-600 hover:text-blue-800"
            >
              <img src="/img/pencil-square.svg" width="18" height="18" />
            </button>
          </div>

          <div v-if="isOwnProfile && isEditingRoles">
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <label
                v-for="role in allRoles"
                :key="role.id"
                class="flex items-center gap-2 p-3 border-2 cursor-pointer transition-all justify-center"
                :class="
                  selectedRoleIds.includes(role.id)
                    ? 'border-black bg-black text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                    : 'border-gray-200 hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] hover:border-black'
                "
              >
                <input type="checkbox" :value="role.id" v-model="selectedRoleIds" class="sr-only" />
                <span class="font-bold uppercase text-xs">{{ role.name }}</span>
              </label>
            </div>
            <div class="flex justify-end gap-3 mt-6">
              <button
                @click="cancelEditingRoles"
                class="px-2 py-2 text-sm uppercase border-2 border-black bg-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all"
              >
                Отмена
              </button>
              <button
                @click="saveRoles"
                :disabled="userStore.isSaving"
                class="px-2 py-2 text-sm uppercase border-2 border-black bg-black !text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ userStore.isSaving ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>
          </div>

          <div v-else>
            <div v-if="(viewedProfile.profile.roles || []).length > 0">
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="role in viewedProfile.profile.roles"
                  :key="role.id"
                  class="bg-black text-white font-mono text-sm uppercase px-2 py-1"
                >
                  {{ role.name }}
                </span>
              </div>
            </div>
            <p v-else class="text-gray-400 italic">Капитан, стрелец и на AWP игрец</p>
          </div>
        </section>

        <!-- Stats -->
        <section>
          <h3 class="font-black text-xl uppercase mb-6">Основная статистика</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              class="border border-black p-4 bg-green-50 flex items-center justify-between hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all"
            >
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">headshot %</div>
                <div
                  class="text-2xl font-black"
                  :class="
                    getHeadshotColorClass(viewedProfile.faceit_data.average_headshots_percentage)
                  "
                >
                  {{ formatStat(viewedProfile.faceit_data.average_headshots_percentage, '%') }}
                </div>
              </div>
              <img src="/img/bullseye.svg" width="24" height="24" />
            </div>

            <div
              class="border border-black p-4 bg-blue-50 flex items-center justify-between hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all"
            >
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">AVG damage</div>
                <div
                  class="text-2xl font-black"
                  :class="getADRColorClass(viewedProfile.faceit_data.avg_damage_per_round)"
                >
                  {{ formatStat(viewedProfile.faceit_data.avg_damage_per_round) }}
                </div>
              </div>
              <img src="/img/shield_check.svg" width="24" height="24" />
            </div>

            <div
              class="border border-black p-4 bg-amber-50 flex items-center justify-between hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all"
            >
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">K/R ratio</div>
                <div
                  class="text-2xl font-black"
                  :class="getKRColorClass(viewedProfile.faceit_data.k_r_ratio)"
                >
                  {{ formatStat(viewedProfile.faceit_data.k_r_ratio) }}
                </div>
              </div>
              <img src="/img/crosshair.svg" width="24" height="24" />
            </div>

            <div
              class="border border-black p-4 bg-purple-50 flex items-center justify-between hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[1px] hover:-translate-y-[1px] transition-all"
            >
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">win streak</div>
                <div
                  class="text-2xl font-black"
                  :class="getWinStreakColorClass(viewedProfile.faceit_data.longest_win_streak)"
                >
                  {{ formatStat(viewedProfile.faceit_data.longest_win_streak) }}
                </div>
              </div>
              <img src="/img/trophy.svg" width="24" height="24" />
            </div>
          </div>
        </section>

        <!-- Reviews -->
        <section>
          <div class="flex justify-between items-center mb-6 border-b-2 border-black pb-2">
            <h3 class="font-black text-l uppercase">Отзывы</h3>
            <span class="bg-black text-white px-2 py-0.5 text-sm">
              {{ viewedProfile.total_reviews }}
            </span>
          </div>

          <div v-if="!isOwnProfile" class="border-2 border-dashed border-gray-300 p-4 mb-8">
            <h4 class="uppercase mb-3">Оставить отзыв</h4>
            <textarea
              v-model="newReviewContent"
              rows="3"
              class="w-full p-3 border-2 border-black focus:outline-none focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-shadow resize-none text-sm placeholder:text-sm placeholder:text-gray-400"
              placeholder="Напиши отзыв..."
            />
            <div class="flex justify-between items-center mt-3">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold">Оценка:</span>
                <div class="flex gap-1" @mouseleave="hoverRating = 0">
                  <img
                    v-for="star in 5"
                    :key="star"
                    @click="newReviewRating = star"
                    @mouseover="hoverRating = star"
                    :src="
                      star <= (hoverRating || newReviewRating)
                        ? '/img/star-fill.svg'
                        : '/img/star.svg'
                    "
                    class="cursor-pointer transition-transform duration-150 hover:scale-125"
                    width="20"
                    height="20"
                  />
                </div>
              </div>
              <button
                @click="submitReview"
                :disabled="isSubmittingReview"
                class="px-2 py-2 text-sm uppercase border-2 border-black bg-black !text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isSubmittingReview ? 'Отправка...' : 'Отправить' }}
              </button>
            </div>
          </div>

          <div v-if="reviewsLoading" class="flex justify-center py-10">
            <Spinner size="sm" text="Загрузка отзывов..." />
          </div>
          <div v-else-if="reviews.length > 0">
            <Review v-for="review in reviews" :key="review.id" :review="review" />
          </div>
          <div v-else class="text-center text-gray-500 italic">
            {{ isOwnProfile ? 'Пока нет отзывов' : 'Расскажи первым, как он слил тебе игру' }}
          </div>

          <div v-if="isReviewsLoadingMore" class="flex justify-center py-4">
            <Spinner size="sm" />
          </div>
          <div
            v-if="!reviewsLoading && hasMoreReviews"
            ref="reviewsObserverTarget"
            style="height: 50px"
          />
        </section>
      </div>
    </div>
  </main>
</template>

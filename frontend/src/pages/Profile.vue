<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Header from '@/components/Header.vue'
import RatingStars from '@/components/RatingStars.vue'
import Review from '@/components/Review.vue'
import Spinner from '@/components/Spinner.vue'
import api from '@/api'

const route = useRoute()
const userStore = useUserStore()

// Profile state
const viewedProfile = ref(null)
const isLoadingProfile = ref(true)

// Reviews state
const REVIEWS_PAGE_SIZE = 10
const reviews = ref([])
const reviewsCurrentPage = ref(0)
const reviewsLoading = ref(true)
const isReviewsLoadingMore = ref(false)
const hasMoreReviews = ref(true)

// Observer
const reviewsObserverTarget = ref(null)
let observer = null

// Editing state
const isEditing = ref(false)
const editableDescription = ref('')
const newReviewContent = ref('')
const newReviewRating = ref(0)
const isSubmittingReview = ref(false)
const hoverRating = ref(0)

// Roles state
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
        <div class="border-2 border-black p-6 text-center sticky top-24">
          <div
            class="w-32 h-32 border-2 border-black bg-gray-200 mx-auto mb-6 flex items-center justify-center overflow-hidden"
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
          </div>

          <h1 class="text-3xl font-black uppercase tracking-tighter mb-1">
            {{ viewedProfile.faceit_data.nickname }}
          </h1>

          <div class="mb-4 flex justify-center">
            <RatingStars :rating="viewedProfile.rating" />
          </div>

          <div class="grid grid-cols-2 gap-4 border-t-2 border-black pt-6 mb-6">
            <div class="text-center">
              <div class="text-3xl font-black leading-none">
                {{ viewedProfile.faceit_data.lvl }}
              </div>
              <div class="text-[10px] uppercase font-bold text-gray-500">Уровень Faceit</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-black leading-none">
                {{ viewedProfile.faceit_data.elo }}
              </div>
              <div class="text-[10px] uppercase font-bold text-gray-500">Очки ELO</div>
            </div>
          </div>

          <div class="space-y-2 mb-6 text-left">
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">Соотношение K/D</span>
              <span class="font-mono font-bold text-green-600">
                {{ viewedProfile.faceit_data.k_d_ratio }}
              </span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">Процент побед</span>
              <span class="font-mono font-bold">
                {{ viewedProfile.faceit_data.win_rate_percentage }}%
              </span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="font-bold text-gray-500">Матчи</span>
              <span class="font-mono font-bold">{{ viewedProfile.faceit_data.matches }}</span>
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
              class="w-full p-2 border-2 border-black focus:outline-none"
            />
            <div class="flex justify-end gap-4 mt-4">
              <button
                @click="cancelEditing"
                class="px-4 py-2 text-sm font-bold uppercase border-2 border-gray-400"
              >
                Отмена
              </button>
              <button
                @click="saveProfile"
                :disabled="userStore.isSaving"
                class="px-4 py-2 text-sm font-bold uppercase bg-black !text-white"
              >
                {{ userStore.isSaving ? '...' : 'Сохранить' }}
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
                class="flex items-center gap-2 p-3 border-2 border-gray-200 cursor-pointer transition-all justify-center"
                :class="{
                  'border-black bg-black text-white shadow-md': selectedRoleIds.includes(role.id),
                }"
              >
                <input type="checkbox" :value="role.id" v-model="selectedRoleIds" class="sr-only" />
                <span class="font-bold uppercase text-sm">{{ role.name }}</span>
              </label>
            </div>
            <div class="flex justify-end gap-4 mt-6">
              <button
                @click="cancelEditingRoles"
                class="px-4 py-2 text-sm font-bold uppercase border-2 border-gray-400"
              >
                Отмена
              </button>
              <button
                @click="saveRoles"
                :disabled="userStore.isSaving"
                class="px-4 py-2 text-sm font-bold uppercase bg-black !text-white"
              >
                {{ userStore.isSaving ? '...' : 'Сохранить' }}
              </button>
            </div>
          </div>
          <div v-else>
            <div v-if="(viewedProfile.profile.roles || []).length > 0">
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="role in viewedProfile.profile.roles"
                  :key="role.id"
                  class="bg-black text-white font-mono text-xs uppercase px-2 py-1"
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
          <h3 class="font-black text-xl uppercase mb-6 flex items-center gap-2">
            Основная статистика
          </h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="border border-black p-4 bg-gray-50 flex items-center justify-between">
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">headshot %</div>
                <div class="text-2xl font-black">
                  {{ viewedProfile.faceit_data.average_headshots_percentage }}%
                </div>
              </div>
              <img src="/img/bullseye.svg" width="24" height="24" />
            </div>
            <div class="border border-black p-4 bg-gray-50 flex items-center justify-between">
              <div>
                <div class="text-xs uppercase font-bold text-gray-500">AVG damage</div>
                <div class="text-2xl font-black">
                  {{ viewedProfile.faceit_data.avg_damage_per_round }}
                </div>
              </div>
              <img src="/img/shield_check.svg" width="24" height="24" />
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
            <h4 class="font-bold uppercase mb-3">Оставить отзыв</h4>
            <textarea
              v-model="newReviewContent"
              rows="3"
              class="w-full p-2 border-2 border-black"
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
                class="px-4 py-2 text-sm font-bold uppercase bg-black !text-white"
              >
                {{ isSubmittingReview ? '...' : 'Отправить' }}
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
            Расскажи первым, как он слил тебе игру
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

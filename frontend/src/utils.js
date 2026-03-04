/**
 * Декодирует JWT токен, хранящийся в localStorage, и проверяет, не истек ли его срок.
 * @returns {boolean} Возвращает true, если токен просрочен или отсутствует, иначе false.
 */
export function isTokenExpired() {
  const token = localStorage.getItem('user_token')
  if (!token) {
    return true
  }
  try {
    const payloadBase64 = token.split('.')[1]
    const decodedJson = atob(payloadBase64)
    const decoded = JSON.parse(decodedJson)
    const exp = decoded.exp
    const now = Date.now() / 1000
    return exp < now
  } catch (error) {
    console.error('Ошибка декодирования токена:', error)
    return true
  }
}

/**
 * Возвращает CSS-класс цвета текста в зависимости от уровня Faceit.
 */
export function getLevelColorClass(level) {
  if (!level) return ''
  if (level >= 10) return 'text-red-500'
  if (level >= 8) return 'text-orange-500'
  if (level >= 5) return 'text-yellow-500'
  return 'text-green-500'
}

/**
 * Возвращает CSS-класс цвета текста в зависимости от рейтинга.
 */
export function getRatingColorClass(rating) {
  if (rating >= 4.0) return 'text-green-500'
  if (rating >= 2.5) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Форматирует значение статистики: если 0, null или undefined — возвращает прочерк.
 */
export function formatStat(value, suffix = '') {
  if (value === null || value === undefined || value === 0 || value === '0') {
    return '—'
  }
  return `${value}${suffix}`
}

/**
 * Цвет для K/D Ratio.
 */
export function getKDColorClass(value) {
  if (!value) return ''
  if (value > 1.1) return 'text-green-600'
  if (value >= 1.0) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для K/R Ratio.
 * < 0.6 красный, 0.6–0.8 жёлтый, > 0.8 зелёный
 */
export function getKRColorClass(value) {
  if (!value) return ''
  if (value > 0.8) return 'text-green-600'
  if (value >= 0.6) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для Win Rate %.
 */
export function getWinRateColorClass(value) {
  if (!value) return ''
  if (value > 55) return 'text-green-600'
  if (value >= 45) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для Headshot %.
 */
export function getHeadshotColorClass(value) {
  if (!value) return ''
  if (value > 55) return 'text-green-600'
  if (value >= 40) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для AVG Damage per Round.
 */
export function getADRColorClass(value) {
  if (!value) return ''
  if (value > 80) return 'text-green-600'
  if (value >= 60) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для количества матчей.
 */
export function getMatchesColorClass(value) {
  if (!value) return ''
  if (value > 500) return 'text-green-600'
  if (value >= 100) return 'text-yellow-500'
  return 'text-red-500'
}

/**
 * Цвет для Win Streak.
 * < 3 красный, 3–7 жёлтый, > 7 зелёный
 */
export function getWinStreakColorClass(value) {
  if (!value) return ''
  if (value > 7) return 'text-green-600'
  if (value >= 3) return 'text-yellow-500'
  return 'text-red-500'
}

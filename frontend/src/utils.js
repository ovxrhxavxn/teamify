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

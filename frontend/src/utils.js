/**
 * Декодирует JWT токен, хранящийся в localStorage, и проверяет, не истек ли его срок.
 * @returns {boolean} Возвращает true, если токен просрочен или отсутствует, иначе false.
 */
export function isTokenExpired() {
  const token = localStorage.getItem('user_token')

  // Если токена нет, считаем его "просроченным"
  if (!token) {
    return true
  }

  try {
    // Декодируем payload токена. Он находится между двумя точками в строке токена.
    // atob() декодирует строку из формата Base64.
    const payloadBase64 = token.split('.')[1]
    const decodedJson = atob(payloadBase64)
    const decoded = JSON.parse(decodedJson)

    // 'exp' — это стандартное поле в JWT, которое хранит время истечения срока (в секундах).
    const exp = decoded.exp

    // Получаем текущее время (также в секундах).
    const now = Date.now() / 1000

    // Если время 'exp' меньше текущего, токен просрочен.
    return exp < now
  } catch (error) {
    // Если при декодировании произошла ошибка (например, токен некорректный),
    // считаем его невалидным.
    console.error('Ошибка декодирования токена:', error)
    return true
  }
}

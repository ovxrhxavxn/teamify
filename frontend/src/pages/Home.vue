<script setup>
function generateRandomString(length) {
  let text = ''
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length))
  }
  return text
}
// 2. Хеширует verifier с помощью SHA-256 и кодирует в Base64URL (code_challenge)
async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await window.crypto.subtle.digest('SHA-256', data)
  return window
    .btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '')
}

async function loginWithFaceit() {
  const verifier = generateRandomString(128)
  const challenge = await generateCodeChallenge(verifier)
  // Сохраняем verifier, он понадобится после редиректа
  localStorage.setItem('pkce_code_verifier', verifier)

  const clientId = import.meta.env.VITE_FACEIT_CLIENT_ID
  const redirectUri = 'https://teamify.pro/auth/callback'

  const authUrl =
    `https://accounts.faceit.com/login?` +
    `client_id=${clientId}&` +
    `response_type=code&` +
    `redirect_uri=${redirectUri}&` +
    `scope=openid profile&` + // Добавьте нужные scope
    `redirect_popup=true&` +
    `code_challenge=${challenge}&` + // <-- ОБЯЗАТЕЛЬНО
    `code_challenge_method=S256` // <-- ОБЯЗАТЕЛЬНО

  // Перенаправляем пользователя
  window.location.href = authUrl
}
</script>

<template>
  <header
    class="h-20 border-b-2 border-black bg-white flex items-center justify-between px-6 lg:px-12 sticky top-0 z-500"
  >
    <a class="flex items-center gap-3 group">
      <div class="relative w-10 h-10">
        <img src="/img/logo.png" />
      </div>

      <span class="text-2xl font-black uppercase tracking-tighter">Teamify</span>
    </a>
  </header>

  <main class="flex flex-col lg:flex-row min-h-[calc(100vh-80px)]">
    <div
      class="flex-1 p-12 lg:p-20 flex flex-col justify-center border-r-0 lg:border-r-2 border-black relative overflow-hidden"
    >
      <div
        class="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none"
      ></div>

      <div class="relative z-10">
        <div
          class="inline-block bg-black text-white px-3 py-1 text-xs font-bold uppercase mb-6 tracking-widest"
        >
          Counter-Strike 2 Only
        </div>
        <h1 class="text-6xl lg:text-9xl font-black uppercase tracking-tighter leading-[0.85] mb-8">
          Найди свой Дрим Тим
        </h1>
        <p
          class="text-l font-medium text-gray-600 mb-12 max-w-lg leading-relaxed border-l-4 border-black pl-6"
        >
          Платформа для тех, кто хочет побеждать. Фильтр по ролям, ELO и адекватности. Никакого
          шума.
        </p>

        <!-- ИСПРАВЛЕННЫЙ И ПЕРЕМЕЩЕННЫЙ БЛОК ПРЕИМУЩЕСТВ -->
        <div class="flex flex-wrap gap-8 mt-16">
          <!-- Преимущество 1 -->
          <div class="flex items-center gap-3">
            <img src="/img/shield_check.svg" height="25" width="25" />
            <div>
              <div class="font-black text-lg">Достоверность</div>
              <div class="text-xs text-gray-500 uppercase">Подтверждение навыков</div>
            </div>
          </div>
          <!-- Преимущество 2 (теперь находится на том же уровне, что и первое) -->
          <div class="flex items-center gap-3">
            <img src="/img/people.svg" height="25" width="25" />
            <div>
              <div class="font-black text-lg">Сообщество</div>
              <div class="text-xs text-gray-500 uppercase">Общий вклад</div>
            </div>
          </div>
        </div>
        <!-- КОНЕЦ БЛОКА ПРЕИМУЩЕСТВ -->
      </div>
    </div>

    <div class="w-full lg:w-[500px] bg-gray-50 p-12 flex flex-col justify-center relative">
      <div class="absolute inset-0 opacity-[0.03]"></div>
      <div
        class="bg-white border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] relative z-20 flex flex-col p-10"
      >
        <div class="space-y-6 flex flex-col items-center">
          <div class="text-center">
            <h2 class="text-3xl font-black uppercase mb-2">Авторизация</h2>
            <p class="text-gray-500 text-sm">Подтверди свой скилл через Faceit</p>
          </div>
          <div class="flex-grow flex items-center justify-center">
            <button
              @click="loginWithFaceit"
              class="ant-btn css-mncuj7 ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-lg px-8 h-16 rounded-none bg-[#FF5500] hover:!bg-[#e04b00] border-2 border-black font-black uppercase text-lg flex items-center justify-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all"
            >
              <span class="text-white">Войти через FACEIT</span>
            </button>
          </div>
          <div class="text-center">
            <p class="text-xs font-mono text-gray-400">
              * Мы получаем только ваш Public ID, ELO и Nickname.
            </p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

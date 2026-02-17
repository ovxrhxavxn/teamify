<script setup></script>

<template>
  <header
    class="h-20 border-b-2 border-black bg-white flex items-center justify-between px-6 lg:px-12 sticky top-0 z-50"
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
      <div class="absolute top-10 left-10 opacity-5 pointer-events-none"></div>
      <div class="relative z-10">
        <div class="flex flex-wrap gap-8">
          <div class="flex items-center gap-3"></div>
          <div class="flex items-center gap-3"></div>
        </div>

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
      </div>
    </div>

    <div class="w-full lg:w-[500px] bg-gray-50 p-12 flex flex-col justify-center relative">
      <div class="absolute inset-0 opacity-[0.03]"></div>
      <div
        class="bg-white border-2 border-black p-10 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] relative z-20"
      >
        <div class="space-y-6">
          <div class="text-center mb-8">
            <h2 class="text-3xl font-black uppercase mb-2">Авторизация</h2>
            <p class="text-gray-500 text-sm">Подтверди свой скилл через Faceit</p>
          </div>
          <a
            class="ant-btn css-mncuj7 ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-lg ant-btn-block h-16 rounded-none bg-[#FF5500] hover:!bg-[#e04b00] border-2 border-black font-black uppercase text-lg flex items-center justify-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all"
          >
            <img class="" src="/img/faceit_logo.svg" />
            <span class="text-white">Войти через FACEIT</span>
          </a>
          <div class="text-center">
            <p class="text-xs font-mono text-gray-400 mt-4">
              * Мы получаем только ваш Public ID, ELO и Nickname.
            </p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

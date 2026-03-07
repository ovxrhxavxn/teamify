<div align="center">
  <img src="frontend/public/img/logo.png" alt="Teamify Logo" width="120" />

  # TEAMIFY

  **Найди свой дрим-тим на Faceit. Никакого шума.**

  [![Python](https://img.shields.io/badge/Python-3.14-black?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-black?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![Vue.js](https://img.shields.io/badge/Vue.js-3.5-black?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-asyncpg-black?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind-4.1-black?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

  <br />

  <img src="https://img.shields.io/badge/CS2-FACEIT-FF5500?style=for-the-badge&logoColor=white" />

</div>

---

## 🎯 О проекте

**Teamify** — веб-платформа для поиска тиммейтов в Counter-Strike 2 через Faceit. Авторизуйся через Faceit, попади в ленту LFG, найди напарника по ELO, ролям и рейтингу адекватности — и больше не играй с рандомами.

<div align="center">
  <table>
    <tr>
      <td align="center"><b>🛡️ Достоверность</b><br/>Все данные подтянуты с Faceit API</td>
      <td align="center"><b>⚡ Реалтайм</b><br/>WebSocket-уведомления об откликах</td>
      <td align="center"><b>⭐ Рейтинг</b><br/>Система отзывов и оценок игроков</td>
    </tr>
  </table>
</div>

---

## ✨ Возможности

- **🔐 OAuth2-авторизация** через Faceit с PKCE
- **📋 LFG-лента** — просматривай активных игроков в поиске тиммейта
- **🔔 Мгновенные уведомления** — WebSocket-отклики в реальном времени
- **🎭 Фильтрация** по ELO, рейтингу и игровым ролям (AWP, IGL, Support и др.)
- **👤 Профили игроков** с подробной CS2-статистикой из Faceit Data API
- **📝 Отзывы и рейтинг** — оценивай тиммейтов после игры
- **🔄 Auto-refresh токенов** — бесшовная сессия через httpOnly cookies
- **📱 Адаптивный дизайн** — neo-brutalism UI, работает на всех устройствах

---

## 🏗️ Архитектура

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────┐
│                  │  REST   │                  │         │              │
│   Vue.js 3 SPA  │◄───────►│  FastAPI Backend  │◄───────►│  PostgreSQL  │
│   + Pinia + WS   │   API   │  (async/await)   │  asyncpg│              │
│                  │         │                  │         │              │
└──────────────────┘         └────────┬─────────┘         └──────────────┘
                                      │
                                      │ HTTP
                                      ▼
                             ┌──────────────────┐
                             │   Faceit API      │
                             │  ┌──────────────┐ │
                             │  │ OAuth2       │ │
                             │  │ Data API     │ │
                             │  │ UserInfo     │ │
                             │  └──────────────┘ │
                             └──────────────────┘
```

---

## 🛠️ Технологический стек

### Backend
| Технология | Назначение |
|---|---|
| **FastAPI** | Async REST API + WebSocket |
| **SQLAlchemy 2.0** | Async ORM (asyncpg) |
| **PostgreSQL** | Основная БД |
| **python-jose** | JWT access/refresh токены |
| **cryptography (Fernet)** | Шифрование Faceit refresh-токенов |
| **aiohttp** | HTTP-клиент для Faceit API |
| **Pydantic v2** | Валидация и сериализация |

### Frontend
| Технология | Назначение |
|---|---|
| **Vue.js 3** | SPA с Composition API |
| **Pinia** | State management |
| **Vue Router** | Маршрутизация с auth guards |
| **Tailwind CSS 4** | Утилитарные стили (neo-brutalism) |
| **Ant Design Vue** | UI-компоненты |
| **Axios** | HTTP-клиент с auto-refresh |
| **WebSocket** | Реалтайм уведомления |

---

## 📁 Структура проекта

```
teamify/
├── backend/
│   └── src/
│       ├── auth/            # JWT, refresh tokens, security
│       ├── database/        # SQLAlchemy setup, base repository
│       ├── encryption/      # Fernet encryption service
│       ├── faceit/          # OAuth2, Data API, player stats
│       ├── lfg_responses/   # Отклики на игроков (+ WS уведомления)
│       ├── lfg_statuses/    # LFG-статусы, лента, фильтры
│       ├── profiles/        # Профили, роли, описания
│       ├── reviews/         # Отзывы и рейтинг
│       ├── users/           # Пользователи
│       ├── websockets/      # Connection manager
│       └── app.py           # FastAPI application
│
├── frontend/
│   └── src/
│       ├── components/      # Header, LFGCard, Review, RatingStars...
│       ├── pages/           # Home, Profile, LFGLobby, AuthCallback
│       ├── stores/          # Pinia: user, lfg
│       ├── router/          # Vue Router с auth guard
│       ├── api.js           # Axios с auto-refresh interceptor
│       └── utils.js         # Хелперы (цвета, форматирование)
│
└── README.md
```

---

## 🚀 Быстрый старт

### Предварительные требования

- **Python** 3.14+
- **Node.js** 20.19+ / 22.12+
- **PostgreSQL** 15+
- **Faceit Developer Account** ([developers.faceit.com](https://developers.faceit.com))

### 1. Клонирование

```bash
git clone https://github.com/your-username/teamify.git
cd teamify
```

### 2. Backend

```bash
cd backend

# Создаём виртуальное окружение
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Устанавливаем зависимости
uv sync

# Создаём .env файл
cp .env.example .env
```

Заполни `.env`:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=teamify
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES=30
REFRESH_TOKEN_EXPIRES=30

# Encryption
FERNET_ENCRYPTION_KEY=your-fernet-key

# Faceit
FACEIT_CLIENT_ID=your-client-id
FACEIT_CLIENT_SECRET=your-client-secret
FACEIT_AUTH_ENDPOINT=https://accounts.faceit.com
FACEIT_TOKEN_ENDPOINT=https://api.faceit.com/auth/v1/oauth/token
FACEIT_USERINFO_ENDPOINT=https://api.faceit.com/auth/v1/resources/userinfo
FACEIT_SERVER_API_KEY=your-server-api-key
FACEIT_DATA_API_ENDPOINT=https://open.faceit.com/data/v4
FACEIT_CALLBACK_URI=https://your-domain.com/auth/callback
```

```bash
# Запуск
python main.py
```

### 3. Frontend

```bash
cd frontend

# Устанавливаем зависимости
npm install

# Создаём .env файл
cp .env.example .env
```

Заполни `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_FACEIT_CLIENT_ID=your-client-id
VITE_REDIRECT_URI=http://localhost:5173/auth/callback
```

```bash
# Запуск dev-сервера
npm run dev
```

---

## 🔌 API Endpoints

### Auth
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/faceit/oauth2/callback` | Faceit OAuth2 callback |
| `POST` | `/auth/refresh` | Обновление access token |
| `POST` | `/auth/logout` | Выход |

### Profiles
| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/profiles/me` | Мой профиль |
| `GET` | `/profiles/{user_id}` | Профиль игрока |
| `PUT` | `/profiles/me` | Обновить описание/роли |
| `GET` | `/profiles/roles` | Список игровых ролей |

### LFG
| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/lfg/status` | Мой LFG-статус |
| `POST` | `/lfg/status` | Вкл/выкл поиск |
| `GET` | `/lfg/active` | Лента активных игроков |
| `WS` | `/lfg/ws` | WebSocket соединение |

### Responses
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/lfg/responses` | Откликнуться на игрока |

### Reviews
| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/reviews/{profile_id}` | Отзывы о профиле |
| `POST` | `/reviews/{profile_id}` | Оставить отзыв |

---

## 🎨 Дизайн

Проект выполнен в стиле **Neo-Brutalism** — жирные чёрные границы, яркие акценты, выраженные тени и минимум лишнего.

Акцентный цвет: `#FF5500` (Faceit Orange)

---

## 📄 Лицензия

Этот проект распространяется по лицензии MIT. Подробности в файле [LICENSE](LICENSE).

---

<div align="center">
  <sub>Сделано с 🔥 для CS2 комьюнити</sub>
  <br />
  <sub>Teamify © 2026</sub>
</div>

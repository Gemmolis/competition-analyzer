# 🔍 Мониторинг конкурентов — AI Ассистент

Мультимодальное AI-приложение для анализа конкурентов в нише **разработки сайтов и Telegram-ботов**. Работает **без VPN**, использует **GigaChat** (Сбер) для текста и **GPT-4o через ProxyAPI** для изображений.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![GigaChat](https://img.shields.io/badge/GigaChat-2--Pro-red)
![GPT-4o](https://img.shields.io/badge/GPT--4o-ProxyAPI-purple)
![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-yellow)

## 📋 О проекте

Приложение автоматизирует конкурентный анализ: собирает данные с сайтов конкурентов через Selenium, анализирует PDF-прайсы и отзывы, оценивает скриншоты лендингов и выдаёт структурированные JSON-отчёты с рекомендациями.

### 🎯 Кого анализируем

В качестве примера выбрана ниша **веб-разработки и Telegram-ботов**. Проанализированы исполнители с платформы FL.ru:

- **Артём** (artem) — веб-разработка на WordPress/WooCommerce
- **Стас** (stas) — разработка сайтов
- **Василий** (vasil) — веб-разработка
- **Борисова Елена** (borisova) — разработка сайтов

## ✨ Возможности

| Функция                   | Описание                                        | AI-сервис         |
| ------------------------- | ----------------------------------------------- | ----------------- |
| 📝 **Анализ текста**      | Сильные/слабые стороны, УТП, рекомендации       | GigaChat-2-Pro    |
| 🖼️ **Анализ изображений** | Описание, маркетинговые инсайты, оценка стиля   | GPT-4o (ProxyAPI) |
| 📄 **Анализ PDF**         | Извлечение текста из прайсов и отзывов + анализ | GigaChat-2-Pro    |
| 🌐 **Парсинг сайтов**     | Selenium + Chrome, извлечение title/H1/абзаца   | GigaChat-2-Pro    |
| 📋 **История запросов**   | Последние 10 запросов в JSON                    | —                 |

## 🏗️ Архитектура

┌─────────────────────────────────────────────────────────┐
│ Frontend (Web UI) + Desktop (PyQt6) │
└─────────────────────┬───────────────────────────────────┘
│ HTTP
┌─────────────────────▼───────────────────────────────────┐
│ Backend (FastAPI) │
├─────────────────────────────────────────────────────────┤
│ /analyze_text → GigaChat-2-Pro │
│ /analyze_image → GPT-4o (ProxyAPI) │
│ /analyze_pdf → pdfplumber + GigaChat │
│ /parse_demo → Selenium + GigaChat │
│ /history → JSON-файл │
└─────────────────────────────────────────────────────────┘

## 📁 Структура проекта

competition-analyzer/
├── backend/
│ ├── main.py # FastAPI-приложение
│ ├── config.py # Настройки + логирование
│ ├── models/schemas.py # Pydantic-модели
│ └── services/
│ ├── gigachat_service.py # GigaChat (текст, PDF)
│ ├── vision_service.py # GPT-4o Vision (картинки)
│ ├── parser_service.py # Selenium-парсер
│ └── history_service.py # История
├── frontend/ # Веб-интерфейс
│ ├── index.html
│ ├── styles.css
│ └── app.js
├── desktop/ # PyQt6-приложение
│ ├── main.py
│ ├── api_client.py
│ ├── styles.py
│ └── build.py # Сборка .exe
├── data/ # Данные конкурентов
│ ├── artem/
│ ├── stas/
│ ├── vasil/
│ └── borisova/
├── .env.example # Шаблон переменных
├── requirements.txt
└── README.md

## 🚀 Установка и запуск

### 1. Клонирование

```bash
git clone https://github.com/ВАШ_ЛОГИН/competition-analyzer.git
cd competition-analyzer
```

### 2. Виртуальное окружение

```bash
python -m venv venv
```

# Windows:

venv\Scripts\activate

# Linux/Mac:

source venv/bin/activate

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка .env

Создайте файл .env в корне проекта:

# GigaChat (текст и PDF)

GIGACHAT*CREDENTIALS=ваш*ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat-2-Pro

# ProxyAPI (изображения через GPT-4o)

PROXY*API_KEY=ваш*ключ
PROXY_API_BASE_URL=https://api.proxyapi.ru/openai/v1
Где получить ключи:

GigaChat: https://developers.sber.ru/portal/products/gigachat-api

ProxyAPI: https://proxyapi.ru/

### 5. Запуск backend

```bash
python run.py
```

Веб-интерфейс: http://localhost:8000
Swagger-документация: http://localhost:8000/docs

### 6. Запуск desktop-приложения (опционально)

```bash
cd desktop
pip install -r requirements.txt
python main.py
```

Готовый файл: desktop/dist/CompetitorMonitor.exe

### 📡 API-эндпоинты

| **Метод** | **Эндпоинт**     | **Описание**                 |
| :-------- | :--------------- | :--------------------------- |
| POST      | `/analyze_text`  | Анализ текста конкурента     |
| POST      | `/analyze_image` | Анализ изображения           |
| POST      | `/analyze_pdf`   | Анализ PDF-файла             |
| POST      | `/parse_demo`    | Парсинг сайта через Selenium |
| GET       | `/history`       | Получить историю             |
| DELETE    | `/history`       | Очистить историю             |
| GET       | `/health`        | Проверка работоспособности   |

### 🔬 Технические особенности и найденные ограничения

✅ Что работает отлично
GigaChat-2-Pro — превосходно справляется с анализом текста, PDF и извлечённого контента с сайтов. Стабильные и осмысленные ответы.

GPT-4o через ProxyAPI — эталонное качество анализа изображений: точное описание, корректное чтение текста, адекватная оценка UX/UI.

Selenium + Chrome (headless) — надёжный сбор данных с динамических сайтов.

⚠️ Найденные ограничения GigaChat Vision
В ходе работы было протестировано использование GigaChat-2-Pro в качестве vision-модели. Обнаружены критические ограничения:

| **Размер изображения**      | **Результат анализа**              |
| :-------------------------- | :--------------------------------- |
| < 200 KB, до 1024 px        | ✅ Корректно                       |
| 200 KB – 1 MB               | ⚠️ Средне, возможны домыслы        |
| > 1 MB, full-page скриншоты | ❌ Галлюцинации, выдуманные детали |

Пример галлюцинации: при анализе full-page скриншота сайта студии вокала «Вокальный Глеб» GigaChat определил его как «сайт, посвящённый дизайну интерьеров», неверно прочитав содержимое. Оценка визуального стиля также оказалась нестабильной (0/10 для профессионального сайта).

Решение: для анализа изображений используется GPT-4o через ProxyAPI — гибридная схема, где каждая модель решает свою задачу.

### 💡 Рекомендации по промптам для vision-моделей

- Явно требовать: «описывай только то, что реально видно».
- Запрещать выдумывать текст, если он размыт.
- Просить возвращать список реально читаемого текста.
- Уменьшать `temperature` до 0.1–0.3 для снижения креативности.
- Сжимать изображения перед отправкой (JPEG, quality 85–90, до 1024–1536 px).

## 🛠️ Технологический стек

**Backend:**

- Python 3.11, FastAPI, Uvicorn
- Pydantic (валидация), python-dotenv
- pdfplumber (извлечение текста из PDF)
- Pillow (обработка изображений)
- Selenium + webdriver-manager (парсинг)
- BeautifulSoup4 + lxml (HTML)

**AI:**

- GigaChat SDK (Сбер) — текст и PDF
- OpenAI SDK через ProxyAPI — GPT-4o для изображений

**Frontend:**

- Vanilla JS, CSS3, HTML5

**Desktop:**

- PyQt6, PyInstaller

## 🎓 Что было изучено

- Проектирование мультимодального приложения end-to-end
- Интеграция двух AI-провайдеров (GigaChat + OpenAI через ProxyAPI) в одном продукте
- Работа с PDF, изображениями, текстом и веб-страницами в едином пайплайне
- Создание FastAPI-бэкенда с логированием
- Разработка веб-интерфейса и desktop-приложения на PyQt6
- Сборка standalone `.exe` через PyInstaller
- Работа без VPN с отечественными AI-сервисами

## 👤 Автор

Учебный проект в рамках курса «Промпт-инжиниринг 3.0», Модуль 4.

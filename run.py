"""
Скрипт запуска приложения Мониторинг конкурентов
"""
import uvicorn
import logging
from backend.config import settings

# Настраиваем уровень логирования
logging.getLogger("competitor_monitor").setLevel(logging.INFO)

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🚀 МОНИТОРИНГ КОНКУРЕНТОВ - AI Ассистент (GigaChat)")
    print("=" * 60)
    print()
    print(f"📍 Веб-интерфейс:  http://localhost:{settings.api_port}")
    print(f"📚 Документация:   http://localhost:{settings.api_port}/docs")
    print(f"📖 ReDoc:          http://localhost:{settings.api_port}/redoc")
    print()
    print(f"🤖 Модель GigaChat: {settings.gigachat_model}")
    print(f"🔑 API ключ:        {'✓ Настроен' if settings.gigachat_credentials else '✗ НЕ ЗАДАН!'}")
    print()
    print("-" * 60)
    print("Логи запросов будут отображаться ниже...")
    print("-" * 60)
    print()
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
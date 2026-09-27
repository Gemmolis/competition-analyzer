"""
Сервис для работы с GigaChat API
"""
import logging
import json
import re
from gigachat import GigaChat
import io
import os
from PIL import Image

from backend.config import settings

logger = logging.getLogger("competitor_monitor.gigachat")

class GigaChatService:
    def __init__(self):
        logger.info("Инициализация GigaChat сервиса...")
        self.client = GigaChat(
            credentials=settings.gigachat_credentials,
            scope=settings.gigachat_scope,
            model=settings.gigachat_model,
            verify_ssl_certs=False,
        )
        self.model = settings.gigachat_model
        logger.info(f"GigaChat сервис инициализирован. Модель: {self.model}")

    def _parse_json_response(self, content: str) -> dict:
        """Извлекает JSON из ответа модели"""
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Не удалось распарсить JSON из ответа GigaChat")
            return {}

    def analyze_text(self, text: str) -> dict:
        """Анализ текста конкурента"""
        logger.info("Анализ текста через GigaChat...")
        
        system_prompt = """Ты — эксперт по конкурентному анализу. Проанализируй текст конкурента и верни СТРОГО JSON:
        {
            "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
            "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
            "unique_offers": ["уникальное предложение 1", "уникальное предложение 2", "уникальное предложение 3"],
            "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
            "summary": "Краткое резюме"
        }
        Каждый массив должен содержать 3-5 пунктов. Пиши на русском языке."""

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Проанализируй текст:\n\n{text}"}
            ]
        }
        
        response = self.client.chat(payload)
        content = response.choices[0].message.content
        return self._parse_json_response(content)

    def analyze_image(self, image_path: str) -> dict:
        """Анализ изображения через GigaChat Vision (со сжатием)"""
        logger.info(f"Анализ изображения: {image_path}")
        
        # Сжимаем изображение перед загрузкой
        img = Image.open(image_path)
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
    
        original_size = os.path.getsize(image_path) / 1024
        compressed_size = len(buffer.getvalue()) / 1024
        logger.info(f"  Сжатие: {original_size:.0f} KB → {compressed_size:.0f} KB")
        
        buffer.name = "image.jpg"  # ← подсказка для GigaChat о формате файла
        uploaded_file = self.client.upload_file(buffer, purpose="general")
        file_id = uploaded_file.id_
        logger.info(f"  Файл загружен, ID: {file_id}")
        
        system_prompt = """Ты — аналитик визуального контента. Опиши ТОЛЬКО ТО, ЧТО РЕАЛЬНО ВИДИШЬ.

        КРИТИЧЕСКИЕ ПРАВИЛА:
        1. НЕ выдумывай элементы, которых нет на изображении.
        2. Если текст размыт или не читается — напиши "не читается".
        3. НЕ придумывай названия компаний, цифры, имена.
        4. Описывай конкретику: цвета, блоки, кнопки, изображения, читаемый текст.
        5. Избегай общих фраз типа "современный дизайн", "удобный интерфейс".

        Верни СТРОГО JSON:
        {
            "description": "Что реально видно: блоки, цвета, читаемый текст, элементы",
            "visible_text": ["только реально читаемый текст"],
            "marketing_insights": ["наблюдение на основе видимого"],
            "visual_style_analysis": "Оценка только по видимым элементам",
            "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"]
        }

        Пиши на русском. Будь честен: если что-то непонятно — пиши об этом прямо."""

        payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Опиши только то, что реально видно. Не выдумывай.",
                "attachments": [file_id]
            }
        ]
    }
    
        response = self.client.chat(payload)
        content = response.choices[0].message.content
        return self._parse_json_response(content)

# Глобальный экземпляр
gigachat_service = GigaChatService()
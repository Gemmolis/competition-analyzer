"""
Сервис анализа изображений через ProxyAPI (GPT-4o Vision)
Работает без VPN, оплата в рублях
"""
import base64
import io
import json
import re
import logging
from openai import OpenAI
from PIL import Image
from backend.config import settings

logger = logging.getLogger("competitor_monitor.vision")


class VisionService:
    """Анализ изображений через GPT-4o (ProxyAPI)"""

    def __init__(self):
        logger.info("Инициализация Vision сервиса (ProxyAPI)...")
        self.client = OpenAI(
            api_key=settings.proxy_api_key,
            base_url=settings.proxy_api_base_url
        )
        self.model = "gpt-4o"  # Лучшая модель для vision
        logger.info(f"Vision сервис готов. Модель: {self.model}")

    def _parse_json_response(self, content: str) -> dict:
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Не удалось распарсить JSON")
            return {}

    def analyze_image(self, image_path: str) -> dict:
        """Анализ изображения через GPT-4o Vision"""
        logger.info(f"Анализ изображения через GPT-4o: {image_path}")

        # Сжимаем до разумного размера (для GPT-4o можно больше, но экономим токены)
        img = Image.open(image_path)
        img.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="JPEG", quality=90)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        system_prompt = """Ты — эксперт по визуальному маркетингу и UX/UI дизайну.

Проанализируй изображение конкурента и верни СТРОГО JSON:
{
    "description": "Подробное описание: что за сайт/баннер, какая тема, какие блоки, цвета, читаемый текст, элементы",
    "visible_text": ["весь реально читаемый текст с картинки"],
    "marketing_insights": ["инсайт 1", "инсайт 2", "инсайт 3", "инсайт 4"],
    "visual_style_score": 7,
    "visual_style_analysis": "Детальный анализ: цветовая палитра, типографика, композиция, UX/UI",
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"]
}

Правила:
- visual_style_score от 0 до 10
- Описывай КОНКРЕТИКУ, не используй общие фразы
- Пиши на русском языке
- Если на картинке сайт — укажи его тематику (например, "студия вокала", "веб-студия")
- Читай весь видимый текст и включай его в visible_text"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проанализируй это изображение конкурента:"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=2500
        )

        content = response.choices[0].message.content
        return self._parse_json_response(content)


# Глобальный экземпляр
vision_service = VisionService()
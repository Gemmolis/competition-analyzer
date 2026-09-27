import os
import base64
import pdfplumber
from backend.services.gigachat_service import gigachat_service
import io
from PIL import Image

def prepare_image(file_path, max_size=(1024, 1024)):
    """Сжимает и изменяет размер изображения перед отправкой в GigaChat"""
    img = Image.open(file_path)
    # Сохраняем пропорции, уменьшаем до 1024px по большей стороне
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Конвертируем в RGB (убираем альфа-канал, если он есть) и сохраняем в буфер как JPEG
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=85)
    
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# Путь к вашей папке data
DATA_DIR = "data"

def analyze_pdf(file_path):
    print(f"\n📄 Анализ PDF: {file_path}")
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    if not text.strip():
        print("⚠️ PDF не содержит текста (возможно, это сканы). Нужен OCR.")
        return
        
    print(f"  Извлечено {len(text)} символов. Отправка в GigaChat...")
    result = gigachat_service.analyze_text(text)
    print("  Результат:")
    print(f"  - Сильные стороны: {result.get('strengths')}")
    print(f"  - Слабые стороны: {result.get('weaknesses')}")
    print(f"  - Резюме: {result.get('summary')}")

def analyze_image(file_path):
    print(f"\n🖼️ Анализ изображения: {file_path}")
    result = gigachat_service.analyze_image(file_path)
    print("  Результат:")
    print(f"  - Описание: {result.get('description')}")
    print(f"  - Оценка стиля: {result.get('visual_style_score')}/10")

if __name__ == "__main__":
    # Пройдемся по папкам конкурентов
    for competitor in os.listdir(DATA_DIR):
        competitor_path = os.path.join(DATA_DIR, competitor)
        if not os.path.isdir(competitor_path):
            continue
            
        print(f"\n{'='*40}")
        print(f"🏢 Конкурент: {competitor.upper()}")
        print(f"{'='*40}")
        
        for file in os.listdir(competitor_path):
            file_path = os.path.join(competitor_path, file)
            if file.endswith(".pdf"):
                analyze_pdf(file_path)
            elif file.endswith((".png", ".jpg", ".jpeg")):
                analyze_image(file_path)
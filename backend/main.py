"""
Главный модуль FastAPI приложения
Мониторинг конкурентов - MVP ассистент (на GigaChat)
"""
import base64
import time
import logging
import tempfile
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from backend.config import settings
from backend.models.schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    ImageAnalysisResponse,
    ParseDemoRequest,
    ParseDemoResponse,
    ParsedContent,
    HistoryResponse,
    CompetitorAnalysis
)
from backend.services.gigachat_service import gigachat_service
from backend.services.vision_service import vision_service
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service

# Логгер для API
logger = logging.getLogger("competitor_monitor.api")

# Инициализация приложения
logger.info("=" * 60)
logger.info("🚀 ЗАПУСК ПРИЛОЖЕНИЯ: Мониторинг конкурентов (GigaChat)")
logger.info("=" * 60)

app = FastAPI(
    title="Мониторинг конкурентов",
    description="MVP ассистент для анализа конкурентов на базе GigaChat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Middleware для логирования ===
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"➡️  {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed = time.time() - start_time
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(f"{status_emoji} {request.method} {request.url.path} -> {response.status_code} ({elapsed:.3f}s)")
    return response


# === События жизненного цикла ===
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🟢 СЕРВЕР ЗАПУЩЕН")
    logger.info(f"  Адрес: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"  Документация: http://localhost:{settings.api_port}/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🔴 ОСТАНОВКА СЕРВЕРА")
    await parser_service.close()


# === Эндпоинты ===

@app.get("/")
async def root():
    """Главная страница"""
    return FileResponse("frontend/index.html")


@app.post("/analyze_text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Анализ текста конкурента через GigaChat"""
    logger.info("=" * 50)
    logger.info("📝 API: АНАЛИЗ ТЕКСТА")
    logger.info(f"  Длина текста: {len(request.text)} символов")
    
    try:
        # GigaChat возвращает dict, оборачиваем в модель
        analysis_data = gigachat_service.analyze_text(request.text)
        analysis = CompetitorAnalysis(**analysis_data)
        
        history_service.add_entry(
            request_type="text",
            request_summary=request.text[:100] + "..." if len(request.text) > 100 else request.text,
            response_summary=analysis.summary
        )
        
        logger.info("  ✅ УСПЕХ")
        logger.info("=" * 50)
        return TextAnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        logger.error(f"  ❌ ОШИБКА: {e}")
        logger.error("=" * 50)
        return TextAnalysisResponse(success=False, error=str(e))


@app.post("/analyze_image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Анализ изображения конкурента через GigaChat Vision"""
    logger.info("=" * 50)
    logger.info("🖼️ API: АНАЛИЗ ИЗОБРАЖЕНИЯ")
    logger.info(f"  Файл: {file.filename}")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла")
    
    try:
        # Сохраняем во временный файл (GigaChat принимает путь к файлу)
        content = await file.read()
        logger.info(f"  Размер: {len(content) / 1024:.1f} KB")
        
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.info("  🔍 Отправка в GigaChat Vision...")
        analysis_data = vision_service.analyze_image(tmp_path)
        analysis = ImageAnalysisResponse  # placeholder
        from backend.models.schemas import ImageAnalysis
        analysis = ImageAnalysis(**analysis_data)
        
        os.unlink(tmp_path)
        
        history_service.add_entry(
            request_type="image",
            request_summary=f"Изображение: {file.filename}",
            response_summary=analysis.description[:200] if analysis.description else "Анализ изображения"
        )
        
        logger.info("  ✅ УСПЕХ")
        logger.info("=" * 50)
        return ImageAnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        logger.error(f"  ❌ ОШИБКА: {e}")
        logger.error("=" * 50)
        return ImageAnalysisResponse(success=False, error=str(e))


@app.post("/analyze_pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    """Анализ PDF-файла конкурента"""
    logger.info("=" * 50)
    logger.info("📄 API: АНАЛИЗ PDF")
    logger.info(f"  Файл: {file.filename}")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Только PDF файлы")
    
    try:
        import pdfplumber
        
        content = await file.read()
        logger.info(f"  Размер: {len(content) / 1024:.1f} KB")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Извлекаем текст из PDF
        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        os.unlink(tmp_path)
        
        if not text.strip():
            return {"success": False, "error": "PDF не содержит текста"}
        
        logger.info(f"  Извлечено {len(text)} символов. Отправка в GigaChat...")
        
        analysis_data = gigachat_service.analyze_text(text)
        analysis = CompetitorAnalysis(**analysis_data)
        
        history_service.add_entry(
            request_type="pdf",
            request_summary=f"PDF: {file.filename}",
            response_summary=analysis.summary[:200]
        )
        
        logger.info("  ✅ УСПЕХ")
        logger.info("=" * 50)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"  ❌ ОШИБКА: {e}")
        logger.error("=" * 50)
        return {"success": False, "error": str(e)}


@app.post("/parse_demo", response_model=ParseDemoResponse)
async def parse_demo(request: ParseDemoRequest):
    """Парсинг сайта через Selenium + анализ через GigaChat (текст)"""
    logger.info("=" * 50)
    logger.info("🌐 API: ПАРСИНГ САЙТА")
    logger.info(f"  URL: {request.url}")
    
    try:
        title, h1, first_paragraph, screenshot_bytes, error = await parser_service.parse_url(request.url)
        
        if error:
            return ParseDemoResponse(success=False, error=error)
        
        logger.info(f"  Title: {title[:50] if title else 'N/A'}")
        logger.info(f"  H1: {h1[:50] if h1 else 'N/A'}")
        
        # GigaChat анализирует текст (не картинку скриншота)
        context_parts = [f"URL: {request.url}"]
        if title:
            context_parts.append(f"Title: {title}")
        if h1:
            context_parts.append(f"H1: {h1}")
        if first_paragraph:
            context_parts.append(f"Текст: {first_paragraph}")
        
        combined_text = "\n".join(context_parts)
        
        analysis_data = gigachat_service.analyze_text(combined_text)
        analysis = CompetitorAnalysis(**analysis_data)
        
        parsed_content = ParsedContent(
            url=request.url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
            analysis=analysis
        )
        
        history_service.add_entry(
            request_type="parse",
            request_summary=f"URL: {request.url}",
            response_summary=analysis.summary[:100] if analysis.summary else f"Title: {title or 'N/A'}"
        )
        
        logger.info("  ✅ УСПЕХ")
        logger.info("=" * 50)
        return ParseDemoResponse(success=True, data=parsed_content)
    except Exception as e:
        logger.error(f"  ❌ ОШИБКА: {e}")
        logger.error("=" * 50)
        return ParseDemoResponse(success=False, error=str(e))


@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """Получить историю"""
    items = history_service.get_history()
    return HistoryResponse(items=items, total=len(items))


@app.delete("/history")
async def clear_history():
    """Очистить историю"""
    history_service.clear_history()
    return {"success": True, "message": "История очищена"}


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "healthy", "service": "Competitor Monitor", "version": "1.0.0"}


# Статические файлы
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
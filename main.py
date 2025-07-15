from fastapi import FastAPI, HTTPException
from pyrogram import Client
from pyrogram.types import Message
from pydantic import BaseModel
import base64
import os
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

MY_SESSION = os.getenv("MY_SESSION_STRING")
MY_CHANNEL_ID = int(os.getenv("MY_CHANNEL_ID", "-1001234567890"))  # Твой приватный канал

class FileRequest(BaseModel):
    file_id: str
    bot_token: str
    
class ForwardRequest(BaseModel):
    chat_id: int
    message_id: int
    bot_token: str

@app.get("/")
async def root():
    return {
        "message": "Telegram File API", 
        "status": "working",
        "endpoints": ["/api/get_file", "/api/forward_and_download"]
    }

@app.post("/api/forward_and_download")
async def forward_and_download(request: ForwardRequest):
    """Переслать сообщение и скачать файл"""
    
    logger.info(f"Пересылка сообщения {request.message_id} из чата {request.chat_id}")
    
    if not MY_SESSION:
        raise HTTPException(status_code=500, detail="Session не настроена")
    
    # Создаём бота для пересылки
    bot = Client(
        name="forward_bot",
        bot_token=request.bot_token,
        in_memory=True
    )
    
    # Создаём userbot для скачивания
    userbot = Client(
        name="my_userbot",
        session_string=MY_SESSION,
        in_memory=True
    )
    
    try:
        # Запускаем обоих
        await bot.start()
        await userbot.start()
        
        # Пересылаем сообщение в наш канал
        forwarded = await bot.forward_messages(
            chat_id=MY_CHANNEL_ID,
            from_chat_id=request.chat_id,
            message_ids=request.message_id
        )
        
        logger.info(f"Сообщение переслано: {forwarded.id}")
        
        # Ждём немного
        await asyncio.sleep(1)
        
        # Получаем сообщение через userbot
        message = await userbot.get_messages(MY_CHANNEL_ID, forwarded.id)
        
        if message.video:
            file_id = message.video.file_id
        elif message.document:
            file_id = message.document.file_id
        elif message.photo:
            file_id = message.photo.file_id
        else:
            raise HTTPException(status_code=400, detail="Нет медиа в сообщении")
        
        # Скачиваем файл
        file_bytes = await userbot.download_media(message, in_memory=True)
        
        # Удаляем переслаанное сообщение
        await userbot.delete_messages(MY_CHANNEL_ID, forwarded.id)
        
        await bot.stop()
        await userbot.stop()
        
        if file_bytes and file_bytes.getvalue():
            data = file_bytes.getvalue()
            logger.info(f"Файл скачан: {len(data)} байт")
            
            return {
                "status": "ok",
                "file_data": base64.b64encode(data).decode(),
                "file_size": len(data)
            }
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await bot.stop()
        await userbot.stop()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/get_file")
async def get_file(request: FileRequest):
    """Старый метод для обратной совместимости"""
    return {
        "status": "error",
        "message": "Используйте /api/forward_and_download",
        "file_data": "",
        "file_size": 0
    }
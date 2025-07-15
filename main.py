from fastapi import FastAPI, HTTPException
from pyrogram import Client
import os
import asyncio

app = FastAPI()

# Клиенты для каждого пользователя
clients = {}

@app.post("/api/get_file")
async def get_file(session_string: str, file_id: str):
    """Получить прямую ссылку на файл"""
    
    # Создаём клиента если его нет
    if session_string not in clients:
        clients[session_string] = Client(
            "session",
            session_string=session_string
        )
    
    client = clients[session_string]
    
    try:
        async with client:
            # Скачиваем файл
            file_path = await client.download_media(file_id)
            
            # Тут можно загрузить на ваш CDN или вернуть base64
            # Пока просто вернём путь
            return {"file_path": file_path, "status": "ok"}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Telegram File API"}
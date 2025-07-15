from fastapi import FastAPI, HTTPException
from pyrogram import Client
import os
import asyncio
import tempfile

app = FastAPI()

# Клиенты для каждого пользователя
clients = {}

@app.post("/api/create_session")
async def create_session(api_id: int, api_hash: str, phone_number: str):
    """Создать новую session строку"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        client = Client(
            "temp_session",
            api_id=api_id,
            api_hash=api_hash,
            workdir=temp_dir,
            phone_number=phone_number
        )
        
        try:
            await client.start()
            session_string = await client.export_session_string()
            await client.stop()
            
            return {
                "session_string": session_string,
                "status": "ok",
                "message": "Session создана успешно"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

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
            file_path = await client.download_media(file_id, in_memory=True)
            
            # Возвращаем файл как base64 или URL
            return {
                "status": "ok",
                "message": "Файл готов к скачиванию",
                "file_path": file_path
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Telegram File API", "status": "working"}
from fastapi import FastAPI, HTTPException
from pyrogram import Client
import base64
import os

app = FastAPI()

# Твоя постоянная session строка
MY_SESSION = os.getenv("MY_SESSION_STRING")  # Храним в переменных Railway

# Один клиент для всех запросов
my_client = Client(
    name="my_userbot",
    session_string=MY_SESSION,
    in_memory=True
)

@app.post("/api/get_file")
async def get_file(file_id: str, bot_token: str):
    """Получить файл любого размера"""
    try:
        async with my_client:
            # Скачиваем через твой userbot
            file_bytes = await my_client.download_media(
                file_id,
                in_memory=True
            )
            
            if file_bytes:
                file_base64 = base64.b64encode(file_bytes.getvalue()).decode()
                return {
                    "status": "ok",
                    "file_data": file_base64,
                    "file_size": len(file_bytes.getvalue())
                }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
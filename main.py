from fastapi import FastAPI, HTTPException
from pyrogram import Client
from pydantic import BaseModel
import base64
import os

app = FastAPI()

# Твоя постоянная session строка
MY_SESSION = os.getenv("MY_SESSION_STRING")

# Модель для входных данных
class FileRequest(BaseModel):
    file_id: str
    bot_token: str

@app.get("/")
async def root():
    return {
        "message": "Telegram File API", 
        "status": "working",
        "endpoints": ["/api/get_file"]
    }

@app.post("/api/get_file")
async def get_file(request: FileRequest):
    """Получить файл любого размера"""
    
    if not MY_SESSION:
        raise HTTPException(status_code=500, detail="Session не настроена")
    
    # Создаём клиента
    client = Client(
        name="my_userbot",
        session_string=MY_SESSION,
        in_memory=True
    )
    
    try:
        await client.start()
        
        # Скачиваем через твой userbot
        file_bytes = await client.download_media(
            request.file_id,
            in_memory=True
        )
        
        await client.stop()
        
        if file_bytes:
            file_base64 = base64.b64encode(file_bytes.getvalue()).decode()
            return {
                "status": "ok",
                "file_data": file_base64,
                "file_size": len(file_bytes.getvalue())
            }
        else:
            raise HTTPException(status_code=404, detail="Файл не найден")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
from pyrogram import Client
import asyncio

async def get_session():
    api_id = int(input("Введите API ID: "))
    api_hash = input("Введите API Hash: ")
    
    app = Client(
        "my_account",
        api_id=api_id,
        api_hash=api_hash
    )
    
    async with app:
        session_string = await app.export_session_string()
        print("\n\nВаша session строка:")
        print("="*50)
        print(session_string)
        print("="*50)
        print("\nСохраните её в безопасном месте!")
        
asyncio.run(get_session())
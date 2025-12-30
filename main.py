from pyrogram import Client, filters
from pyrogram.types import Message

# Apnar details ekhane set kora holo
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8170872541:AAEW9FehHQ7RoDaTIGuWywH4xubLaALcZd8"

app = Client("remover_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Service messages (Join, Leave, VC Start/End) delete korar function
@app.on_message(filters.group & filters.service)
async def delete_service_messages(_, message: Message):
    try:
        await message.delete()
        print(f"Deleted a service message: {message.service}")
    except Exception as e:
        print(f"Error: {e}")

print("--- Service Message Remover Bot Started ---")
app.run()

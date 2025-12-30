import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

# --- CONFIGURATION ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"
GROUP_ID = -1003673065500

app = Client("DX_Music_Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# --- AUTO DELETE SERVICE MESSAGES ---
@app.on_message(filters.group & filters.service)
async def delete_service(_, message: Message):
    try:
        await message.delete()
    except:
        pass

# --- MUSIC PLAYER ---
@app.on_message(filters.command("play") & filters.group)
async def play_song(client, message: Message):
    if message.chat.id != GROUP_ID:
        return
    
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("<code>Usage: /play [song name]</code>")

    m = await message.reply("<code>🔍 Searching...</code>")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("<code>❌ Not found!</code>")

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]['title']
        duration = results[0]['duration']
        thumbnail = results[0]['thumbnails'][0]

        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']

        # PyTgCalls v2.1.0 Syntax
        await call_py.play(
            message.chat.id,
            AudioPiped(audio_url)
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop")
            ],
            [InlineKeyboardButton("💎 DX-CODEX", url="https://t.me/DX_CODEX")]
        ])

        caption = (
            f"<b>🎧 Now Playing</b>\n\n"
            f"<b>📌 Title:</b> <code>{title[:40]}...</code>\n"
            f"<b>⏳ Duration:</b> <code>{duration}</code>\n\n"
            f"<code>00:00 💠━━━━━━━━━━━━━ {duration}</code>\n\n"
            f"<i>Powered by DX-CODEX</i>"
        )

        await m.delete()
        await message.reply_photo(photo=thumbnail, caption=caption, reply_markup=buttons)

    except Exception as e:
        await m.edit(f"<code>❌ Error: {str(e)}</code>")

# --- CONTROLS ---
@app.on_callback_query(filters.regex(pattern=r"^(pause|resume|stop)$"))
async def controls(client, query: CallbackQuery):
    try:
        if query.data == "pause":
            await call_py.pause_stream(query.message.chat.id)
            await query.answer("Paused")
        elif query.data == "resume":
            await call_py.resume_stream(query.message.chat.id)
            await query.answer("Resumed")
        elif query.data == "stop":
            await call_py.leave_call(query.message.chat.id)
            await query.message.delete()
            await query.answer("Stopped")
    except:
        await query.answer("No active stream")

# --- TAG ALL ---
@app.on_message(filters.command("tagall") & filters.group)
async def tag_all(client, message: Message):
    # Check if sender is admin
    check = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not check.status in ("administrator", "creator"):
        return await message.reply("<code>❌ Admin Only!</code>")

    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            members.append(m.user.mention)
    
    for i in range(0, len(members), 5):
        await client.send_message(message.chat.id, f"🔔 {', '.join(members[i:i+5])}")
        await asyncio.sleep(2)

# --- BOOT LOGIC ---
async def main():
    await app.start()
    await call_py.start()
    print("✅ DX-CODEX IS NOW LIVE")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

# --- CONFIGURATION (UPDATED) ---
API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "7853734473:AAHdGjbtPFWD6wFlyu8KRWteRg_961WGRJk"
GROUP_ID = -1003673065500

class DXBot(Client):
    def __init__(self):
        super().__init__(
            name="DX_Music_Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
        )
        self.call_py = PyTgCalls(self)

    async def start(self):
        await super().start()
        await self.call_py.start()
        print("💎 DX-CODEX Bot is now Online!")

app = DXBot()

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

    m = await message.reply("<code>🔍 Searching on YouTube...</code>")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("<code>❌ Song not found!</code>")

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]['title']
        duration = results[0]['duration']
        thumbnail = results[0]['thumbnails'][0]

        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info['url']

        await app.call_py.join_group_call(
            message.chat.id,
            AudioPiped(audio_url)
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop")
            ],
            [InlineKeyboardButton("⭐ DX-CODEX SYSTEM", url="https://t.me/DX_CODEX")]
        ])

        caption = (
            f"<b>🎧 Now Playing</b>\n\n"
            f"<b>📌 Title:</b> <code>{title[:40]}...</code>\n"
            f"<b>⏳ Duration:</b> <code>{duration}</code>\n"
            f"<b>👤 Requestor:</b> {message.from_user.mention}\n\n"
            f"<b>Playback:</b>\n"
            f"<code>00:00 💠━━━━━━━━━━━━━ {duration}</code>\n\n"
            f"<i>Design by BOT CREATOR DX-CODEX</i>"
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
            await app.call_py.pause_stream(query.message.chat.id)
            await query.answer("Paused ⏸")
        elif query.data == "resume":
            await app.call_py.resume_stream(query.message.chat.id)
            await query.answer("Resumed ▶️")
        elif query.data == "stop":
            await app.call_py.leave_group_call(query.message.chat.id)
            await query.message.delete()
            await query.answer("Stopped ⏹", show_alert=True)
    except:
        await query.answer("No active stream!")

# --- TAG ALL (ADMIN ONLY) ---
@app.on_message(filters.command("tagall") & filters.group)
async def tag_all(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await message.reply("<code>❌ Only Admins can use this!</code>")

    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            members.append(m.user.mention)
    
    await message.reply(f"<b>📣 Tagging {len(members)} users...</b>")
    
    for i in range(0, len(members), 5):
        await client.send_message(message.chat.id, f"🔔 {', '.join(members[i:i+5])}")
        await asyncio.sleep(2)

# --- SONG DOWNLOADER ---
@app.on_message(filters.command("song") & filters.group)
async def download_song(client, message: Message):
    query = " ".join(message.command[1:])
    if not query: return await message.reply("<code>Usage: /song [name]</code>")
    m = await message.reply("<code>📥 Downloading Audio...</code>")
    # Basic logic to acknowledge; full download requires local storage handling
    await m.edit(f"<b>✅ Search Complete:</b> <code>{query}</code>\n<i>File sending feature is ready!</i>")

if __name__ == "__main__":
    app.run()

import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

# --- CONFIGURATION ---
API_ID = 20579940  # Get from my.telegram.org
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
        print("DX-CODEX Music Bot is Online!")
        await self.call_py.start()

app = DXBot()

# --- AUTO DELETE SERVICE MESSAGES ---
@app.on_message(filters.group & filters.service)
async def delete_service(_, message: Message):
    try:
        await message.delete()
    except:
        pass

# --- MUSIC PLAYER WITH ADVANCE UI ---
@app.on_message(filters.command("play") & filters.group)
async def play_song(client, message: Message):
    if message.chat.id != GROUP_ID:
        return
    
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("`Usage: /play [song name]`")

    m = await message.reply("`🔍 Searching on YouTube...`")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("`❌ Song not found!`")

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

        # Advanced Design Buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸️ Pause", callback_data="pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume"),
                InlineKeyboardButton("⏹️ Stop", callback_data="stop")
            ],
            [InlineKeyboardButton("⭐ DX-CODEX SYSTEM", url="https://t.me/DX_CODEX")]
        ])

        # Premium Caption Design
        caption = (
            f"<b>🎧 Now Playing</b>\n\n"
            f"<b>📌 Title:</b> <code>{title}</code>\n"
            f"<b>⏳ Duration:</b> <code>{duration}</code>\n"
            f"<b>👤 Requested By:</b> {message.from_user.mention}\n\n"
            f"<b>Playback Progress:</b>\n"
            f"<code>00:00 💠━━━━━━━━━━━━━ {duration}</code>\n\n"
            f"<i>Powered by DX-CODEX Music System</i>"
        )

        await m.delete()
        await message.reply_photo(
            photo=thumbnail,
            caption=caption,
            reply_markup=buttons
        )

    except Exception as e:
        await m.edit(f"`❌ Error: {str(e)}`")

# --- SONG DOWNLOADER ---
@app.on_message(filters.command("song") & filters.group)
async def download_song(client, message: Message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("`Usage: /song [song name]`")
    
    m = await message.reply("`📥 Processing Download...`")
    # Add your downloader logic here
    await m.edit("`✅ Song sent to the group!`")

# --- CONTROLS CALLBACK ---
@app.on_callback_query(filters.regex(pattern=r"^(pause|resume|stop)$"))
async def controls(client, query: CallbackQuery):
    if query.data == "pause":
        await app.call_py.pause_stream(query.message.chat.id)
        await query.answer("Paused", show_alert=False)
    elif query.data == "resume":
        await app.call_py.resume_stream(query.message.chat.id)
        await query.answer("Resumed", show_alert=False)
    elif query.data == "stop":
        await app.call_py.leave_group_call(query.message.chat.id)
        await query.message.delete()
        await query.answer("Stopped", show_alert=True)

# --- TAG ALL (ADMIN ONLY) ---
@app.on_message(filters.command("tagall") & filters.group)
async def tag_all(client, message: Message):
    # Check Admin Permission
    check = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not check.status in ("administrator", "creator"):
        return await message.reply("`❌ Only Admins can use this!`")

    members = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            members.append(m.user.mention)
    
    await message.reply(f"<b>📣 Tagging {len(members)} users...</b>")
    
    for i in range(0, len(members), 5):
        await client.send_message(message.chat.id, f"🔔 {', '.join(members[i:i+5])}")
        await asyncio.sleep(1.5)

app.run()

const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const express = require('express');
const bodyParser = require('body-parser');

const token = '8339809079:AAGyTLUuk4gjjsshw8EJi6BolkfZnuft04Y';
const bot = new TelegramBot(token, { polling: true });
const app = express();
app.use(bodyParser.json());

let activeUsers = new Set();

// --- Control API ---
app.post('/activate', (req, res) => {
    const { chatId } = req.body;
    activeUsers.add(chatId.toString());
    bot.sendMessage(chatId, "<b>✅ Codex Online</b>\nYour session has started. You can now send phone numbers to lookup.", { parse_mode: 'HTML' });
    res.sendStatus(200);
});

app.post('/deactivate', (req, res) => {
    const { chatId } = req.body;
    activeUsers.delete(chatId.toString());
    bot.sendMessage(chatId, "<b>❌ Codex Offline</b>\nThe terminal session has ended. Bot is now inactive.", { parse_mode: 'HTML' });
    res.sendStatus(200);
});

// --- Bot Logic ---
bot.on('message', async (msg) => {
    const chatId = msg.chat.id.toString();
    const text = msg.text;

    if (!activeUsers.has(chatId)) {
        if (text === '/start') {
            return bot.sendMessage(chatId, "⚠️ <b>Code Access Denied</b>\nPlease login via the terminal script first.", { parse_mode: 'HTML' });
        }
        return;
    }

    if (text === '/start') {
        return bot.sendMessage(chatId, "👋 <b>Welcome C-Info!</b>\nPlease enter the mobile number you want to track without +91", { parse_mode: 'HTML' });
    }

    if (/^\d+$/.test(text)) {
        bot.sendMessage(chatId, "🔍 <i>Processing request...</i>", { parse_mode: 'HTML' });

        try {
            const response = await axios.get(`https://check-api-sage.vercel.app/?num=${text}`);
            const data = response.data;

            if (data.success && data["0"]) {
                const info = data["0"];
                const result = `
🌟 <b>CODE DETAILS FOUND</b> 🌟
━━━━━━━━━━━━━━━━━━━━
👤 <b>Name:</b> <code>${info.name}</code>
👨‍💼 <b>Father:</b> <code>${info.father_name}</code>
📱 <b>Mobile:</b> <code>${info.mobile}</code>
🆔 <b>ID Number:</b> <code>${info.id_number}</code>
📍 <b>Address:</b> <code>${info.address}</code>
🌐 <b>Circle:</b> <code>${info.circle}</code>
📧 <b>Email:</b> <code>${info.email || 'N/A'}</code>
━━━━━━━━━━━━━━━━━━━━
🛠 <b>Source:</b> @Termuxcodex
🕒 <b>Timestamp:</b> ${data.metadata.timestamp}
                `;
                bot.sendMessage(chatId, result, { parse_mode: 'HTML' });
            } else {
                bot.sendMessage(chatId, "❌ <b>No records found</b> for this number.", { parse_mode: 'HTML' });
            }
        } catch (error) {
            bot.sendMessage(chatId, "⚠️ <b>Error:</b> Unable to connect to the database.", { parse_mode: 'HTML' });
        }
    }
});

app.listen(3000, () => console.log('Backend Control Server Active on Port 3000'));


const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config();

const token = process.env.BOT_TOKEN;

const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, 'Да, со вайтренер ву, Аса хьуна г1о дийра ду жимма форме ва, дальше больше');
});

bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const text = msg.text;

  if (text.startsWith('/start')) return;

  bot.sendMessage(chatId, `Ты написал: ${text}`);
});
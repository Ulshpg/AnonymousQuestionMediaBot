from aiogram import Bot

LINK = "https://t.me/anonkamessBot" #Ссылка на бота
SMALL_LINK = "@anonkamessBot" #Юзернейм бота
ADMIN_ID = #ID админа
TELEGRAM_TOKEN = "" #Токен бота
YOOMONEY_TOKEN = "" #Токен юмани
PRICE = 89 #Цена випки
ALL_CONTENT_TYPE = ("photo", "video", "text", "voice", "video_note", "sticker")
LIMIT_SYMBOLS = 4000 #Лимит символов в сообщении
FIRST_PRICE = PRICE + 60 #Изначальная цена

bot = Bot(token=TELEGRAM_TOKEN)

from telethon import TelegramClient, events, Button
from telethon.tl.functions.messages import GetMessageReactionsListRequest
from telethon.utils import get_display_name
from html import escape
import re
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def transform_text(text):
    text = text.replace("⚠️", "✅", 1)
    text = re.sub(r'`ОЖИДАЕТ ОПЛАТЫ`', '`ОПЛАЧЕНО`', text, count=1)
    text = re.sub(
        r'⚠️ \*\*В статусе \*\*`ОЖИДАЕТ ОПЛАТЫ`.*',
        '✅ **В статусе **`ОПЛАЧЕНО`** вы можете ожидать получение подарка.**',
        text,
        flags=re.DOTALL
    )
    return text

async def send_confirmation_message(event):
    confirmation_text = "✅ **Вы оплатили сделку. Ожидайте получения подарка и затем нажмите на кнопку для подтверждения получения.**"
    
    # Создаем inline-кнопку с галочкой
    button = [Button.inline("✅ Подтвердить", b"confirm_receipt")]
    
    await event.respond(
        confirmation_text,
        buttons=button
    )

@client.on(events.NewMessage(forwards=True))
async def handle_forwarded(event):
    msg = event.message

    if not msg.text:
        await event.reply("❌ Не удалось прочитать текст.")
        return

    try:
        updated_text = transform_text(msg.text)
        buttons = [
            [Button.inline("👈 Назад", b"back"), 
             Button.inline("🔄 Обновить статус", b"refresh")]
        ]
        
        await event.respond(
            updated_text,
            buttons=buttons
        )
        
        # Отправляем сообщение с подтверждением
        await send_confirmation_message(event)

    except Exception as e:
        await event.reply(f"❌ Ошибка: {e}")

@client.on(events.CallbackQuery(data=b"confirm_receipt"))
async def confirm_receipt_handler(event):
    await event.respond("🎉 **Спасибо! Ваше получение подарка подтверждено!**")

print("🤖 Бот запущен и ждёт пересланных сообщений...")
client.run_until_disconnected()

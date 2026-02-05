import os
import asyncio
import random
import time
from aiohttp import web
from groq import AsyncGroq
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"
GROQ_API_KEY = "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"
ADMIN_USERNAME = "Natalya_golovickaya"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# СТАБИЛЬНАЯ КОЛОДА
TAROT_DECK = {
    "Шут": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "Маг": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
    "Жрица": "https://avatars.mds.yandex.net/get-entity_search/11019286/1227420746/S600xU_2x",
    "Императрица": "https://upload.wikimedia.org/wikipedia/commons/a/af/RWS_Tarot_03_Empress.jpg",
    "Император": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg",
    "Иерофант": "https://upload.wikimedia.org/wikipedia/commons/8/8d/RWS_Tarot_05_Hierophant.jpg",
    "Влюбленные": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_06_Lovers.jpg",
    "Колесница": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg",
    "Сила": "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg",
    "Отшельник": "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg",
    "Колесо Фортуны": "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "Справедливость": "https://upload.wikimedia.org/wikipedia/commons/e/e0/RWS_Tarot_11_Justice.jpg",
    "Повешенный": "https://upload.wikimedia.org/wikipedia/commons/2/2b/RWS_Tarot_12_Hanged_Man.jpg",
    "Смерть": "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg",
    "Умеренность": "https://upload.wikimedia.org/wikipedia/commons/f/f8/RWS_Tarot_14_Temperance.jpg",
    "Дьявол": "https://upload.wikimedia.org/wikipedia/commons/5/55/RWS_Tarot_15_Devil.jpg",
    "Башня": "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg",
    "Звезда": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "Луна": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg",
    "Солнце": "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg",
    "Суд": "https://upload.wikimedia.org/wikipedia/commons/d/d4/RWS_Tarot_20_Judgement.jpg",
    "Мир": "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg"
}


# --- ФУНКЦИИ ---

def get_card_url(name):
    """Берет ссылку и добавляет метку времени для обхода кэша и ошибки WEBPAGE_MEDIA_EMPTY"""
    base_url = TAROT_DECK.get(name, "https://via.placeholder.com/300x500.png?text=Tarot+Card")
    return f"{base_url}?v={time.time()}"


def get_main_menu():
    """Создает Reply-меню, которое всегда под рукой"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🃏 Карта дня")
    builder.button(text="🔮 Расклад на 3 карты")
    builder.button(text="✍️ Личный расклад")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True, persistent=True)


async def get_ai_reading(prompt):
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Ты — Наталья, мудрая проводница в мире Таро. Твои ответы — это глубокое исследование судьбы.\n\n"
                        "ПРИДЕРЖИВАЙСЯ СЛЕДУЮЩЕГО СТИЛЯ (ПО ОБРАЗЦУ):\n"
                        "1. Вступление: Начни с теплого приветствия и краткой оценки динамики расклада (например: 'Карты выстроились очень логично', 'Это история эволюции').\n"
                        "2. Общая атмосфера: Опиши преобладающую стихию или главный посыл всех карт вместе.\n"
                        "3. Попозиционный разбор: Для каждой карты укажи название, её значение и что она значит конкретно для ситуации пользователя.\n"
                        "4. Интерпретация всей истории: Соедини все карты в единый связный рассказ в кавычках.\n"
                        "5. Сравнение вариантов (если вопрос о выборе): Оценивай потенциал дохода, условия и общую картину для каждого пути.\n"
                        "6. Совет и Итог: Дай четкую рекомендацию, на что обратить внимание и какой путь выбрать.\n\n"
                        "ТОН: Эмпатичный, профессиональный, психологичный. Используй красивые метафоры, но оставайся практичной. Отвечай на русском языке."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return completion.choices[0].message.content
    except Exception:
        return "Милый друг, нити судьбы сейчас слишком запутаны для взгляда... Попробуй еще раз чуть позже."


# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Твой новый текст приветствия
    welcome_text = (
        "✨ **Доброго дня, дорогой друг! Рада видеть тебя в нашем пространстве** ✨\n\n"
        "Что тебя беспокоит? Что тебе сейчас важно? Что ты хочешь узнать? "
        "Как ты себя чувствуешь? Какую задачу хочешь решить?\n\n"
        "🔮 **Мысленно задай свой вопрос или попроси совета, и карты помогут тебе!**\n"
        "Просто сердцем выбери нужный расклад.\n\n"
        "🤝 _Если хочешь, чтобы я лично тебе помогла, выбери личный расклад, и напиши мне._"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@dp.message(F.text == "✍️ Личный расклад")
async def personal_reading(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="✨ Написать Наталье", url=f"https://t.me/{ADMIN_USERNAME}")
    await message.answer(
        "Для индивидуального разбора ситуации жду тебя в личных сообщениях:",
        reply_markup=kb.as_markup()
    )


@dp.message(F.text.in_({"🃏 Карта дня", "🔮 Расклад на 3 карты"}))
async def handle_draw(message: types.Message):
    num = 1 if "Карта дня" in message.text else 3
    selected_names = random.sample(list(TAROT_DECK.keys()), num)

    # Сначала визуализация
    media = [types.InputMediaPhoto(media=get_card_url(name)) for name in selected_names]

    try:
        await message.answer_media_group(media=media)
    except TelegramBadRequest:
        # Если ссылка из списка сдохла, шлем текст и переген
        await message.answer(
            f"Выпавшие карты: {', '.join(selected_names)}\n(Изображения временно заменяются энергетическим кодом...)")

    # Затем запрос к Groq
    prompt = f"Расклад Таро: {', '.join(selected_names)}."
    if num == 3:
        prompt += " Кратко: 1-прошлое, 2-настоящее, 3-будущее."

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    reading = await get_ai_reading(prompt)

    kb = InlineKeyboardBuilder()
    kb.button(text="🔮 Записаться на полный разбор", url=f"https://t.me/{ADMIN_USERNAME}")

    await message.answer(
        f"📜 **Послание карт:**\n\n{reading}",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )


@dp.message()
async def chat_msg(message: types.Message):
    """Любое сообщение, не попавшее в фильтры, получает ответ ИИ и возвращает меню"""
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    response = await get_ai_reading(message.text)
    await message.answer(response, reply_markup=get_main_menu())


# --- SERVER ---
async def handle(request): return web.Response(text="OK")


async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app);
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    asyncio.create_task(web.TCPSite(runner, '0.0.0.0', port).start())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())



import os
import asyncio
import random
import time
from aiohttp import web
from groq import AsyncGroq
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
# Токены и ключи подхватываются из настроек Render (Environment Variables)
BOT_TOKEN = "8557375398:AAF0rafVTVUQmT7fUn68L0afBYOKW8NxsjM"
GROQ_API_KEY = "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"
ADMIN_USERNAME = "Natalya_golovickaya"
DEV_USERNAME = "illumanest"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# --- ПОЛНАЯ БАЗА ТАРО (78 КАРТ) ---
TAROT_DECK = {
    # Старшие Арканы
    "Шут": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "Маг": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
    "Жрица": "https://avatars.mds.yandex.net/get-entity_search/2295215/1243844570/S600xU_2x",
    "Императрица": "https://avatars.mds.yandex.net/get-entity_search/7980979/1230442980/S600xU_2x",
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
    "Суд": "https://avatars.mds.yandex.net/get-entity_search/4964907/1228608504/S600xU_2x",
    "Мир": "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg",
    # Жезлы
    "Туз Жезлов": "https://upload.wikimedia.org/wikipedia/commons/1/11/Wands01.jpg",
    "Двойка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Wands02.jpg",
    "Тройка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Wands03.jpg",
    "Четверка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Wands04.jpg",
    "Пятерка Жезлов": "https://avatars.mds.yandex.net/i?id=457ab80829756c7b01f55abc3b7b11db_l-8199736-images-thumbs&n=13",
    "Шестерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wands06.jpg",
    "Семерка Жезлов": "https://i.pinimg.com/736x/2a/46/08/2a4608fb9a3b0132c0c51a929e56f019.jpg",
    "Восьмерка Жезлов": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Wands08.jpg",
    "Девятка Жезлов": "https://i.pinimg.com/736x/fe/6d/a1/fe6da1ab4cb0dd718e2a9223566b7546.jpg",
    "Десятка Жезлов": "https://i.pinimg.com/originals/5d/ad/e4/5dade4eb375ef62f828189d5015ebbae.jpg",
    "Паж Жезлов": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Wands11.jpg",
    "Рыцарь Жезлов": "https://upload.wikimedia.org/wikipedia/commons/1/16/Wands12.jpg",
    "Королева Жезлов": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Wands13.jpg",
    "Король Жезлов": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Wands14.jpg",
    # Кубки
    "Туз Кубков": "https://upload.wikimedia.org/wikipedia/commons/3/36/Cups01.jpg",
    "Двойка Кубков": "https://upload.wikimedia.org/wikipedia/commons/f/f8/Cups02.jpg",
    "Тройка Кубков": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Cups03.jpg",
    "Четверка Кубков": "https://upload.wikimedia.org/wikipedia/commons/3/35/Cups04.jpg",
    "Пятерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Cups05.jpg",
    "Шестерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/1/17/Cups06.jpg",
    "Семерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Cups07.jpg",
    "Восьмерка Кубков": "https://upload.wikimedia.org/wikipedia/commons/6/60/Cups08.jpg",
    "Девятка Кубков": "https://upload.wikimedia.org/wikipedia/commons/2/24/Cups09.jpg",
    "Десятка Кубков": "https://i.pinimg.com/originals/61/9e/00/619e0051588eaa68249799e860dcaff1.jpg",
    "Паж Кубков": "https://upload.wikimedia.org/wikipedia/commons/a/ad/Cups11.jpg",
    "Рыцарь Кубков": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Cups12.jpg",
    "Королева Кубков": "https://upload.wikimedia.org/wikipedia/commons/6/62/Cups13.jpg",
    "Король Кубков": "https://upload.wikimedia.org/wikipedia/commons/0/04/Cups14.jpg",
    # Мечи
    "Туз Мечей": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Swords01.jpg",
    "Двойка Мечей": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Swords02.jpg",
    "Тройка Мечей": "https://upload.wikimedia.org/wikipedia/commons/0/02/Swords03.jpg",
    "Четверка Мечей": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Swords04.jpg",
    "Пятерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/23/Swords05.jpg",
    "Шестерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/29/Swords06.jpg",
    "Семерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/3/34/Swords07.jpg",
    "Восьмерка Мечей": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Swords08.jpg",
    "Девятка Мечей": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Swords09.jpg",
    "Десятка Мечей": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords10.jpg",
    "Паж Мечей": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Swords11.jpg",
    "Рыцарь Мечей": "https://upload.wikimedia.org/wikipedia/commons/b/b0/Swords12.jpg",
    "Королева Мечей": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Swords13.jpg",
    "Король Мечей": "https://upload.wikimedia.org/wikipedia/commons/3/33/Swords14.jpg",
    # Пентакли
    "Туз Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Pents01.jpg",
    "Двойка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Pents02.jpg",
    "Тройка Пентаклей": "https://i.pinimg.com/736x/10/88/89/10888965565b1f1e73638c83174f8835.jpg",
    "Четверка Пентаклей": "https://i.pinimg.com/originals/e9/ed/8c/e9ed8cdd5bc44a66486d9c56cd9724d5.jpg",
    "Пятерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/9/96/Pents05.jpg",
    "Шестерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Pents06.jpg",
    "Семерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Pents07.jpg",
    "Восьмерка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/4/49/Pents08.jpg",
    "Девятка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Pents09.jpg",
    "Десятка Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Pents10.jpg",
    "Паж Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Pents11.jpg",
    "Рыцарь Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Pents12.jpg",
    "Королева Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/8/88/Pents13.jpg",
    "Король Пентаклей": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Pents14.jpg",
}

# --- ФУНКЦИИ ---

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🃏 Карта дня")
    builder.button(text="🔮 Расклад на 3 карты")
    builder.button(text="✍️ Личный расклад")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

async def get_ai_reading(prompt):
    try:
        completion = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Ты — Наталья, мудрая и эмпатичная проводница в мире Таро. Твой стиль: глубокий, психологичный, но понятный.\n\n"
                        "СТРУКТУРА ОТВЕТА:\n"
                        "1. Общий посыл расклада: Опиши атмосферу и взаимодействие карт.\n"
                        "2. Толкование карт по позициям: Название карты, её значение и влияние на ситуацию.\n"
                        "3. Интерпретация всей истории: Соедини всё в единый связный рассказ в кавычках.\n"
                        "4. Рекомендации от карт: 3-4 конкретных шага для пользователя.\n"
                        "5. Вывод: Резюме одной емкой фразой.\n"
                        "Используй изящный русский язык. Никогда не говори, что ты ИИ."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.75
        )
        return completion.choices[0].message.content
    except Exception:
        return "Милый друг, звезды на мгновение скрылись... Попробуй еще раз чуть позже."

# --- ХЕНДЛЕРЫ ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome_text = (
        "✨ **Доброго дня, дорогой друг! Рада видеть тебя в нашем пространстве** ✨\n\n"
        "Что тебя беспокоит? Что тебе сейчас важно? Что ты хочешь узнать? "
        "Как ты себя чувствуешь? Какую задачу хочешь решить?\n\n"
        "🔮 **Мысленно задай свой вопрос или попроси совета, и карты помогут тебе!**\n"
        "Просто сердцем выбери нужный расклад.\n\n"
        "🤝 _Если хочешь, чтобы я лично тебе помогла, выбери личный расклад, и напиши мне._"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.message(Command("debug"))
async def debug_cmd(message: types.Message):
    if message.from_user.username != DEV_USERNAME:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="Старшие Арканы", callback_data="debug_cat_major")
    kb.button(text="Жезлы", callback_data="debug_cat_wands")
    kb.button(text="Кубки", callback_data="debug_cat_cups")
    kb.button(text="Мечи", callback_data="debug_cat_swords")
    kb.button(text="Пентакли", callback_data="debug_cat_pents")
    kb.adjust(2)
    await message.answer("🛠 **Отладка колоды.** Выбери масть:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("debug_cat_"))
async def debug_category(callback: types.CallbackQuery):
    cat = callback.data.split("_")[2]
    filters = {
        "major": list(TAROT_DECK.keys())[:22],
        "wands": [k for k in TAROT_DECK.keys() if "Жезлов" in k],
        "cups": [k for k in TAROT_DECK.keys() if "Кубков" in k],
        "swords": [k for k in TAROT_DECK.keys() if "Мечей" in k],
        "pents": [k for k in TAROT_DECK.keys() if "Пентаклей" in k]
    }
    kb = InlineKeyboardBuilder()
    for name in filters.get(cat, []):
        kb.button(text=name, callback_data=f"check_{name}")
    kb.adjust(3)
    await callback.message.edit_text(f"Проверка масти {cat}:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("check_"))
async def check_card(callback: types.CallbackQuery):
    card_name = callback.data.split("_")[1]
    url = f"{TAROT_DECK[card_name]}?v={time.time()}"
    try:
        await callback.message.answer_photo(photo=url, caption=f"✅ {card_name}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)[:50]}")
    await callback.answer()

@dp.message(F.text == "✍️ Личный расклад")
async def personal_reading(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="✨ Написать Наталье", url=f"https://t.me/{ADMIN_USERNAME}")
    await message.answer("Для индивидуального разбора ситуации жду тебя в личных сообщениях:", reply_markup=kb.as_markup())

@dp.message(F.text.in_({"🃏 Карта дня", "🔮 Расклад на 3 карты"}))
async def handle_draw(message: types.Message):
    num = 1 if "Карта дня" in message.text else 3
    selected_names = random.sample(list(TAROT_DECK.keys()), num)
    
    media = [types.InputMediaPhoto(media=f"{TAROT_DECK[name]}?v={time.time()}") for name in selected_names]
    
    try:
        await message.answer_media_group(media=media)
    except Exception:
        await message.answer(f"Выпали карты: {', '.join(selected_names)}")

    prompt = f"Расклад на {num} карт: {', '.join(selected_names)}."
    if num == 3:
        prompt += " Трактуй: 1-прошлое, 2-настоящее, 3-будущее."
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    reading = await get_ai_reading(prompt)
    
    # Финальная фраза клиента
    warning_text = (
        "\n\n---\n"
        "Дорогой друг, автоматическая трактовка расклада не всегда точно отражает течение жизни. "
        "Если Вас смутил расклад, вы почувствовали беспокойство, тревогу, непонимание, "
        "появились подозрения на сглаз, порчу и другие влияния на Вас каких-то потусторонних сил, "
        "вы можете обратиться за помощью к Наталье. Она очень опытный Оракул и поможет Вам "
        "правильно интерпретировать Вашу ситуацию. Живой, ведающий, чувствующий человек поможет во всем разобраться."
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔮 Записаться к Наталье", url=f"https://t.me/{ADMIN_USERNAME}")
    
    await message.answer(f"📜 **Послание карт:**\n\n{reading}{warning_text}", reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.message()
async def chat_msg(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    response = await get_ai_reading(message.text)
    await message.answer(response, reply_markup=get_main_menu())

# --- SERVER ---
async def handle(request): return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    port = int(os.getenv('PORT', 8080))
    asyncio.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())



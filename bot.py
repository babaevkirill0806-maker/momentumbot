import asyncio
import logging
from urllib.parse import quote
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Ваш токен Telegram-бота
BOT_TOKEN = "8859337574:AAGuNq4KE-DEdRqtwWz3vUIhSkxynaxkz8k"
ADMIN_USERNAME = "TraidingNadzor"  # Ваш юзернейм без @

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Определение состояний FSM для ввода количества Stars
class SellStars(StatesGroup):
    waiting_for_amount = State()

# Главное меню клавиатуры
def get_main_keyboard():
    kb = [
        [types.KeyboardButton(text="⭐ Продать Stars"), types.KeyboardButton(text="🎁 Продать NFT")],
        [types.KeyboardButton(text="🛡️ Гарант"), types.KeyboardButton(text="📊 Прайс-лист")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 **Привет! Добро пожаловать в сервис скупки Stars и NFT подарков.**\n\n"
        f"🛡️ Безопасные сделки через гаранта: @{ADMIN_USERNAME}\n\n"
        f"Выберите интересующий раздел в меню ниже:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# Кнопка: Гарант
@dp.message(F.text == "🛡️ Гарант")
async def show_guarantor(message: types.Message):
    await message.answer(
        f"🛡️ **Гарант сервиса:**\n\n"
        f"Все сделки по скупке Stars и NFT проходят с гарантией честности.\n"
        f"По всем вопросам и для проведения сделок обращайтесь к гаранту: @{ADMIN_USERNAME}",
        parse_mode="Markdown"
    )

# Кнопка: Продать NFT
@dp.message(F.text == "🎁 Продать NFT")
async def show_nft_info(message: types.Message):
    await message.answer(
        f"🎁 **Скупка NFT подарков:**\n\n"
        f"За продажей желаемой NFT обращайтесь в ЛС @{ADMIN_USERNAME}",
        parse_mode="Markdown"
    )

# Кнопка: Прайс-лист
@dp.message(F.text == "📊 Прайс-лист")
async def show_price(message: types.Message):
    await message.answer(
        f"📊 **Текущий прайс на скупку Stars:**\n\n"
        f"• **100 Stars** = **140 рублей**\n"
        f"• Принимаем от **100** до **1000** Stars.\n\n"
        f"Для оформления заявки нажмите кнопку «⭐ Продать Stars».",
        parse_mode="Markdown"
    )

# Кнопка: Продать Stars (Начало диалога)
@dp.message(F.text == "⭐ Продать Stars")
async def start_sell_stars(message: types.Message, state: FSMContext):
    await state.set_state(SellStars.waiting_for_amount)
    await message.answer(
        "Введите количество **Telegram Stars**, которое вы хотите продать (от **100** до **1000**):",
        parse_mode="Markdown"
    )

# Обработка ввода количества Stars
@dp.message(SellStars.waiting_for_amount)
async def process_stars_amount(message: types.Message, state: FSMContext):
    text = message.text.strip()
    
    if not text.isdigit():
        await message.answer("❌ Пожалуйста, введите количество числом (например: 100, 500, 1000).")
        return

    amount = int(text)

    if amount < 100 or amount > 1000:
        await message.answer("❌ Минимальное количество для продажи — **100 Stars**, максимальное — **1000 Stars**. Попробуйте еще раз:")
        return

    # Расчет цены: 100 Stars = 140 рублей (1.4 рубля за 1 star)
    price_rub = round(amount * 1.4, 2)
    
    # Текст сообщения для администратора
    order_text = f"Здравствуйте! Хочу продать {amount} Stars за {price_rub} рублей. Мой ID: {message.from_user.id}"
    encoded_text = quote(order_text)
    
    # Ссылка для прямого перехода в ЛС к админу с текстом
    direct_link = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📩 Отправить заявку в ЛС", url=direct_link)]
    ])

    await message.answer(
        f"✅ **Заявка сформирована!**\n\n"
        f"• **Количество:** {amount} Stars\n"
        f"• **К выплате:** {price_rub} рублей\n\n"
        f"Нажмите кнопку ниже, чтобы перейти в ЛС к @{ADMIN_USERNAME} и отправить готовое сообщение:",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

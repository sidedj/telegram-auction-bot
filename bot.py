# Файл: bot.pyбот заработал со всем функционалом

import asyncio
import logging
import os
import queue
from datetime import datetime, timedelta
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputMediaPhoto,
    InputMediaVideo
)

# Импорты наших модулей
from config import load_config
from database import Database
from auction_timer import AuctionTimer
from balance_manager import BalanceManager
from auction_persistence import AuctionPersistence
# from api_integration import api_integration  # Отключено
# from yoomoney_payment import YooMoneyPayment  # Отключено
# from payment_server import get_notification_queue  # Отключено

# --- 1. КОНФИГУРАЦИЯ ---

# --- Функция фильтрации вредных ссылок и @ упоминаний ---
def filter_description(description: str) -> tuple[str, bool]:
    """
    Фильтрует описание товара, удаляя ссылки и @ упоминания
    
    Args:
        description: Исходное описание
        
    Returns:
        tuple: (отфильтрованное описание, есть ли нарушения)
    """
    if not description:
        return description, False
    
    original = description
    has_violations = False
    
    # Удаляем ссылки (http, https, www, t.me, telegram.me, домены)
    url_patterns = [
        r'https?://[^\s]+',  # HTTP/HTTPS ссылки
        r'www\.[^\s]+',      # www ссылки
        r't\.me/[^\s]+',     # t.me ссылки
        r'telegram\.me/[^\s]+',  # telegram.me ссылки
        r'[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}[^\s]*',  # Любые домены (2+ букв)
        r'@[a-zA-Zа-яА-Я0-9_]+',  # @ упоминания (включая кириллицу)
    ]
    
    for pattern in url_patterns:
        if re.search(pattern, description, re.IGNORECASE):
            has_violations = True
            description = re.sub(pattern, '[ССЫЛКА УДАЛЕНА]', description, flags=re.IGNORECASE)
    
    # Удаляем множественные пробелы
    description = re.sub(r'\s+', ' ', description).strip()
    
    return description, has_violations

# --- 2. ИНИЦИАЛИЗАЦИЯ ---

# Загружаем конфигурацию
config = load_config()
BOT_TOKEN = config['BOT_TOKEN']
PAYMENTS_PROVIDER_TOKEN = config['PAYMENTS_PROVIDER_TOKEN']
YOOMONEY_RECEIVER = config['YOOMONEY_RECEIVER']
YOOMONEY_SECRET = config['YOOMONEY_SECRET']
YOOMONEY_NOTIFICATION_URL = config['YOOMONEY_NOTIFICATION_URL']
PAYMENT_PLANS = config['PAYMENT_PLANS']
YOOMONEY_BASE_URL = config['YOOMONEY_BASE_URL']
CHANNEL_USERNAME = config['CHANNEL_USERNAME']
CHANNEL_USERNAME_LINK = config['CHANNEL_USERNAME_LINK']
CHANNEL_DISPLAY_NAME = config['CHANNEL_DISPLAY_NAME']
ADMIN_USER_IDS = config['ADMIN_USER_IDS']
DATABASE_PATH = config['DATABASE_PATH']

# Инициализация базы данных
db = Database(DATABASE_PATH)

# Инициализация менеджера балансов
balance_manager = BalanceManager(DATABASE_PATH)

# Инициализация системы оплаты ЮMoney (отключено)
# yoomoney_payment = YooMoneyPayment()

# --- 3. КЛАВИАТУРЫ ---

# Функция для создания главного меню с учетом баланса пользователя
def get_main_menu(user_balance=None, is_admin=False):
    balance_text = "∞" if is_admin else str(user_balance) if user_balance is not None else "?"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать аукцион 🚀")],
            [
                KeyboardButton(text="Мои аукционы 📦"),
                KeyboardButton(text=f"Пополнить баланс 💳 ({balance_text})")
            ],
            [KeyboardButton(text="📊 Статистика")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Нажмите /start для начала работы"
    )

# Статичное главное меню для случаев, когда баланс неизвестен
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать аукцион 🚀")],
        [
            KeyboardButton(text="Мои аукционы 📦"),
            KeyboardButton(text="Пополнить баланс 💳")
        ],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Нажмите /start для начала работы"
)

# Inline-кнопки для выбора длительности аукциона
def get_duration_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="1 час", callback_data="duration_3600"),
            InlineKeyboardButton(text="6 часов", callback_data="duration_21600"),
            InlineKeyboardButton(text="12 часов", callback_data="duration_43200"),
        ],
        [
            InlineKeyboardButton(text="1 день", callback_data="duration_86400"),
            InlineKeyboardButton(text="3 дня", callback_data="duration_259200"),
            InlineKeyboardButton(text="7 дней", callback_data="duration_604800"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Ранее здесь были inline-кнопки оплаты; удалены по требованию

# Inline-кнопки для управления созданным лотом (предпросмотр)
def get_preview_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_auction")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_auction")],
        [InlineKeyboardButton(text="❌ Удалить", callback_data="delete_auction")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура торгов с выкупом
def get_bidding_keyboard(blitz_price: int | None):
    rows = [[
        InlineKeyboardButton(text="+100 ₽", callback_data=f"bid:100"),
        InlineKeyboardButton(text="+500 ₽", callback_data=f"bid:500"),
        InlineKeyboardButton(text="+1000 ₽", callback_data=f"bid:1000"),
    ]]
    if blitz_price:
        rows.append([InlineKeyboardButton(text=f"Выкупить за {blitz_price} ₽", callback_data="buyout")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# --- 4. ЛОГИКА БОТА ---

# Совместимость с aiogram v2/v3
import importlib
try:
    client_default = importlib.import_module("aiogram.client.default")
    enums = importlib.import_module("aiogram.enums")
    DefaultBotProperties = getattr(client_default, "DefaultBotProperties")
    ParseMode = getattr(enums, "ParseMode")
    DEFAULT_BOT_KWARGS = {"default": DefaultBotProperties(parse_mode=ParseMode.HTML)}
except Exception:
    DEFAULT_BOT_KWARGS = {"parse_mode": "HTML"}

# --- Функция проверки подписки на канал ---
async def check_user_subscription(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        # Получаем информацию о статусе подписки пользователя
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        
        # Проверяем статус подписки
        # member, administrator, creator - активные подписчики
        # left, kicked - не подписан
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking subscription for user {user_id}: {e}")
        # В случае ошибки считаем, что пользователь не подписан
        return False

# --- Инициализация ---
bot = Bot(token=BOT_TOKEN, **DEFAULT_BOT_KWARGS)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Инициализация таймера аукционов
auction_timer = AuctionTimer(bot, db, CHANNEL_USERNAME)

# Инициализация системы персистентности аукционов
auction_persistence = AuctionPersistence(db)

# Буфер для альбомов фотографий
album_buffers = {}

# --- Машина состояний (FSM) для создания аукциона ---
class AuctionCreation(StatesGroup):
    waiting_for_photos = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_blitz_price = State()
    waiting_for_duration = State()

# --- Машина состояний (FSM) для создания байт поста ---
class BuyPostCreation(StatesGroup):
    waiting_for_photos = State()
    waiting_for_description = State()
    waiting_for_price = State()

# --- Хендлеры команд ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Получаем или создаем пользователя в базе данных
    user = await db.get_or_create_user(user_id, username, full_name)
    
    # Проверяем, является ли пользователь администратором
    is_admin = user_id in ADMIN_USER_IDS
    if is_admin and not user['is_admin']:
        await db.grant_admin_status(user_id)
        user['is_admin'] = True

    balance_text = "∞ (администратор)" if user['is_admin'] else f"{user['balance']}"

    # Создаем меню с учетом баланса пользователя
    dynamic_menu = get_main_menu(user['balance'], user['is_admin'])

    await message.answer(
        f"👋 <b>Добро пожаловать в бот аукционов!</b>\n\n"
        f"🎯 <b>Что я умею:</b>\n"
        f"• Создавать аукционы с фото/видео\n"
        f"• Проводить торги в реальном времени\n"
        f"• Управлять ставками и блиц-покупками\n"
        f"• Отслеживать историю торгов\n\n"
        f"💰 <b>Ваш баланс:</b> {balance_text} публикаций\n\n"
        f"📢 <b>Важно:</b> Для участия в аукционах необходимо быть подписанным на канал <a href='https://t.me/{CHANNEL_USERNAME_LINK}'>Барахолка СПБ</a>\n\n"
        f"🚀 <b>Готовы начать?</b> Нажмите кнопку ниже!",
        reply_markup=dynamic_menu,
        parse_mode="HTML"
    )


# --- Хендлер "Мои аукционы" ---
@dp.message(F.text == "Мои аукционы 📦")
async def my_auctions(message: types.Message):
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    # Получаем активные аукционы пользователя
    active_auctions = await db.get_user_auctions(user_id, 'active')
    
    if not active_auctions:
        await message.answer("У вас нет активных аукционов (аукционы, которые еще не завершились по времени).")
        return
    
    text = f"📦 <b>Ваши активные аукционы ({len(active_auctions)}):</b>\n"
    text += f"<i>Показаны только аукционы, которые еще не завершились по времени</i>\n\n"
    
    for auction in active_auctions:
        time_left = await auction_timer.get_auction_time_left(auction['end_time'])
        text += f"🆔 <b>ID:</b> {auction['id']}\n"
        text += f"📝 <b>Описание:</b> {auction['description'][:50]}{'...' if len(auction['description']) > 50 else ''}\n"
        text += f"💰 <b>Текущая цена:</b> {auction['current_price']} ₽\n"
        text += f"⏰ <b>Осталось:</b> {time_left}\n"
        text += f"👑 <b>Лидер:</b> @{auction['current_leader_username'] if auction['current_leader_username'] else 'Нет'}\n\n"
    
    # Создаем клавиатуру с кнопками для каждого аукциона
    keyboard_buttons = []
    for auction in active_auctions:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📊 История ставок (ID: {auction['id']})", 
                callback_data=f"history_{auction['id']}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# --- Хендлер статистики ---
@dp.message(F.text == "📊 Статистика")
async def statistics(message: types.Message):
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    # Получаем все аукционы пользователя
    all_auctions = await db.get_user_auctions(user_id)
    
    # Получаем количество действительно активных аукционов (не истекших по времени)
    active_count = await db.get_truly_active_auctions_count(user_id)
    sold_count = len([a for a in all_auctions if a['status'] == 'sold'])
    expired_count = len([a for a in all_auctions if a['status'] == 'expired'])
    
    text = f"📊 <b>Ваша статистика:</b>\n\n"
    text += f"💰 <b>Баланс:</b> {user['balance']} публикаций\n"
    text += f"🚀 <b>Всего аукционов:</b> {len(all_auctions)}\n"
    text += f"🟢 <b>Активных:</b> {active_count}\n"
    text += f"✅ <b>Проданных:</b> {sold_count}\n"
    text += f"⏰ <b>Завершенных:</b> {expired_count}\n"
    
    if user['is_admin']:
        text += f"\n👑 <b>Статус:</b> Администратор"
        # Добавляем кнопку админ-панели для администраторов
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")]
        ])
        await message.answer(text, reply_markup=admin_keyboard, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")

# --- Хендлеры пополнения баланса ---
@dp.message(F.text.startswith("Пополнить баланс 💳"))
async def top_up_balance(message: types.Message):
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if user['is_admin']:
        await message.answer("У вас неограниченный баланс как у администратора.")
        return
    
    # Создаем клавиатуру для выбора количества публикаций
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 публикация - 50₽", callback_data="buy_1"),
            InlineKeyboardButton(text="5 публикаций - 200₽", callback_data="buy_5")
        ],
        [
            InlineKeyboardButton(text="10 публикаций - 350₽", callback_data="buy_10"),
            InlineKeyboardButton(text="20 публикаций - 600₽", callback_data="buy_20")
        ]
    ])
    
    await message.answer(
        f"💳 <b>Пополнение баланса</b>\n\n"
        f"💰 <b>Ваш текущий баланс:</b> {user['balance']} публикаций\n\n"
        "Выберите количество публикаций для покупки:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("buy_"))
async def handle_purchase(callback: types.CallbackQuery):
    try:
        plan_id = callback.data.replace("buy_", "")
        
        if plan_id not in PAYMENT_PLANS:
            await callback.answer("Ошибка: неизвестный тарифный план.", show_alert=True)
            return
        
        user_id = callback.from_user.id
        plan = PAYMENT_PLANS[plan_id]
        
        # Генерируем уникальную ссылку на оплату (отключено)
        # payment_url = yoomoney_payment.generate_payment_url(plan_id, user_id)
        payment_url = f"https://yoomoney.ru/quickpay/confirm.xml?receiver={YOOMONEY_RECEIVER}&quickpay-form=shop&targets={plan['description']}&sum={plan['price']}&label=user_{user_id}"
        
        if not payment_url:
            await callback.answer("Ошибка: не удалось создать ссылку на оплату.", show_alert=True)
            return
        
        # Создаем клавиатуру с кнопкой оплаты
        payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Оплатить {plan['price']}₽", url=payment_url)],
            [InlineKeyboardButton(text="🔄 Обновить статус", callback_data=f"check_payment_{plan_id}")]
        ])
        
        await callback.message.answer(
            f"💳 <b>Пополнение баланса - {plan['description']}</b>\n\n"
            f"💰 <b>Сумма к оплате:</b> {plan['price']} ₽\n\n"
            f"📝 <b>Инструкция:</b>\n"
            f"1. Нажмите кнопку '💳 Оплатить {plan['price']}₽'\n"
            f"2. Выберите способ оплаты на сайте ЮMoney\n"
            f"3. После успешной оплаты нажмите '🔄 Обновить статус'\n\n"
            f"✅ <b>Автоматическое начисление:</b> Публикации будут добавлены автоматически после подтверждения оплаты!",
            reply_markup=payment_keyboard,
            parse_mode="HTML"
        )

        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error creating payment link: {e}")
        await callback.answer("Ошибка создания ссылки на оплату. Попробуйте позже.", show_alert=True)

@dp.callback_query(F.data.startswith("check_payment_"))
async def handle_payment_check(callback: types.CallbackQuery):
    """Обработчик проверки статуса платежа"""
    try:
        plan_id = callback.data.replace("check_payment_", "")
        user_id = callback.from_user.id
        user = await db.get_or_create_user(user_id)
        
        # Проверяем, что пользователь не администратор
        if user['is_admin']:
            await callback.answer("У вас неограниченный баланс как у администратора.", show_alert=True)
            return
        
        # Показываем текущий баланс
        await callback.answer(
            f"💰 <b>Ваш текущий баланс:</b> {user['balance']} публикаций\n\n"
            f"💡 <b>Подсказка:</b> Публикации начисляются автоматически после подтверждения оплаты ЮMoney. "
            f"Если прошло более 5 минут, обратитесь к администратору.",
            show_alert=True,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error checking payment status: {e}")
        await callback.answer("Ошибка проверки статуса платежа. Попробуйте позже.", show_alert=True)

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# Старый обработчик успешной оплаты удален - теперь используем ЮMoney

# --- Хендлеры создания аукциона ---
@dp.message(F.text == "Создать аукцион 🚀")
async def start_auction_creation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    is_admin_user = user['is_admin']

    # Проверяем подписку пользователя на канал (кроме администраторов)
    if not is_admin_user:
        is_subscribed = await check_user_subscription(user_id)
        if not is_subscribed:
            await message.answer(
                f"❌ <b>Для создания аукционов необходимо быть подписанным на канал!</b>\n\n"
                f"Подпишитесь на канал: <a href='https://t.me/{CHANNEL_USERNAME_LINK}'>Барахолка СПБ</a>\n"
                f"После подписки попробуйте создать аукцион снова.",
                reply_markup=main_menu,
                parse_mode="HTML"
            )
            return

    # Если пользователь уже в процессе создания — не перезапускаем, а подсказываем текущий шаг
    current_state = await state.get_state()
    if current_state:
        if current_state == AuctionCreation.waiting_for_photos.state:
            await message.answer(
                "Вы уже начали создание лота. Отправьте до 10 фото. Когда хватит — напишите «далее».\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu
            )
            return
        if current_state == AuctionCreation.waiting_for_description.state:
            await message.answer(
                "Фото уже получено. Введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu
            )
            return
        if current_state == AuctionCreation.waiting_for_price.state:
            await message.answer(
                "Описание сохранено. Укажите стартовую цену в рублях (одно число).\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu
            )
            return
        if current_state == AuctionCreation.waiting_for_blitz_price.state:
            await message.answer(
                "Стартовая цена сохранена. Укажите сумму полного выкупа (блиц-цена), не меньше стартовой.\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu
            )
            return
        if current_state == AuctionCreation.waiting_for_duration.state:
            await message.answer(
                "Цена уже указана. Выберите длительность аукциона:",
                reply_markup=get_duration_keyboard(),
            )
            return

    await state.set_state(AuctionCreation.waiting_for_photos)
    await state.update_data(media=[])
    await message.answer("Отправьте до 10 фото одним разом (альбомом) или по одному. Переход к описанию произойдет автоматически.", reply_markup=main_menu)

# Обработка отмены на любом шаге
@dp.message(StateFilter('*'), F.text.lower() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание отменено.", reply_markup=main_menu)

@dp.message(StateFilter(AuctionCreation.waiting_for_photos), (F.photo | F.video))
async def process_photo(message: types.Message, state: FSMContext):
    # Если это альбом (media_group), копим фото в буфере и завершаем автоматически небольшой задержкой
    if message.media_group_id:
        key = (message.from_user.id, message.media_group_id)
        buf = album_buffers.get(key) or {"media": [], "task": None}
        # Определяем тип и file_id
        if message.photo:
            item = {"type": "photo", "file_id": message.photo[-1].file_id, "order": message.message_id}
        else:
            item = {"type": "video", "file_id": message.video.file_id, "order": message.message_id}
        if len(buf["media"]) < 10:
            buf["media"].append(item)
        album_buffers[key] = buf

        # Перезапускаем таймер завершения альбома
        if buf["task"] and not buf["task"].done():
            buf["task"].cancel()

        async def finalize_after_delay():
            try:
                await asyncio.sleep(1.2)
            except asyncio.CancelledError:
                return
            local_buf = album_buffers.pop(key, None)
            if not local_buf:
                return
            data_inner = await state.get_data()
            media_inner = list(data_inner.get("media", []))
            # Сортируем элементы альбома по message_id для сохранения исходного порядка
            ordered = sorted(local_buf["media"], key=lambda m: m.get("order", 0))
            media_inner.extend(ordered)  # уже не больше 10
            media_inner = media_inner[:10]
            await state.update_data(media=media_inner)
            await state.set_state(AuctionCreation.waiting_for_description)
            await message.answer(
                "Фото приняты! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu,
            )

        buf["task"] = asyncio.create_task(finalize_after_delay())
        album_buffers[key] = buf
        return

    # Одиночное фото — сразу двигаемся дальше
    data = await state.get_data()
    media = list(data.get("media", []))
    if len(media) >= 10:
        await message.answer("Достигнут лимит 10 фото.", reply_markup=main_menu)
        return
    if message.photo:
        media.append({"type": "photo", "file_id": message.photo[-1].file_id})
    else:
        media.append({"type": "video", "file_id": message.video.file_id})
    await state.update_data(media=media)
    await state.set_state(AuctionCreation.waiting_for_description)
    await message.answer(
        "Фото приняты! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
        reply_markup=main_menu,
    )

# Поддержка случая, когда пользователь отправляет изображение как файл (document)
@dp.message(StateFilter(AuctionCreation.waiting_for_photos), F.document)
async def process_photo_document(message: types.Message, state: FSMContext):
    try:
        mime_type = message.document.mime_type or ""
    except Exception:
        mime_type = ""

    if mime_type.startswith("image/") or mime_type.startswith("video/"):
        data = await state.get_data()
        media = list(data.get("media", []))
        if len(media) >= 10:
            await message.answer("Достигнут лимит 10 медиа.", reply_markup=main_menu)
            return
        media.append({"type": "video" if mime_type.startswith("video/") else "photo", "file_id": message.document.file_id})
        await state.update_data(media=media)
        await state.set_state(AuctionCreation.waiting_for_description)
        await message.answer(
            "Медиа принято! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
            reply_markup=main_menu,
        )
    else:
        await message.answer("Похоже, вы отправили файл не с изображением. Пожалуйста, отправьте фото товара.", reply_markup=main_menu)

# Текст на шаге фотографий: показываем короткую подсказку один раз
@dp.message(StateFilter(AuctionCreation.waiting_for_photos), F.text)
async def handle_text_on_photos_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("hint_shown_on_photos"):
        await state.update_data(hint_shown_on_photos=True)
        await message.answer(
            "Отправьте фото/видео альбомом (до 10) или одно медиа — переход будет автоматический.",
            reply_markup=main_menu,
        )

@dp.message(StateFilter(AuctionCreation.waiting_for_description), F.text)
async def process_description(message: types.Message, state: FSMContext):
    # Фильтруем описание от ссылок и @ упоминаний
    filtered_description, has_violations = filter_description(message.text)
    
    if has_violations:
        await message.answer(
            "⚠️ <b>Внимание!</b> Из вашего описания были удалены ссылки и @ упоминания для безопасности.\n\n"
            f"<b>Отфильтрованное описание:</b>\n{filtered_description}\n\n"
            "Продолжить с этим описанием?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, продолжить", callback_data="confirm_filtered_description")],
                [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_description")]
            ]),
            parse_mode="HTML"
        )
        # Сохраняем отфильтрованное описание во временном состоянии
        await state.update_data(filtered_description=filtered_description)
        return
    
    # Если нарушений нет, сохраняем как обычно
    await state.update_data(description=filtered_description)
    await state.set_state(AuctionCreation.waiting_for_price)
    await message.answer(
        "Описание сохранено. Укажите стартовую цену в рублях (только число).\n\n<i>Для отмены напишите «отмена»</i>",
        reply_markup=main_menu,
    )

@dp.message(StateFilter(AuctionCreation.waiting_for_price), F.text)
async def process_price(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❗️Неверный формат. Введите одно число, например: <code>1000</code>")
        return
    start_price = int(text)
    await state.update_data(start_price=start_price)
    await state.set_state(AuctionCreation.waiting_for_blitz_price)
    await message.answer(
        "Стартовая цена сохранена. Теперь укажите сумму полного выкупа (блиц-цена), не меньше стартовой.",
        reply_markup=main_menu,
    )

@dp.message(StateFilter(AuctionCreation.waiting_for_blitz_price), F.text)
async def process_blitz_price(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❗️Неверный формат. Введите одно число, например: <code>5000</code>")
        return
    data = await state.get_data()
    start_price = int(data.get("start_price", 0))
    blitz_price = int(text)
    if blitz_price < start_price:
        await message.answer("Блиц-цена не может быть меньше стартовой. Попробуйте снова.")
        return
    await state.update_data(blitz_price=blitz_price)
    await state.set_state(AuctionCreation.waiting_for_duration)
    await message.answer("Цена установлена. Выберите длительность аукциона:", reply_markup=get_duration_keyboard())

@dp.callback_query(StateFilter(AuctionCreation.waiting_for_duration), F.data.startswith("duration_"))
async def process_duration(callback: types.CallbackQuery, state: FSMContext):
    duration_seconds = int(callback.data.split("_")[1])
    end_time = datetime.now() + timedelta(seconds=duration_seconds)
    await state.update_data(duration=duration_seconds, end_time=end_time, end_time_str=end_time.strftime("%d.%m.%Y %H:%M"))
    
    data = await state.get_data()
    
    # Сохраняем аукцион в базе данных
    auction_id = await db.create_auction(
        owner_id=callback.from_user.id,
        description=data['description'],
        start_price=data['start_price'],
        blitz_price=data['blitz_price'],
        end_time=end_time,
        media_files=data['media']
    )
    
    # Синхронизируем с внешним API (если настроен)
    try:
        auction_data = {
            "id": auction_id,
            "description": data['description'],
            "start_price": data['start_price'],
            "blitz_price": data['blitz_price'],
            "end_time": end_time.isoformat(),
            "owner_id": callback.from_user.id,
            "media_count": len(data['media'])
        }
        # await api_integration.sync_auction_to_external(auction_data)  # Отключено
    except Exception as e:
        logging.warning(f"Не удалось синхронизировать аукцион с внешним API: {e}")
    
    # Сохраняем ID аукциона в состоянии для предпросмотра
    await state.update_data(auction_id=auction_id)

    media_list = data.get('media', [])
    caption_text = (
        f"<b>{data['description']}</b>\n\n"
        f"<b>Стартовая цена:</b> {data['start_price']} ₽\n"
        f"<b>Блиц-цена:</b> {data['blitz_price']} ₽\n"
        f"<b>Окончание:</b> {data['end_time_str']}\n"
        f"Медиа: {len(media_list)} шт."
    )
    
    await callback.message.delete()
    first_media = media_list[0] if media_list else None
    if first_media and first_media.get('type') == 'video':
        await callback.message.answer_video(
            video=first_media['file_id'],
            caption=f"<b>--- ПРЕДПРОСМОТР ---</b>\n\n{caption_text}",
            reply_markup=get_preview_keyboard(),
            parse_mode="HTML"
        )
    else:
        first_file_id = first_media['file_id'] if first_media else None
        await callback.message.answer_photo(
            photo=first_file_id,
            caption=f"<b>--- ПРЕДПРОСМОТР ---</b>\n\n{caption_text}",
            reply_markup=get_preview_keyboard(),
            parse_mode="HTML"
        )
    await state.clear()
    await callback.answer()

# --- Обработчики для создания байт поста ---
@dp.message(StateFilter(BuyPostCreation.waiting_for_photos), (F.photo | F.video))
async def process_buy_post_photo(message: types.Message, state: FSMContext):
    # Если это альбом (media_group), копим фото в буфере и завершаем автоматически небольшой задержкой
    if message.media_group_id:
        key = (message.from_user.id, message.media_group_id)
        buf = album_buffers.get(key) or {"media": [], "task": None}
        # Определяем тип и file_id
        if message.photo:
            item = {"type": "photo", "file_id": message.photo[-1].file_id, "order": message.message_id}
        else:
            item = {"type": "video", "file_id": message.video.file_id, "order": message.message_id}
        if len(buf["media"]) < 10:
            buf["media"].append(item)
        album_buffers[key] = buf

        # Перезапускаем таймер завершения альбома
        if buf["task"] and not buf["task"].done():
            buf["task"].cancel()

        async def finalize_after_delay():
            try:
                await asyncio.sleep(1.2)
            except asyncio.CancelledError:
                return
            local_buf = album_buffers.pop(key, None)
            if not local_buf:
                return
            data_inner = await state.get_data()
            media_inner = list(data_inner.get("media", []))
            # Сортируем элементы альбома по message_id для сохранения исходного порядка
            ordered = sorted(local_buf["media"], key=lambda m: m.get("order", 0))
            media_inner.extend(ordered)  # уже не больше 10
            media_inner = media_inner[:10]
            await state.update_data(media=media_inner)
            await state.set_state(BuyPostCreation.waiting_for_description)
            await message.answer(
                "Фото приняты! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
                reply_markup=main_menu,
            )

        buf["task"] = asyncio.create_task(finalize_after_delay())
        album_buffers[key] = buf
        return

    # Одиночное фото — сразу двигаемся дальше
    data = await state.get_data()
    media = list(data.get("media", []))
    if len(media) >= 10:
        await message.answer("Достигнут лимит 10 фото.", reply_markup=main_menu)
        return
    if message.photo:
        media.append({"type": "photo", "file_id": message.photo[-1].file_id})
    else:
        media.append({"type": "video", "file_id": message.video.file_id})
    await state.update_data(media=media)
    await state.set_state(BuyPostCreation.waiting_for_description)
    await message.answer(
        "Фото приняты! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
        reply_markup=main_menu,
    )

# Поддержка случая, когда пользователь отправляет изображение как файл (document) для байт поста
@dp.message(StateFilter(BuyPostCreation.waiting_for_photos), F.document)
async def process_buy_post_photo_document(message: types.Message, state: FSMContext):
    try:
        mime_type = message.document.mime_type or ""
    except Exception:
        mime_type = ""

    if mime_type.startswith("image/") or mime_type.startswith("video/"):
        data = await state.get_data()
        media = list(data.get("media", []))
        if len(media) >= 10:
            await message.answer("Достигнут лимит 10 медиа.", reply_markup=main_menu)
            return
        media.append({"type": "video" if mime_type.startswith("video/") else "photo", "file_id": message.document.file_id})
        await state.update_data(media=media)
        await state.set_state(BuyPostCreation.waiting_for_description)
        await message.answer(
            "Медиа принято! Теперь введите описание товара (название, состояние и т.д.).\n\n<i>Для отмены напишите «отмена»</i>",
            reply_markup=main_menu,
        )
    else:
        await message.answer("Похоже, вы отправили файл не с изображением. Пожалуйста, отправьте фото товара.", reply_markup=main_menu)

# Текст на шаге фотографий для байт поста
@dp.message(StateFilter(BuyPostCreation.waiting_for_photos), F.text)
async def handle_text_on_buy_post_photos_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("hint_shown_on_photos"):
        await state.update_data(hint_shown_on_photos=True)
        await message.answer(
            "Отправьте фото/видео альбомом (до 10) или одно медиа — переход будет автоматический.",
            reply_markup=main_menu,
        )

@dp.message(StateFilter(BuyPostCreation.waiting_for_description), F.text)
async def process_buy_post_description(message: types.Message, state: FSMContext):
    # Фильтруем описание от ссылок и @ упоминаний
    filtered_description, has_violations = filter_description(message.text)
    
    if has_violations:
        await message.answer(
            "⚠️ <b>Внимание!</b> Из вашего описания были удалены ссылки и @ упоминания для безопасности.\n\n"
            f"<b>Отфильтрованное описание:</b>\n{filtered_description}\n\n"
            "Продолжить с этим описанием?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, продолжить", callback_data="confirm_filtered_buy_post_description")],
                [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_buy_post_description")]
            ]),
            parse_mode="HTML"
        )
        # Сохраняем отфильтрованное описание во временном состоянии
        await state.update_data(filtered_description=filtered_description)
        return
    
    # Если нарушений нет, сохраняем как обычно
    await state.update_data(description=filtered_description)
    await state.set_state(BuyPostCreation.waiting_for_price)
    await message.answer(
        "Описание сохранено. Укажите цену товара в рублях (только число).\n\n<i>Для отмены напишите «отмена»</i>",
        reply_markup=main_menu,
    )

@dp.message(StateFilter(BuyPostCreation.waiting_for_price), F.text)
async def process_buy_post_price(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❗️Неверный формат. Введите одно число, например: <code>1000</code>")
        return
    price = int(text)
    await state.update_data(price=price)
    
    data = await state.get_data()
    
    # Создаем клавиатуру с кнопкой подписки на канал
    buy_post_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", url="https://t.me/+DYI1hAaTWy0wOTAy")]
    ])
    
    media_list = data.get('media', [])
    caption_text = (
        f"<b>{data['description']}</b>\n\n"
        f"<b>Цена:</b> {data['price']} ₽\n\n"
        f"<b>Для покупки нажмите кнопку ниже 👇</b>"
    )
    
    first_media = media_list[0] if media_list else None
    if first_media and first_media.get('type') == 'video':
        await message.answer_video(
            video=first_media['file_id'],
            caption=f"<b>--- ПРЕДПРОСМОТР БАЙТ ПОСТА ---</b>\n\n{caption_text}",
            reply_markup=buy_post_keyboard,
            parse_mode="HTML"
        )
    else:
        first_file_id = first_media['file_id'] if first_media else None
        await message.answer_photo(
            photo=first_file_id,
            caption=f"<b>--- ПРЕДПРОСМОТР БАЙТ ПОСТА ---</b>\n\n{caption_text}",
            reply_markup=buy_post_keyboard,
            parse_mode="HTML"
        )
    
    # Создаем клавиатуру для подтверждения публикации
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать байт пост", callback_data="publish_buy_post")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_buy_post")]
    ])
    
    await message.answer(
        "Байт пост готов к публикации! Нажмите кнопку для публикации в канале.",
        reply_markup=confirm_keyboard
    )
    
    # Сохраняем данные поста для последующей публикации
    await state.update_data(
        post_media=media_list,
        post_description=data['description'],
        post_price=data['price'],
        preview_caption=caption_text
    )

# --- Хендлеры управления предпросмотром ---
@dp.callback_query(F.data == "delete_auction")
async def delete_auction(callback: types.CallbackQuery):
    # Получаем последний созданный аукцион пользователя
    user_auctions = await db.get_user_auctions(callback.from_user.id)
    if user_auctions:
        latest_auction = user_auctions[0]  # Самый новый
        await db.update_auction_status(latest_auction['id'], 'deleted')
    
    await callback.message.delete()
    await callback.message.answer("Аукцион удален.", reply_markup=main_menu)
    await callback.answer()

@dp.callback_query(F.data == "edit_auction")
async def edit_auction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await start_auction_creation(callback.message, state) # Просто начинаем процесс заново
    await callback.answer()

# Обработчики для байт поста
@dp.callback_query(F.data == "publish_buy_post")
async def publish_buy_post(callback: types.CallbackQuery, state: FSMContext):
    """Публикация байт поста в канал"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    # Получаем данные поста из состояния
    data = await state.get_data()
    post_media = data.get('post_media', [])
    post_description = data.get('post_description', '')
    post_price = data.get('post_price', 0)
    
    if not post_media or not post_description:
        await callback.answer("Данные поста не найдены. Попробуйте создать пост заново.", show_alert=True)
        return
    
    # Создаем текст поста
    caption_text = (
        f"<b>{post_description}</b>\n\n"
        f"<b>Цена:</b> {post_price} ₽\n\n"
        f"<b>Для покупки нажмите кнопку ниже 👇</b>"
    )
    
    # Создаем клавиатуру с кнопкой подписки на канал
    buy_post_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", url="https://t.me/+DYI1hAaTWy0wOTAy")]
    ])
    
    try:
        # Публикуем в канал
        first_media = post_media[0] if post_media else None
        if first_media and first_media.get('type') == 'video':
            posted_message = await bot.send_video(
                chat_id=CHANNEL_USERNAME,
                video=first_media['file_id'],
                caption=caption_text,
                reply_markup=buy_post_keyboard
            )
        else:
            first_file_id = first_media['file_id'] if first_media else None
            posted_message = await bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=first_file_id,
                caption=caption_text,
                reply_markup=buy_post_keyboard
            )
        
        await callback.message.edit_text("✅ Байт пост успешно опубликован в канале!")
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Failed to publish buy post: {e}")
        await callback.answer("Не удалось опубликовать в канале. Проверьте, что бот добавлен в канал и имеет права администратора.", show_alert=True)

@dp.callback_query(F.data == "cancel_buy_post")
async def cancel_buy_post(callback: types.CallbackQuery, state: FSMContext):
    """Отмена создания байт поста"""
    await callback.message.edit_text("Создание байт поста отменено.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "publish_auction")
async def check_balance_before_publish(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    is_admin_user = user['is_admin']

    # Проверяем подписку пользователя на канал (кроме администраторов)
    if not is_admin_user:
        is_subscribed = await check_user_subscription(user_id)
        if not is_subscribed:
            await callback.message.answer(
                f"❌ <b>Для создания аукционов необходимо быть подписанным на канал!</b>\n\n"
                f"Подпишитесь на канал: <a href='https://t.me/{CHANNEL_USERNAME_LINK}'>Барахолка СПБ</a>\n"
                f"После подписки попробуйте создать аукцион снова.",
                reply_markup=main_menu,
                parse_mode="HTML"
            )
            await callback.answer()
            return

    if is_admin_user or user['balance'] > 0:
        if not is_admin_user:
            # Списываем 1 публикацию
            await db.update_user_balance(
                user_id=user_id,
                amount=-1,
                transaction_type="auction_created",
                description="Создание аукциона"
            )
        
        await callback.message.edit_reply_markup(reply_markup=None)
        
        # Получаем последний созданный аукцион пользователя
        user_auctions = await db.get_user_auctions(user_id)
        if not user_auctions:
            await callback.message.answer("Лот не найден. Создайте аукцион заново.")
            await callback.answer()
            return

        auction_data = user_auctions[0]  # Самый новый аукцион
        
        # Форматируем текст аукциона
        text, bidding_keyboard = await auction_timer.format_auction_text(auction_data, show_buttons=True)

        try:
            # Публикуем в канал
            posted_message = await _publish_auction_to_channel(auction_data, text, bidding_keyboard)
            
            if posted_message:
                # Сохраняем информацию о сообщении в канале
                await db.set_auction_channel_info(
                    auction_data['id'],
                    posted_message.chat.id,
                    posted_message.message_id
                )
            
            new_balance = await db.get_user_balance(user_id)
            balance_text = "∞ (администратор)" if is_admin_user else f"{new_balance}"
            
            await callback.message.answer(
                f"✅ Опубликовано в канале <a href='https://t.me/{CHANNEL_USERNAME_LINK}'>Барахолка СПБ</a>.\n"
                f"Осталось публикаций: <b>{balance_text}</b>.",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Failed to post to channel: {e}")
            await callback.message.answer("Не удалось опубликовать в канале. Проверьте, что бот добавлен в канал и имеет права администратора.")
    else:
        await callback.message.answer(
            "❗️ На вашем балансе недостаточно публикаций. Пополните баланс для создания аукционов."
        )
    await callback.answer()


async def _publish_auction_to_channel(auction_data: dict, text: str, keyboard) -> types.Message:
    """Публикует аукцион в канал"""
    media_items = auction_data.get('media', [])
    
    if not media_items:
        return await bot.send_message(chat_id=CHANNEL_USERNAME, text=text, reply_markup=keyboard)
    
    # Если одно медиа — публикуем только его с кнопками
    if len(media_items) == 1:
        single = media_items[0]
        if single['type'] == 'photo':
            return await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=single['file_id'], caption=text, reply_markup=keyboard)
        else:
            return await bot.send_video(chat_id=CHANNEL_USERNAME, video=single['file_id'], caption=text, reply_markup=keyboard)
    
    # Множественные медиа
    # 1) Сначала публикуем весь альбом (без подписей)
    album = []
    for item in media_items[:10]:
        if item['type'] == 'photo':
            album.append(InputMediaPhoto(media=item['file_id']))
        else:
            album.append(InputMediaVideo(media=item['file_id']))

    try:
        await bot.send_media_group(chat_id=CHANNEL_USERNAME, media=album)
    except Exception as e:
        logging.warning(f"Failed to send media group: {e}")

    # 2) Затем пост с первой фотографией и кнопками
    head_photo = None
    for item in media_items:
        if item['type'] == 'photo':
            head_photo = item['file_id']
            break

    if head_photo:
        return await bot.send_photo(chat_id=CHANNEL_USERNAME, photo=head_photo, caption=text, reply_markup=keyboard)
    else:
        return await bot.send_message(chat_id=CHANNEL_USERNAME, text=text, reply_markup=keyboard)


# --- Логика обработки ставок (Callback) ---
@dp.callback_query(F.data == "buyout")
async def handle_buyout(callback: types.CallbackQuery):
    """Обработка выкупа по блиц-цене"""
    try:
        # Проверяем подписку пользователя на канал
        is_subscribed = await check_user_subscription(callback.from_user.id)
        if not is_subscribed:
            await callback.answer(
                f"❌ Для участия в аукционе необходимо быть подписанным на канал!\n"
                f"Подпишитесь на канал: https://t.me/{CHANNEL_USERNAME_LINK}", 
                show_alert=True
            )
            return

        # Получаем аукцион по сообщению в канале
        auction = await db.get_auction_by_channel_message(
            callback.message.chat.id, 
            callback.message.message_id
        )
        
        if not auction:
            await callback.answer("Аукцион не найден.", show_alert=True)
            return
            
        if auction['status'] != 'active':
            await callback.answer("Аукцион уже завершен.", show_alert=True)
            return
            
        if not auction['blitz_price']:
            await callback.answer("Блиц-цена не установлена для этого аукциона.", show_alert=True)
            return
        
        # Обновляем статус аукциона на "продан"
        await db.update_auction_status(auction['id'], 'sold')
        
        # Обновляем текущую цену и лидера
        await db.place_bid(
            auction['id'],
            callback.from_user.id,
            callback.from_user.username or callback.from_user.full_name,
            auction['blitz_price']
        )
        
        # Формируем кликабельную ссылку на покупателя
        if callback.from_user.username:
            buyer_display = f"@{callback.from_user.username}"
            buyer_link = f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.full_name or callback.from_user.username}</a>"
        else:
            buyer_display = callback.from_user.full_name or f"ID: {callback.from_user.id}"
            buyer_link = f"<a href='tg://user?id={callback.from_user.id}'>{buyer_display}</a>"
        
        new_text = f"<b>{auction['description']}</b>\n\n"
        new_text += f"<b>Стартовая цена:</b> {auction['start_price']} ₽\n"
        new_text += f"<b>Блиц-цена:</b> {auction['blitz_price']} ₽\n"
        new_text += "———————————————\n"
        new_text += f"<b>Текущая ставка:</b> {auction['blitz_price']} ₽\n"
        new_text += f"<b>Лидер:</b> {buyer_link}\n"
        # Безопасное форматирование даты
        end_time = auction['end_time']
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                end_time = datetime.now()
        
        new_text += f"<b>Окончание:</b> {end_time.strftime('%d.%m.%Y %H:%M')}\n\n"
        new_text += f"<b>Статус:</b> ✅ ПРОДАНО\n"
        new_text += f"<b>Покупатель:</b> {buyer_link}"
        
        # Обновляем сообщение без кнопки истории ставок
        if callback.message.caption is not None:
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=new_text,
                parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=new_text,
                parse_mode="HTML"
            )
        
        await callback.answer("Товар выкуплен по блиц-цене!")
        
        # Создаем кликабельную ссылку на продавца
        seller_link = f"<a href='tg://user?id={auction['owner_id']}'>продавцом</a>"
        
        # Уведомляем покупателя
        try:
            # Проверяем подписку пользователя перед созданием ссылки на пост
            is_subscribed = await check_user_subscription(callback.from_user.id)
            
            keyboard_buttons = []
            if is_subscribed:
                # Создаем ссылку на пост аукциона только если пользователь подписан
                # Используем username канала для ссылок
                auction_link = f"https://t.me/{CHANNEL_USERNAME_LINK}/{callback.message.message_id}"
                
                keyboard_buttons.append([InlineKeyboardButton(text="🔗 Перейти к посту", url=auction_link)])
            else:
                # Если пользователь не подписан, предлагаем подписаться
                keyboard_buttons.append([InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=f"🎉 <b>Поздравляем!</b>\n\n"
                     f"Вы выкупили лот: <b>{auction['description']}</b>\n"
                     f"Цена выкупа: <b>{auction['blitz_price']} ₽</b>\n\n"
                     f"Свяжитесь с {seller_link} для завершения сделки.",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            logging.warning(f"Failed to notify buyer: {e}")
        
        # Уведомляем продавца с кнопкой истории ставок
        try:
            # Проверяем подписку продавца перед созданием ссылки на пост
            seller_subscribed = await check_user_subscription(auction['owner_id'])
            
            # Создаем клавиатуру с кнопкой истории ставок
            keyboard_buttons = [
                [InlineKeyboardButton(text="📊 История ставок", callback_data=f"history_{auction['id']}")]
            ]
            
            # Добавляем кнопку ссылки на пост только если продавец подписан
            if seller_subscribed:
                # Используем username канала для ссылок
                auction_link = f"https://t.me/{CHANNEL_USERNAME_LINK}/{callback.message.message_id}"
                
                keyboard_buttons.append([InlineKeyboardButton(text="🔗 Перейти к посту", url=auction_link)])
            else:
                # Если продавец не подписан, предлагаем подписаться
                keyboard_buttons.append([InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")])
            
            history_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await bot.send_message(
                chat_id=auction['owner_id'],
                text=f"✅ <b>Лот продан!</b>\n\n"
                     f"Ваш лот <b>{auction['description']}</b> выкуплен за <b>{auction['blitz_price']} ₽</b>\n"
                     f"Покупатель: {buyer_link}\n\n"
                     f"Свяжитесь с покупателем для завершения сделки.",
                parse_mode="HTML",
                reply_markup=history_keyboard
            )
        except Exception as e:
            logging.warning(f"Failed to notify seller: {e}")
            
    except Exception as e:
        logging.error(f"Error processing buyout: {e}")
        await callback.answer("Ошибка при обработке выкупа. Попробуйте позже.", show_alert=True)

@dp.callback_query(F.data.startswith("bid:"))
async def handle_bid(callback: types.CallbackQuery):
    """Обработка обычных ставок"""
    try:
        bid_amount = int(callback.data.split(":")[1])

        # Проверяем подписку пользователя на канал
        is_subscribed = await check_user_subscription(callback.from_user.id)
        if not is_subscribed:
            await callback.answer(
                f"❌ Для участия в аукционе необходимо быть подписанным на канал!\n"
                f"Подпишитесь на канал: https://t.me/{CHANNEL_USERNAME_LINK}", 
                show_alert=True
            )
            return

        # Получаем аукцион по сообщению в канале
        auction = await db.get_auction_by_channel_message(
            callback.message.chat.id, 
            callback.message.message_id
        )
        
        if not auction:
            await callback.answer("Аукцион не найден.", show_alert=True)
            return

        if auction['status'] != 'active':
            await callback.answer("Аукцион уже завершен.", show_alert=True)
            return

        # Вычисляем новую цену
        new_price = auction['current_price'] + bid_amount
        
        # Проверяем, не превышает ли блиц-цену
        if auction['blitz_price'] and new_price >= auction['blitz_price']:
            new_price = auction['blitz_price']
        
        # Делаем ставку в базе данных
        success = await db.place_bid(
            auction['id'],
            callback.from_user.id,
            callback.from_user.username or callback.from_user.full_name,
            new_price
        )
        
        if not success:
            await callback.answer("Не удалось сделать ставку. Попробуйте позже.", show_alert=True)
            return
        
        # Синхронизируем ставку с внешним API (если настроен)
        try:
            bid_data = {
                "auction_id": auction['id'],
                "bidder_id": callback.from_user.id,
                "bidder_username": callback.from_user.username or callback.from_user.full_name,
                "amount": new_price,
                "bid_amount": bid_amount,
                "timestamp": datetime.now().isoformat()
            }
            # await api_integration.sync_bid_to_external(auction['id'], bid_data)  # Отключено
        except Exception as e:
            logging.warning(f"Не удалось синхронизировать ставку с внешним API: {e}")
        
        # Получаем обновленные данные аукциона
        updated_auction = await db.get_auction(auction['id'])
        
        # Форматируем новый текст
        text, keyboard = await auction_timer.format_auction_text(updated_auction, show_buttons=True)
        
        # Обновляем сообщение
        if callback.message.caption is not None:
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        await callback.answer(f"Ваша ставка {new_price} ₽ принята!")
        
    except Exception as e:
        logging.error(f"Error processing bid: {e}")
        await callback.answer("Ошибка при обработке ставки. Попробуйте позже.", show_alert=True)

# --- Обработчик истории ставок (только для продавца) ---
@dp.callback_query(F.data.startswith("history_"))
async def show_bidding_history(callback: types.CallbackQuery):
    """Показать историю ставок для аукциона (только продавцу)"""
    try:
        auction_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Проверяем, что это личное сообщение (не группа/канал)
        if callback.message.chat.type != 'private':
            await callback.answer("История ставок доступна только в личных сообщениях.", show_alert=True)
            return
        
        # Получаем информацию об аукционе
        auction = await db.get_auction(auction_id)
        if not auction:
            await callback.answer("Аукцион не найден.", show_alert=True)
            return
        
        # Проверяем, является ли пользователь продавцом
        if auction['owner_id'] != user_id:
            await callback.answer("История ставок доступна только продавцу.", show_alert=True)
            return
        
        # Получаем историю ставок
        history = await db.get_bidding_history(auction_id)
        
        if not history:
            await callback.answer("История ставок пуста.", show_alert=True)
            return
        
        text = f"📊 <b>История ставок</b>\n\n"
        text += f"<b>Лот:</b> {auction['description']}\n\n"
        
        for i, bid in enumerate(history[:10], 1):  # Показываем последние 10 ставок
            username = bid['bidder_username'] or "Аноним"
            amount = bid['amount']
            created_at = bid['created_at']
            
            # Создаем кликабельную ссылку на пользователя
            if username != "Аноним":
                user_link = f"<a href='tg://user?id={bid.get('bidder_id', '')}'>@{username}</a>"
                text += f"{i}. {user_link}: <b>{amount} ₽</b>\n"
            else:
                text += f"{i}. @{username}: <b>{amount} ₽</b>\n"
            text += f"   <i>{created_at}</i>\n\n"
        
        if len(history) > 10:
            text += f"... и еще {len(history) - 10} ставок"
        
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Error showing bidding history: {e}")
        await callback.answer("Ошибка при загрузке истории ставок.", show_alert=True)

# --- Административные функции ---
@dp.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    """Обработчик админ-панели"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    # Создаем клавиатуру админ-панели
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="💰 Управление балансом", callback_data="admin_balance"),
            InlineKeyboardButton(text="🚀 Аукционы", callback_data="admin_auctions")
        ],
        [
            InlineKeyboardButton(text="📄 Экспорт балансов", callback_data="admin_export_balances"),
            InlineKeyboardButton(text="🛒 Байт пост", callback_data="admin_buy_post")
        ],
        [
            InlineKeyboardButton(text="💾 Состояние аукционов", callback_data="admin_persistence")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_stats")
        ]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Административная панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_users")
async def admin_users_callback(callback: types.CallbackQuery):
    """Показать список пользователей"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    # Получаем последних 10 пользователей
    try:
        async with db.db_path as db_conn:
            cursor = await db_conn.execute(
                "SELECT user_id, username, full_name, balance, is_admin FROM users ORDER BY created_at DESC LIMIT 10"
            )
            users = await cursor.fetchall()
            
            text = "👥 <b>Последние пользователи:</b>\n\n"
            for user_data in users:
                admin_mark = "👑" if user_data[4] else "👤"
                username = f"@{user_data[1]}" if user_data[1] else "Без username"
                text += f"{admin_mark} ID: {user_data[0]}\n"
                text += f"   {username} | Баланс: {user_data[3]}\n\n"
            
            back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
            ])
            
            await callback.message.edit_text(text, reply_markup=back_keyboard)
            
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        await callback.answer("Ошибка при получении списка пользователей.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: types.CallbackQuery):
    """Показать общую статистику"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        # Получаем статистику
        async with db.db_path as db_conn:
            # Общее количество пользователей
            cursor = await db_conn.execute("SELECT COUNT(*) FROM users")
            total_users = (await cursor.fetchone())[0]
            
            # Активные аукционы (не истекшие по времени)
            active_auctions = await db.get_truly_active_auctions_count()
            
            # Всего аукционов
            cursor = await db_conn.execute("SELECT COUNT(*) FROM auctions")
            total_auctions = (await cursor.fetchone())[0]
            
            text = "📊 <b>Общая статистика бота:</b>\n\n"
            text += f"👥 Всего пользователей: {total_users}\n"
            text += f"🚀 Всего аукционов: {total_auctions}\n"
            text += f"🟢 Активных аукционов: {active_auctions}\n"
            
            back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
            ])
            
            await callback.message.edit_text(text, reply_markup=back_keyboard)
            
    except Exception as e:
        logging.error(f"Error getting stats: {e}")
        await callback.answer("Ошибка при получении статистики.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "admin_balance")
async def admin_balance_callback(callback: types.CallbackQuery):
    """Управление балансом пользователей"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    text = "💰 <b>Управление балансом</b>\n\n"
    text += "Для изменения баланса пользователя используйте команды:\n\n"
    text += "<code>/add_balance [user_id] [amount] [description]</code>\n"
    text += "Пример: <code>/add_balance 123456789 5 Бонус за активность</code>\n\n"
    text += "<code>/remove_balance [user_id] [amount] [description]</code>\n"
    text += "Пример: <code>/remove_balance 123456789 2 Штраф</code>\n\n"
    text += "Или используйте консольную админ-панель:\n"
    text += "<code>python admin_panel.py</code>"
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=back_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "admin_auctions")
async def admin_auctions_callback(callback: types.CallbackQuery):
    """Управление аукционами"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        # Получаем активные аукционы (не истекшие по времени)
        async with db.db_path as db_conn:
            cursor = await db_conn.execute(
                "SELECT id, owner_id, description, current_price, end_time FROM auctions WHERE status = 'active' AND end_time > ? ORDER BY created_at DESC LIMIT 5",
                (datetime.now(),)
            )
            auctions = await cursor.fetchall()
            
            text = "🚀 <b>Активные аукционы:</b>\n\n"
            if auctions:
                for auction in auctions:
                    text += f"🆔 ID: {auction[0]}\n"
                    text += f"👤 Владелец: {auction[1]}\n"
                    text += f"📝 {auction[2][:50]}...\n"
                    text += f"💰 Цена: {auction[3]} ₽\n"
                    text += f"⏰ До: {auction[4]}\n\n"
            else:
                text += "Нет активных аукционов"
            
            back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
            ])
            
            await callback.message.edit_text(text, reply_markup=back_keyboard)
            
    except Exception as e:
        logging.error(f"Error getting auctions: {e}")
        await callback.answer("Ошибка при получении аукционов.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "admin_export_balances")
async def admin_export_balances_callback(callback: types.CallbackQuery):
    """Экспорт балансов пользователей в txt файл"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        # Экспортируем балансы
        success = await balance_manager.export_balances_to_txt()
        
        if success:
            # Отправляем файл пользователю
            with open("user_balances.txt", "rb") as file:
                await bot.send_document(
                    chat_id=user_id,
                    document=file,
                    caption="📄 <b>Файл с балансами пользователей</b>\n\n"
                           "Файл содержит:\n"
                           "• Список всех пользователей с балансами\n"
                           "• Статистику по пользователям\n"
                           "• Команды для управления балансами\n\n"
                           "Для обновления файла используйте команду /export_balances"
                )
            
            await callback.answer("✅ Файл с балансами создан и отправлен!")
        else:
            await callback.answer("❌ Ошибка при создании файла с балансами.", show_alert=True)
            
    except Exception as e:
        logging.error(f"Error exporting balances: {e}")
        await callback.answer("❌ Ошибка при экспорте балансов.", show_alert=True)

@dp.callback_query(F.data == "admin_buy_post")
async def admin_buy_post_callback(callback: types.CallbackQuery, state: FSMContext):
    """Создание байт поста"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    await state.set_state(BuyPostCreation.waiting_for_photos)
    await state.update_data(media=[])
    
    await callback.message.edit_text(
        "🛒 <b>Создание байт поста</b>\n\n"
        "Отправьте до 10 фото одним разом (альбомом) или по одному. "
        "Переход к описанию произойдет автоматически.\n\n"
        "<i>Для отмены напишите «отмена»</i>"
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_persistence")
async def admin_persistence_callback(callback: types.CallbackQuery):
    """Управление системой персистентности аукционов"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        # Получаем информацию о системе персистентности
        persistence_info = auction_persistence.get_persistence_info()
        
        # Получаем количество активных аукционов
        active_count = await db.get_truly_active_auctions_count()
        
        text = "💾 <b>Система персистентности аукционов</b>\n\n"
        text += f"🟢 <b>Активных аукционов:</b> {active_count}\n"
        
        if persistence_info.get('exists'):
            text += f"📁 <b>Файл состояния:</b> Существует\n"
            text += f"📊 <b>Размер файла:</b> {persistence_info['size']} байт\n"
            text += f"🕒 <b>Последнее изменение:</b> {persistence_info['last_modified']}\n"
        else:
            text += f"📁 <b>Файл состояния:</b> Не существует\n"
        
        text += f"\n<b>Функции:</b>\n"
        text += f"• Автоматическое сохранение каждые 5 минут\n"
        text += f"• Восстановление при запуске бота\n"
        text += f"• Сохранение при корректном завершении\n"
        
        # Создаем клавиатуру
        keyboard_buttons = [
            [InlineKeyboardButton(text="💾 Принудительно сохранить", callback_data="force_save_state")],
            [InlineKeyboardButton(text="🔄 Восстановить состояние", callback_data="restore_state")],
            [InlineKeyboardButton(text="📊 Информация о файле", callback_data="persistence_info")]
        ]
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons + [
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
        ])
        
        await callback.message.edit_text(text, reply_markup=back_keyboard)
        
    except Exception as e:
        logging.error(f"Error in admin_persistence_callback: {e}")
        await callback.answer("Ошибка при получении информации о персистентности.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "force_save_state")
async def force_save_state_callback(callback: types.CallbackQuery):
    """Принудительно сохранить состояние аукционов"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        success = await auction_persistence.force_save()
        
        if success:
            await callback.answer("✅ Состояние аукционов успешно сохранено!", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при сохранении состояния.", show_alert=True)
            
    except Exception as e:
        logging.error(f"Error in force_save_state_callback: {e}")
        await callback.answer("❌ Ошибка при сохранении состояния.", show_alert=True)

@dp.callback_query(F.data == "restore_state")
async def restore_state_callback(callback: types.CallbackQuery):
    """Восстановить состояние аукционов"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        success = await auction_persistence.restore_state()
        
        if success:
            await callback.answer("✅ Состояние аукционов успешно восстановлено!", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при восстановлении состояния.", show_alert=True)
            
    except Exception as e:
        logging.error(f"Error in restore_state_callback: {e}")
        await callback.answer("❌ Ошибка при восстановлении состояния.", show_alert=True)

@dp.callback_query(F.data == "persistence_info")
async def persistence_info_callback(callback: types.CallbackQuery):
    """Показать подробную информацию о файле персистентности"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await callback.answer("У вас нет прав администратора.", show_alert=True)
        return
    
    try:
        persistence_info = auction_persistence.get_persistence_info()
        
        text = "📊 <b>Подробная информация о персистентности</b>\n\n"
        
        if persistence_info.get('exists'):
            text += f"📁 <b>Путь к файлу:</b>\n<code>{persistence_info.get('path', 'Неизвестно')}</code>\n\n"
            text += f"📊 <b>Размер файла:</b> {persistence_info['size']} байт\n"
            text += f"🕒 <b>Последнее изменение:</b> {persistence_info['last_modified']}\n"
        else:
            text += f"📁 <b>Файл состояния:</b> Не существует\n"
            text += f"<i>Файл будет создан при первом сохранении</i>\n"
        
        if persistence_info.get('error'):
            text += f"\n❌ <b>Ошибка:</b> {persistence_info['error']}"
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_persistence")]
        ])
        
        await callback.message.edit_text(text, reply_markup=back_keyboard)
        
    except Exception as e:
        logging.error(f"Error in persistence_info_callback: {e}")
        await callback.answer("Ошибка при получении информации.", show_alert=True)
    
    await callback.answer()

@dp.callback_query(F.data == "back_to_stats")
async def back_to_stats_callback(callback: types.CallbackQuery):
    """Вернуться к статистике"""
    user_id = callback.from_user.id
    user = await db.get_or_create_user(user_id)
    
    # Получаем все аукционы пользователя
    all_auctions = await db.get_user_auctions(user_id)
    
    # Получаем количество действительно активных аукционов (не истекших по времени)
    active_count = await db.get_truly_active_auctions_count(user_id)
    sold_count = len([a for a in all_auctions if a['status'] == 'sold'])
    expired_count = len([a for a in all_auctions if a['status'] == 'expired'])
    
    text = f"📊 <b>Ваша статистика:</b>\n\n"
    text += f"💰 <b>Баланс:</b> {user['balance']} публикаций\n"
    text += f"🚀 <b>Всего аукционов:</b> {len(all_auctions)}\n"
    text += f"🟢 <b>Активных:</b> {active_count}\n"
    text += f"✅ <b>Проданных:</b> {sold_count}\n"
    text += f"⏰ <b>Завершенных:</b> {expired_count}\n"
    text += f"\n👑 <b>Статус:</b> Администратор"
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=admin_keyboard)
    await callback.answer()

# --- Обработчики фильтрации описаний ---
@dp.callback_query(F.data == "confirm_filtered_description")
async def confirm_filtered_description(callback: types.CallbackQuery, state: FSMContext):
    """Подтвердить использование отфильтрованного описания для аукциона"""
    data = await state.get_data()
    filtered_description = data.get('filtered_description')
    
    if not filtered_description:
        await callback.answer("Ошибка: отфильтрованное описание не найдено.", show_alert=True)
        return
    
    # Сохраняем отфильтрованное описание
    await state.update_data(description=filtered_description)
    await state.set_state(AuctionCreation.waiting_for_price)
    
    await callback.message.edit_text(
        "Описание сохранено. Укажите стартовую цену в рублях (только число).\n\n<i>Для отмены напишите «отмена»</i>"
    )
    await callback.answer()

@dp.callback_query(F.data == "edit_description")
async def edit_description(callback: types.CallbackQuery, state: FSMContext):
    """Редактировать описание аукциона"""
    await callback.message.edit_text(
        "Введите новое описание товара (название, состояние и т.д.).\n\n"
        "<i>⚠️ Ссылки и @ упоминания будут автоматически удалены для безопасности</i>\n\n"
        "<i>Для отмены напишите «отмена»</i>"
    )
    await callback.answer()

@dp.callback_query(F.data == "confirm_filtered_buy_post_description")
async def confirm_filtered_buy_post_description(callback: types.CallbackQuery, state: FSMContext):
    """Подтвердить использование отфильтрованного описания для байт поста"""
    data = await state.get_data()
    filtered_description = data.get('filtered_description')
    
    if not filtered_description:
        await callback.answer("Ошибка: отфильтрованное описание не найдено.", show_alert=True)
        return
    
    # Сохраняем отфильтрованное описание
    await state.update_data(description=filtered_description)
    await state.set_state(BuyPostCreation.waiting_for_price)
    
    await callback.message.edit_text(
        "Описание сохранено. Укажите цену товара в рублях (только число).\n\n<i>Для отмены напишите «отмена»</i>"
    )
    await callback.answer()

@dp.callback_query(F.data == "edit_buy_post_description")
async def edit_buy_post_description(callback: types.CallbackQuery, state: FSMContext):
    """Редактировать описание байт поста"""
    await callback.message.edit_text(
        "Введите новое описание товара (название, состояние и т.д.).\n\n"
        "<i>⚠️ Ссылки и @ упоминания будут автоматически удалены для безопасности</i>\n\n"
        "<i>Для отмены напишите «отмена»</i>"
    )
    await callback.answer()

# --- Административные команды ---
@dp.message(F.text.startswith("/add_balance"))
async def add_balance_command(message: types.Message):
    """Команда для добавления баланса пользователю"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Используйте: <code>/add_balance [user_id] [amount] [description]</code>\n"
                "Пример: <code>/add_balance 123456789 5 Бонус за активность</code>"
            )
            return
        
        target_user_id = int(parts[1])
        amount = int(parts[2])
        description = " ".join(parts[3:]) if len(parts) > 3 else "Административное начисление"
        
        logging.info(f"Admin {user_id} trying to add {amount} balance to user {target_user_id}")
        
        # Проверяем, существует ли пользователь
        target_user = await db.get_or_create_user(target_user_id)
        logging.info(f"Target user found: {target_user}")
        
        success = await db.update_user_balance(
            user_id=target_user_id,
            amount=amount,
            transaction_type="admin_grant",
            description=description
        )
        
        logging.info(f"Balance update result: {success}")
        
        if success:
            # Получаем обновленную информацию о пользователе
            updated_user = await db.get_or_create_user(target_user_id)
            await message.answer(
                f"✅ Баланс пользователя {target_user_id} обновлен!\n"
                f"Добавлено: +{amount} публикаций\n"
                f"Новый баланс: {updated_user['balance']} публикаций\n"
                f"Описание: {description}"
            )
        else:
            await message.answer("❌ Не удалось обновить баланс.")
            
    except ValueError:
        await message.answer("❌ Неверный формат данных. ID и количество должны быть числами.")
    except Exception as e:
        logging.error(f"Error in add_balance command: {e}")
        await message.answer("❌ Произошла ошибка при обновлении баланса.")

@dp.message(F.text.startswith("/remove_balance"))
async def remove_balance_command(message: types.Message):
    """Команда для списания баланса у пользователя"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Используйте: <code>/remove_balance [user_id] [amount] [description]</code>\n"
                "Пример: <code>/remove_balance 123456789 2 Штраф</code>"
            )
            return
        
        target_user_id = int(parts[1])
        amount = int(parts[2])
        description = " ".join(parts[3:]) if len(parts) > 3 else "Административное списание"
        
        success = await db.update_user_balance(
            user_id=target_user_id,
            amount=-amount,  # Отрицательное значение для списания
            transaction_type="admin_penalty",
            description=description
        )
        
        if success:
            target_user = await db.get_or_create_user(target_user_id)
            await message.answer(
                f"✅ Баланс пользователя {target_user_id} обновлен!\n"
                f"Списано: -{amount} публикаций\n"
                f"Новый баланс: {target_user['balance']} публикаций\n"
                f"Описание: {description}"
            )
        else:
            await message.answer("❌ Не удалось обновить баланс.")
            
    except ValueError:
        await message.answer("❌ Неверный формат данных. ID и количество должны быть числами.")
    except Exception as e:
        logging.error(f"Error in remove_balance command: {e}")
        await message.answer("❌ Произошла ошибка при обновлении баланса.")

@dp.message(F.text == "/save_state")
async def save_state_command(message: types.Message):
    """Команда для принудительного сохранения состояния аукционов"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        success = await auction_persistence.force_save()
        
        if success:
            await message.answer("✅ Состояние аукционов успешно сохранено!")
        else:
            await message.answer("❌ Ошибка при сохранении состояния.")
            
    except Exception as e:
        logging.error(f"Error in save_state_command: {e}")
        await message.answer("❌ Ошибка при сохранении состояния.")

@dp.message(F.text == "/restore_state")
async def restore_state_command(message: types.Message):
    """Команда для восстановления состояния аукционов"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        success = await auction_persistence.restore_state()
        
        if success:
            await message.answer("✅ Состояние аукционов успешно восстановлено!")
        else:
            await message.answer("❌ Ошибка при восстановлении состояния.")
            
    except Exception as e:
        logging.error(f"Error in restore_state_command: {e}")
        await message.answer("❌ Ошибка при восстановлении состояния.")

@dp.message(F.text == "/persistence_info")
async def persistence_info_command(message: types.Message):
    """Команда для получения информации о системе персистентности"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        persistence_info = auction_persistence.get_persistence_info()
        active_count = await db.get_truly_active_auctions_count()
        
        text = "💾 <b>Информация о системе персистентности</b>\n\n"
        text += f"🟢 <b>Активных аукционов:</b> {active_count}\n"
        
        if persistence_info.get('exists'):
            text += f"📁 <b>Файл состояния:</b> Существует\n"
            text += f"📊 <b>Размер файла:</b> {persistence_info['size']} байт\n"
            text += f"🕒 <b>Последнее изменение:</b> {persistence_info['last_modified']}\n"
            text += f"📁 <b>Путь:</b> <code>{persistence_info.get('path', 'Неизвестно')}</code>\n"
        else:
            text += f"📁 <b>Файл состояния:</b> Не существует\n"
        
        if persistence_info.get('error'):
            text += f"\n❌ <b>Ошибка:</b> {persistence_info['error']}"
        
        await message.answer(text)
        
    except Exception as e:
        logging.error(f"Error in persistence_info_command: {e}")
        await message.answer("❌ Ошибка при получении информации.")

@dp.message(F.text == "/export_balances")
async def export_balances_command(message: types.Message):
    """Команда для экспорта балансов в txt файл"""
    user_id = message.from_user.id
    user = await db.get_or_create_user(user_id)
    
    if not user['is_admin']:
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        # Экспортируем балансы
        success = await balance_manager.export_balances_to_txt()
        
        if success:
            # Отправляем файл пользователю
            with open("user_balances.txt", "rb") as file:
                await bot.send_document(
                    chat_id=user_id,
                    document=file,
                    caption="📄 <b>Файл с балансами пользователей</b>\n\n"
                           "Файл содержит:\n"
                           "• Список всех пользователей с балансами\n"
                           "• Статистику по пользователям\n"
                           "• Команды для управления балансами\n\n"
                           "Для обновления файла используйте команду /export_balances"
                )
            
            await message.answer("✅ Файл с балансами создан и отправлен!")
        else:
            await message.answer("❌ Ошибка при создании файла с балансами.")
            
    except Exception as e:
        logging.error(f"Error exporting balances: {e}")
        await message.answer("❌ Ошибка при экспорте балансов.")

# --- Настройка команд бота ---
async def set_bot_commands():
    """Устанавливает команды бота в меню"""
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
    ]
    
    await bot.set_my_commands(commands)
    logging.info("Bot commands set successfully")

# --- Обработка уведомлений от сервера платежей ---
# async def process_payment_notifications():
#     """Обрабатывает уведомления о платежах от сервера (отключено)"""
#     pass

# --- Запуск бота ---
async def main():
    payment_task = None  # Initialize payment_task variable
    
    try:
        logging.info("Bot is starting...")
        
        # Инициализируем базу данных
        await db.init_db()
        logging.info("Database initialized")
        
        # Настраиваем команды бота
        await set_bot_commands()
        logging.info("Bot commands configured")
        
        # Запускаем систему персистентности аукционов
        await auction_persistence.start()
        logging.info("Auction persistence system started")
        
        # Запускаем таймер аукционов
        await auction_timer.start()
        logging.info("Auction timer started")
        
        # Запускаем обработку уведомлений о платежах (отключено)
        # payment_task = asyncio.create_task(process_payment_notifications())
        # logging.info("Payment notification processor started")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
    finally:
        # Останавливаем таймер
        await auction_timer.stop()
        logging.info("Auction timer stopped")
        
        # Останавливаем систему персистентности
        await auction_persistence.stop()
        logging.info("Auction persistence system stopped")
        
        # Отменяем задачу обработки уведомлений
        if payment_task is not None:
            payment_task.cancel()
            logging.info("Payment notification processor stopped")
        
        await bot.session.close()
        logging.info("Bot has been stopped.")

if __name__ == "__main__":
    asyncio.run(main())
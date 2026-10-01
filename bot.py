import os
import asyncio
import logging
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import yfinance as yf
from asgiref.sync import sync_to_async
from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from trackers.models import Ticker
from alerts.models import PriceAlert

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Finite State Machine
class AlertForm(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_condition = State()
    waiting_for_price = State()
    waiting_for_interval = State()


# --- Keyboards  ---
def get_main_reply_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Новий алерт"),
                KeyboardButton(text="📋 Мої алерти")
            ]
        ],
        resize_keyboard=True
    )


def get_action_navigation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Новий алерт", callback_data="nav_newalert"),
            InlineKeyboardButton(text="📋 Мої алерти", callback_data="nav_myalerts")
        ]
    ])


def get_condition_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Більше", callback_data="cond_ABOVE"),
            InlineKeyboardButton(text="📉 Менше", callback_data="cond_BELOW")
        ]
    ])


def get_interval_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱ 1 хв", callback_data="int_1m"),
            InlineKeyboardButton(text="⏰ 1 год", callback_data="int_1h"),
            InlineKeyboardButton(text="📅 1 день", callback_data="int_1d")
        ]
    ])


# Currency function
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'UAH': '₴',
    'PLN': 'zł',
    'CAD': 'CA$',
    'JPY': '¥',
}


def get_currency_symbol(info_or_dict) -> str:
    if isinstance(info_or_dict, dict):
        currency_code = info_or_dict.get('currency', 'USD')
    else:
        currency_code = getattr(info_or_dict, 'currency', 'USD')
    return CURRENCY_SYMBOLS.get(currency_code, f" {currency_code}")


# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вітаю! 👋 Я бот для відстеження цін на акції та інші активи.\n\n"
        "Оберіть дію за допомогою кнопок нижче або введіть команду:",
        reply_markup=get_main_reply_kb()
    )


@dp.message(Command("newalert"))
@dp.message(F.text == "➕ Новий алерт")
async def cmd_start_alert(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вітаю! 👋 Введіть символ тікера, за яким бажаєте стежити:",
        parse_mode="HTML")
    await state.set_state(AlertForm.waiting_for_ticker)

@dp.callback_query(F.data.startswith("del_"))
async def process_delete_alert(callback: CallbackQuery):
    alert_id = int(callback.data.split("_")[1])
    chat_id = str(callback.message.chat.id)

    @sync_to_async
    def delete_alert():
        deleted_count, _ = PriceAlert.objects.filter(id=alert_id, telegram_chat_id=chat_id).delete()
        return deleted_count > 0

    success = await delete_alert()

    if success:
        await callback.answer("🗑 Алерт успішно видалено!", show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("❌ Не вдалося видалити алерт або його не існує.", show_alert=True)



@dp.message(AlertForm.waiting_for_ticker)
async def process_ticker(message: Message, state: FSMContext):
    symbol = message.text.strip().upper()

    try:
        data = yf.Ticker(symbol)
        info = data.fast_info
        price = info.get('lastPrice')
        curr_symbol = get_currency_symbol(info)
    except Exception:
        price = None

    if not price:
        await message.answer(f"❌ Тікер <b>{symbol}</b> не знайдено або дані недоступні. Спробуйте ще раз:",
                             parse_mode="HTML")
        return

    await state.update_data(ticker=symbol, current_price=price, currency_symbol=curr_symbol)

    await message.answer(
        f"📊 Актуальна ціна: <b>{symbol}</b> <b>{curr_symbol}{price:.2f}</b>\n\nОберіть умову для алерта:",
        reply_markup=get_condition_kb(),
        parse_mode="HTML"
    )
    await state.set_state(AlertForm.waiting_for_condition)


@dp.callback_query(AlertForm.waiting_for_condition, F.data.startswith("cond_"))
async def process_condition(callback: CallbackQuery, state: FSMContext):
    condition = callback.data.split("_")[1]
    await state.update_data(condition=condition)

    cond_str = "вище" if condition == "ABOVE" else "нижче"
    await callback.message.edit_text(
        f"Введіть цільову ціну. Сповіщення надійде коли ціна стане {cond_str}:")
    await state.set_state(AlertForm.waiting_for_price)


@dp.message(AlertForm.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    try:
        target_price = float(message.text.replace(",", "."))
        if target_price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Будь ласка, введіть коректне число (наприклад: 250.5):")
        return

    await state.update_data(target_price=target_price)
    await message.answer("Оберіть частоту перевірки ціни:", reply_markup=get_interval_kb())
    await state.set_state(AlertForm.waiting_for_interval)


@dp.callback_query(F.data == "nav_newalert")
async def nav_new_alert_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "Введіть символ тікера, за яким бажаєте стежити:",
        parse_mode="HTML"
    )
    await state.set_state(AlertForm.waiting_for_ticker)

@dp.callback_query(F.data == "nav_myalerts")
async def nav_my_alerts_callback(callback: CallbackQuery):
    await callback.answer()
    await cmd_my_alerts(callback.message)

@dp.callback_query(AlertForm.waiting_for_interval, F.data.startswith("int_"))
async def process_interval(callback: CallbackQuery, state: FSMContext):
    interval = callback.data.split("_")[1]
    user_data = await state.get_data()

    chat_id = str(callback.message.chat.id)
    symbol = user_data['ticker']
    condition = user_data['condition']
    target_price = user_data['target_price']
    curr_symbol = user_data.get('currency_symbol', '$')

    @sync_to_async
    def save_alert():
        ticker_obj, _ = Ticker.objects.get_or_create(symbol=symbol, defaults={'name': symbol, 'is_active': True})
        if not ticker_obj.is_active:
            ticker_obj.is_active = True
            ticker_obj.save()

        return PriceAlert.objects.create(
            ticker=ticker_obj,
            target_price=target_price,
            condition=condition,
            check_interval=interval,
            telegram_chat_id=chat_id,
            is_triggered=False
        )

    await save_alert()
    await state.clear()

    interval_labels = {'1m': '1 хв', '1h': '1 год', '1d': '1 день'}
    cond_str = "вище" if condition == "ABOVE" else "нижча"

    await callback.message.edit_text(
        f"✅ <b>Алерт успішно створено!</b>\n\n"
        f"📈 Тікер: <b>{symbol}</b>\n"
        f"🎯 Ціль: <b>{cond_str} за {curr_symbol}{target_price:.2f}</b>\n"
        f"⏱ Частота: <b>{interval_labels.get(interval)}</b>\n\n"
        f"Ми сповістимо вас, як тільки ціна досягне цілі!",
        parse_mode="HTML",
        reply_markup=get_action_navigation_kb()
    )


@dp.message(Command("myalerts"))
@dp.message(F.text == "📋 Мої алерти")
async def cmd_my_alerts(message: Message):
    chat_id = str(message.chat.id)

    @sync_to_async
    def get_user_alerts():
        return list(
            PriceAlert.objects.filter(telegram_chat_id=chat_id, is_triggered=False).select_related('ticker'))

    try:
        alerts = await get_user_alerts()
    except Exception as e:
        await message.answer("❌ Сталася помилка при отриманні списку алертів.")
        print(f"Error fetching alerts: {e}")
        return

    if not alerts:
        await message.answer("📭 У вас немає активних алертів.")
        return

    def fetch_alert_currencies(alert_list):
        result = []
        for alert in alert_list:
            try:
                data = yf.Ticker(alert.ticker.symbol)
                curr_symbol = get_currency_symbol(data.fast_info)
            except Exception:
                curr_symbol = '$'
            result.append((alert, curr_symbol))
        return result

    alerts_with_currencies = await asyncio.to_thread(fetch_alert_currencies, alerts)

    interval_labels = {'1m': '1 хв', '1h': '1 год', '1d': '1 день'}

    text = f"📋 <b>Ваші активні алерти:</b>\n\n"
    for i, (alert, curr_symbol) in enumerate(alerts_with_currencies, 1):
        cond_str = "вище" if alert.condition == "ABOVE" else "нижче"
        interval_str = interval_labels.get(alert.check_interval, alert.check_interval)

        text = (
            f"{i}. <b>{alert.ticker.symbol}</b>\n"
            f"   🎯 Ціль: <b>{cond_str} за {curr_symbol}{alert.target_price:.2f}</b>\n"
            f"   ⏱ Інтервал: <b>{interval_str}</b>\n\n"
        )
        delete_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Видалити алерт", callback_data=f"del_{alert.id}")]
        ])

        await message.answer(text, parse_mode="HTML", reply_markup=delete_kb)

    await message.answer("Оберіть наступну дію:", reply_markup=get_action_navigation_kb())


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

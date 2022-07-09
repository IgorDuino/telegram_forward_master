from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from models import Rule, Filter
from typing import List


def rules_menu(rules: List[Rule]):
    keyboard = InlineKeyboardMarkup()
    for i, rule in enumerate(rules):
        status = "🟢" if rule.is_enabled else "🔴"
        keyboard.add(
            InlineKeyboardButton(text=f"{status} {i+1}. {rule.name}", callback_data=f"rule_{rule.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data="main-menu"))
    return keyboard


def rule_menu(rule: Rule):
    keyboard = InlineKeyboardMarkup()

    if rule.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable-rule_{rule.id}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable-rule_{rule.id}"))

    keyboard.add(
        InlineKeyboardButton(text="Фильтры 🕳️", callback_data=f"filters_{rule.id}"))

    keyboard.add(
        InlineKeyboardButton(text="Удалить правило 🗑", callback_data=f"delete-rule_{rule.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data="all-rules"))
    return keyboard


def filters_menu(rule: Rule):
    keyboard = InlineKeyboardMarkup()
    for i, filter in enumerate(rule.filters):
        title = f"{filter.replace_word} -> {filter.to_replace_word}"
        status = "🟢" if filter.is_enabled else "🔴"

        keyboard.add(
            InlineKeyboardButton(text=f"{status} {i+1}. {title}", callback_data=f"filter_{filter.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Добавить фильтр 📝", callback_data=f"add-filter_{rule.id}"))
    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"rule_{rule.id}"))
    return keyboard


def filter_menu(filter: Filter):
    keyboard = InlineKeyboardMarkup()
    if filter.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable-filter_{filter.id}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable-filter_{filter.id}"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить фильтр 🗑", callback_data=f"delete-filter_{filter.id}"))
    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"rule_{filter.rule_id}"))
    return keyboard


def main_menu(state):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Все правила", callback_data="all-rules"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить правило", callback_data="add-rule"))
    if state:
        keyboard.add(
            InlineKeyboardButton(text="Отключить бота 🔴", callback_data="stop"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить бота 🟢", callback_data="start"))

    return keyboard

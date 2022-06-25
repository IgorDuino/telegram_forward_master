from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.models import Rule, Filter
from typing import List


def rules_menu(rules: List[Rule]):
    keyboard = InlineKeyboardMarkup()
    for i, rule in enumerate(rules):
        keyboard.add(
            InlineKeyboardButton(text=f"{i}: {rule.name}", callback_data=f"rule_{rule.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data="main_menu"))
    return keyboard


def rule_menu(rule: Rule):
    keyboard = InlineKeyboardMarkup()

    if rule.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable_rule_{rule.id}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable_rule_{rule.id}"))

    keyboard.add(
        InlineKeyboardButton(text="Фильтры 🕳️", callback_data=f"filters_{rule.Wid}"))

    keyboard.add(
        InlineKeyboardButton(text="Удалить правило 🗑", callback_data=f"delete_rule_{rule.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data="main_menu"))
    return keyboard


def filters_menu(rule: Rule):
    keyboard = InlineKeyboardMarkup()
    for i, filter in enumerate(rule.filters):
        keyboard.add(
            InlineKeyboardButton(text=f"{i}: {filter.name}", callback_data=f"filter_{filter.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"rule_{rule.id}"))
    return keyboard


def filter_menu(filter: Filter):
    keyboard = InlineKeyboardMarkup()
    if filter.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable_filter_{filter.id}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable_filter_{filter.id}"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить фильтр 🗑", callback_data=f"delete_filter_{filter.id}"))
    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"rule_{filter.rule_id}"))
    return keyboard


def main_menu(state):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Все правила", callback_data="all_rules"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить правило", callback_data="add_rule"))
    if state:
        keyboard.add(
            InlineKeyboardButton(text="Отключить бота 🔴", callback_data="stop"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить бота 🟢", callback_data="start"))

    return keyboard

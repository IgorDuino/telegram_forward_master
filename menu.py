from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from models import Rule, Filter
from typing import List, Union


def main_menu(state):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Все равила", callback_data="all-rules"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить правило", callback_data="add-rule"))

    keyboard.add(
        InlineKeyboardButton(text="Общие фильтры", callback_data="filters_-1"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить общий фильтр", callback_data="add-filter_-1"))

    if state:
        keyboard.add(
            InlineKeyboardButton(text="Отключить бота 🔴", callback_data="disable-bot"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить бота 🟢", callback_data="enable-bot"))

    return keyboard


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
        InlineKeyboardButton(text="Фильтры", callback_data=f"filters_{rule.id}"))

    keyboard.add(
        InlineKeyboardButton(text="Удалить правило", callback_data=f"delete-rule_{rule.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data="all-rules"))
    return keyboard


def add_filter_trigger_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Слово или фразу", callback_data="add-filter-trigger_phrase"))
    keyboard.add(
        InlineKeyboardButton(text="Любой номер телефона", callback_data="add-filter-trigger_phone"))
    keyboard.add(
        InlineKeyboardButton(text="Любую почту", callback_data="add-filter-trigger_mail"))
    keyboard.add(
        InlineKeyboardButton(text="Telegram ник", callback_data="add-filter-trigger_telegram"))
    keyboard.add(
        InlineKeyboardButton(text="Любую ссылку", callback_data="add-filter-trigger_link"))
    keyboard.add(
        InlineKeyboardButton(text="Отмена 🚫", callback_data="all-rules_remove-temp-filter"))

    return keyboard


def add_filter_action_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Заменить на что-либо", callback_data="add-filter-action_phrase"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить триггер", callback_data="add-filter-action_delete"))
    keyboard.add(
        InlineKeyboardButton(text="Не пересылать сообщение", callback_data="add-filter-action_cancel-forward"))
    keyboard.add(
        InlineKeyboardButton(text="Отключить правило", callback_data="add-filter-action_disable-rule"))

    keyboard.add(
        InlineKeyboardButton(text="Отмена 🚫", callback_data="all-rules_remove-temp-filter"))

    return keyboard


def filters_menu(rule_id, filters: List[Filter]):
    keyboard = InlineKeyboardMarkup()

    for i, filter in enumerate(filters):
        trigger_replace_dict = {
            "telegram": "Telegram ник",
            "phone": "Телефон",
            "mail": "Эл. почта",
            "link": "Ссылка"
        }

        trigger = trigger_replace_dict.get(
            filter.replace_word, filter.replace_word)

        action_replace_dict = {
            "": "Удалить триггер",
            "disable-rule": "Отключение правила",
            "cancel-forward": "Отмена пересылки"}

        action = action_replace_dict.get(
            filter.to_replace_word, filter.to_replace_word)

        title = f"{trigger} → {action}"
        status = "🟢" if filter.is_enabled else "🔴"

        keyboard.add(
            InlineKeyboardButton(text=f"{status} {i+1}. {title}", callback_data=f"filter_{filter.id}"))

    keyboard.add(InlineKeyboardButton(
        text="Добавить фильтр", callback_data=f"add-filter_{rule_id}"))
    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"rule_{rule_id}"))

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

    if filter.rule_id == -1:
        keyboard.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data="all-rules"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data=f"rule_{filter.rule_id}"))

    return keyboard

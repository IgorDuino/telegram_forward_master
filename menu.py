from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from models import Rule, Filter, Folder
from typing import List, Union
from random import randint


def main_menu(state):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Правила и папки", callback_data=f"all-rules@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить правило", callback_data=f"add-rule-type@{randint(1, 100)}@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить папку", callback_data=f"add-folder@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Общие фильтры", callback_data=f"filters_general@{randint(1, 100)}@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Добавить общий фильтр", callback_data=f"add-filter_general@{randint(1, 100)}@{randint(1, 100)}"))
    if state:
        keyboard.add(
            InlineKeyboardButton(text="Отключить бота 🔴", callback_data=f"disable-bot@{randint(1, 100)}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить бота 🟢", callback_data=f"enable-bot@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Перезапуск системы", callback_data=f"docker-restart@{randint(1, 100)}"))

    return keyboard


def add_rule_type_menu(n: int):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="От человека" if n == 1 else "Человеку", callback_data=f"add-rule-user_{n}@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Из чата" if n == 1 else "В чат", callback_data=f"add-rule-chat_{n}@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Отмена 🚫", callback_data=f"all-rules_remove-temp-rule@{randint(1, 100)}"))

    return keyboard


def rules_and_folders(elements: List[Union[Rule, Folder]]):
    keyboard = InlineKeyboardMarkup()

    for i, element in enumerate(elements):
        if type(element) == Rule:
            rule = element
            status = "🟢" if rule.is_enabled else "🔴"
            keyboard.add(
                InlineKeyboardButton(text=f"{status}  {rule.name}", callback_data=f"rule_{rule.id}@{randint(1, 100)}"))

        elif type(element) == Folder:
            folder = element
            status = "🟢" if folder.is_enabled else "🔴"
            keyboard.add(
                InlineKeyboardButton(text=f"📁 {status}  {folder.name}", callback_data=f"folder_{folder.id}@{randint(1, 100)}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"main-menu@{randint(1, 100)}"))

    return keyboard


def rule_menu(rule: Rule):
    keyboard = InlineKeyboardMarkup()

    if rule.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable-rule_{rule.id}@{randint(1, 100)}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable-rule_{rule.id}@{randint(1, 100)}"))

    keyboard.add(
        InlineKeyboardButton(text="Фильтры", callback_data=f"filters_{rule.id}@{randint(1, 100)}"))

    keyboard.add(
        InlineKeyboardButton(text="Удалить правило", callback_data=f"delete-rule_{rule.id}@{randint(1, 100)}"))

    if rule.folder_id:
        keyboard.add(
            InlineKeyboardButton(text="Убрать из папки", callback_data=f"remove-from-folder_{rule.id}@{randint(1, 100)}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"all-rules@{randint(1, 100)}"))
    return keyboard


def folder_menu(folder: Folder, rules):
    keyboard = InlineKeyboardMarkup()

    if folder.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить", callback_data=f"disable-folder_{folder.id}@{randint(1, 100)}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить ", callback_data=f"enable-folder_{folder.id}@{randint(1, 100)}"))

    for i, rule in enumerate(rules):
        status = "🟢" if rule.is_enabled else "🔴"
        keyboard.add(
            InlineKeyboardButton(text=f"{status}  {rule.name}", callback_data=f"rule_{rule.id}@{randint(1, 100)}"))

    keyboard.add(
        InlineKeyboardButton(text="Удалить папку", callback_data=f"delete-folder_{folder.id}@{randint(1, 100)}"))

    keyboard.add(InlineKeyboardButton(
        text="Назад 🔙", callback_data=f"all-rules@{randint(1, 100)}"))
    return keyboard

def add_filter_trigger_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Слово или фразу", callback_data=f"add-filter-trigger_phrase@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Часть слова", callback_data=f"add-filter-trigger_part@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Любой номер телефона", callback_data=f"add-filter-trigger_phone@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Любую почту", callback_data=f"add-filter-trigger_mail@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Telegram ник", callback_data=f"add-filter-trigger_telegram@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Любую ссылку", callback_data=f"add-filter-trigger_link@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Номер карты", callback_data=f"add-filter-trigger_card@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Отмена 🚫", callback_data=f"all-rules_remove-temp-filter@{randint(1, 100)}"))

    return keyboard


def add_filter_action_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text="Заменить триггер", callback_data=f"add-filter-action_phrase@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить триггер", callback_data=f"add-filter-action_delete@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Не пересылать сообщение", callback_data=f"add-filter-action_cancel-forward@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Отключить правило", callback_data=f"add-filter-action_disable-rule@{randint(1, 100)}"))

    keyboard.add(
        InlineKeyboardButton(text="Отмена 🚫", callback_data=f"all-rules_remove-temp-filter@{randint(1, 100)}"))

    return keyboard


def filters_menu(rule_id, filters: List[Filter]):
    keyboard = InlineKeyboardMarkup()

    for i, filter in enumerate(filters):
        status = "🟢" if filter.is_enabled else "🔴"

        keyboard.add(
            InlineKeyboardButton(text=f"{status} {i+1}. {filter.name}", callback_data=f"filter_{filter.id}@{randint(1, 100)}"))

    if rule_id == -1:
        keyboard.add(InlineKeyboardButton(
            text="Добавить фильтр", callback_data=f"add-filter_general@{randint(1, 100)}"))
    else:
        keyboard.add(InlineKeyboardButton(
            text="Добавить фильтр", callback_data=f"add-filter_{rule_id}@{randint(1, 100)}"))

    if rule_id == -1:
        keyboard.add(InlineKeyboardButton(
            text="Назад 🔙", callback_data=f"main-menu@{randint(1, 100)}"))
    else:
        keyboard.add(InlineKeyboardButton(
            text="Назад 🔙", callback_data=f"rule_{rule_id}@{randint(1, 100)}"))

    return keyboard


def filter_menu(filter: Filter):
    keyboard = InlineKeyboardMarkup()

    if filter.is_enabled:
        keyboard.add(
            InlineKeyboardButton(text="Отключить 🔴", callback_data=f"disable-filter_{filter.id}@{randint(1, 100)}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Включить 🟢", callback_data=f"enable-filter_{filter.id}@{randint(1, 100)}"))
    keyboard.add(
        InlineKeyboardButton(text="Удалить фильтр", callback_data=f"delete-filter_{filter.id}@{randint(1, 100)}"))

    if filter.is_general:
        keyboard.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data=f"all-rules@{randint(1, 100)}"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data=f"rule_{filter.rule_id}@{randint(1, 100)}"))

    return keyboard

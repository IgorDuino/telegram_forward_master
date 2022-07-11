from decouple import config
from typing import List, Tuple
import logging
import re
import os

import pyrogram
from pyrogram import Client, filters
import pyrogram.types

import telebot
from menu import rule_menu

from db_session import global_init, create_session
from models import Rule, Filter


logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s [%(levelname)s] %(name)s :%(message)s')
logger = logging.getLogger(__name__)

api_token = config("BOT_API", cast=str)

bot = telebot.TeleBot(api_token)


def send_disable_rule_notification_to_telegram(rule, reason):
    telegram_id = config('TELEGRAM_ID', cast=str)
    bot.send_message(telegram_id,
                     f"Правило [{rule.id}] {rule.name} отключено из-за фильтра на слово {reason}", reply_markup=rule_menu(rule))


def disable_rule(rule: Rule):
    session = create_session()
    real_rule: Rule = session.query(Rule).filter(Rule.id == rule.id).first()
    real_rule.is_enabled = False
    session.commit()


def case_insensitive_replace(text: str, replace_word: str, to_replace_word: str) -> str:
    return re.compile(re.escape(replace_word), re.IGNORECASE).sub(to_replace_word, text)


async def forward_message(app: Client, message: pyrogram.types.Message, target_chat: str, rule: Rule) -> bool:
    session = create_session()
    filters = session.query(Filter).filter(Filter.rule_id == rule.id).all()

    for filter in filters:
        if not filter.is_enabled:
            continue

        if len(re.compile(re.escape(filter.replace_word), re.IGNORECASE).findall(message.text)) > 0:
            if filter.to_replace_word == "ОТКЛЮЧИТЬ":
                disable_rule(rule)
                send_disable_rule_notification_to_telegram(
                    rule, filter.replace_word)
                return False
            if filter.to_replace_word == "ОТМЕНИТЬ":
                return False

        try:
            message.text = case_insensitive_replace(
                message.text, filter.replace_word, filter.to_replace_word)
        except:
            pass

        try:
            message.caption = case_insensitive_replace(
                message.caption, filter.replace_word, filter.to_replace_word)
        except:
            pass

    await message.copy(
        int(target_chat),
    )

    return True


def is_almsost_digit(text: str) -> bool:
    alphabet = "-+0123456789"
    return len(set(text) | set(alphabet)) == len(alphabet)


def get_rules_by_first_user(user_tg_id: str, user_contact: str) -> Tuple[List[Rule], List[Rule]]:
    session = create_session()

    # get rules where our user is first
    # by user_tg_id
    first_rules = session.query(Rule).filter(
        Rule.first_user_tg_id == user_tg_id).all()
    # and by user_contact
    first_rules += session.query(Rule).filter(
        Rule.first_user_tg_id == user_contact).all()

    # get rules where our user is second
    # by user_tg_id
    second_rules = session.query(Rule).filter(
        Rule.second_user_tg_id == user_tg_id).all()
    # and by user_contact
    second_rules += session.query(Rule).filter(
        Rule.second_user_tg_id == user_contact).all()

    return [first_rules, second_rules]


async def get_chat_id_by_contact_name(app: Client, contact_name: str) -> str:
    all_chats: List[pyrogram.types.User] = await app.get_contacts()
    for chat in all_chats:
        try:
            first_name = chat.first_name.lower()
            last_name = chat.last_name.lower()

            a = [first_name, last_name, f"{first_name} {last_name}"]

            if contact_name.lower() in a:
                return chat.id
        except:
            continue


async def replace_chat_id_in_database(app: Client, rule, contact_name: str, number: int):
    chat_id = await get_chat_id_by_contact_name(app, contact_name)
    if chat_id is None:
        return False

    session = create_session()
    real_rule: Rule = session.query(Rule).filter(Rule.id == rule.id).first()

    if number == 1:
        real_rule.first_user_tg_id = chat_id
    elif number == 2:
        real_rule.second_user_tg_id = chat_id
    else:
        return False

    session.commit()
    return True


def main():
    api_id = config('API_ID', cast=int)
    api_hash = config('API_HASH', cast=str)
    phone_number = config('PHONE_NUMBER', cast=str)
    account_name = config('ACCOUNT_NAME', cast=str)

    # check if the sessinon file exists
    if not os.path.exists(f"{account_name}.session"):
        logger.critical(f"{account_name}.session not found")
        # TODO: maybe send a message to the admin from the bot
        return

    app = Client(account_name, phone_number=phone_number,
                 api_hash=api_hash, api_id=api_id)

    @app.on_message(filters.private)
    async def main_handler(client, message: pyrogram.types.messages_and_media.Message):
        from_id = str(message.from_user.id)
        # TODO: add sending by account name
        from_user_contact = "message.contact.first_name"

        target_chat = None

        first_rules, second_rules = get_rules_by_first_user(
            from_id, from_user_contact)

        for rule in first_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_SECOND_TO_FIRST:
                continue

            target_chat = rule.second_user_tg_id
            if not is_almsost_digit(target_chat):
                target_chat = await replace_chat_id_in_database(app, rule, target_chat, 2)

            await forward_message(app, message, target_chat, rule)

        for rule in second_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_FIRST_TO_SECOND:
                continue

            target_chat = rule.first_user_tg_id
            if not is_almsost_digit(target_chat):
                target_chat = await replace_chat_id_in_database(app, rule, target_chat, 1)

            await forward_message(app, message, target_chat, rule)

    app.run()


if __name__ == '__main__':
    db_name = config('POSTGRES_DB', cast=str)
    db_user = config('POSTGRES_USER', cast=str)
    db_password = config('POSTGRES_PASSWORD', cast=str)
    db_host = config('DB_HOST', cast=str)
    db_port = config('POSTGRES_PORT', cast=int)

    global_init(db_user, db_password, db_host, db_port, db_name)
    logger.info("DB initialized")
    main()
    logger.info("Main loop finished")
    logger.info("Exiting")

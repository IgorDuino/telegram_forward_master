from decouple import config
from typing import List, Literal, Tuple
import logging
import re
import os

import pyrogram

from pyrogram import Client, filters, enums
import pyrogram.types

import telebot
from menu import rule_menu

from db_session import global_init, create_session
from models import Rule, Filter, User


logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s [%(levelname)s] %(name)s :%(message)s')
logger = logging.getLogger(__name__)

api_token = config("BOT_API", cast=str)

bot = telebot.TeleBot(api_token)


def send_disable_rule_notification_to_telegram(rule, reason):
    bot.send_message(telegram_id,
                     f"Правило [{rule.id}] {rule.name} отключено из-за фильтра на слово {reason}", reply_markup=rule_menu(rule))


def disable_rule(rule: Rule):
    session = create_session()
    real_rule: Rule = session.query(Rule).filter(Rule.id == rule.id).first()
    real_rule.is_enabled = False
    session.commit()
    session.close()


def apply_filter(trigger, action, text: str):
    status: Literal['not applied', 'cancel-forward',
                    'disable-rule', 'replaced'] = 'not applied'

    regexes = {
        "mail": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        "telegram": r"\B@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*",
        "phone": r"((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}",
        "link": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "card": r"(?<!\d)\d{16}(?!\d)|(?<!\d[ _-])(?<!\d)\d{4}(?:[_ -]\d{4}){3}(?![_ -]?\d)"
    }

    regex = regexes.get(trigger, trigger)

    if list(re.finditer(regex, text, re.IGNORECASE)):
        if action in ['cancel-forward', 'disable-rule']:
            status = action
        else:
            status = 'replaced'
            text = re.sub(regex, action, text, flags=re.IGNORECASE)

    return (status, text)


async def forward_message(app: Client, message: pyrogram.types.Message, target_chat: str, rule: Rule) -> bool:
    print(f"Forwarding message {message.text} to {target_chat}")

    # get filters for this rule
    session = create_session()
    filters: List[Filter] = session.query(
        Filter).filter(Filter.rule_id == rule.id).all()
    filters += session.query(Filter).filter(Filter.is_general == True).all()
    session.close()

    # if messahe is reply
    if message.reply_to_message:
        reply_message = message.reply_to_message

        if reply_message.text:
            datetime_srt = f'{reply_message.date: %d.%m %H:%M}'

            reply_message.text = f"[__In reply from {datetime_srt}__]\n" + \
                reply_message.text
            print(reply_message.text)

        await reply_message.copy(
            chat_id=target_chat,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    for filter in filters:
        if not filter.is_enabled:
            continue

        # apply filter to message text
        if message.text:
            applying_filter_status, applying_filter_text = apply_filter(
                filter.replace_word, filter.to_replace_word, message.text)

            if applying_filter_status == 'disable-rule':
                disable_rule(rule)
                send_disable_rule_notification_to_telegram(
                    rule, filter.replace_word)
                return True

            elif applying_filter_status == 'cancel-forward':
                return True

            elif applying_filter_status == 'replaced':
                message.text = applying_filter_text

        # apply filter to message caption
        if message.caption:
            applying_filter_status, applying_filter_text = apply_filter(
                filter.replace_word, filter.to_replace_word, message.caption)

            if applying_filter_status == 'disable-rule':
                disable_rule(rule)
                send_disable_rule_notification_to_telegram(
                    rule, filter.replace_word)
                return True

            elif applying_filter_status == 'cancel-forward':
                return True

            elif applying_filter_status == 'replaced':
                message.caption = applying_filter_text

    await message.copy(
        int(target_chat),
    )

    return True


def is_almsost_digit(text: str) -> bool:
    alphabet = "-+0123456789"
    return len(set(text) | set(alphabet)) == len(alphabet)


async def get_rules_by_first_user(app: Client, user_tg_id: str, user_contact: str) -> Tuple[List[Rule], List[Rule]]:
    session = create_session()

    # get rules where our user is first
    first_rules = session.query(Rule).filter(
        Rule.first_user_tg_id == user_contact).all()

    for rule in first_rules:
        await replace_chat_id_in_database(app, rule, user_contact, 1)

    first_rules = session.query(Rule).filter(
        Rule.first_user_tg_id == user_tg_id).all()

    # get rules where our user is second
    second_rules = session.query(Rule).filter(
        Rule.second_user_tg_id == user_contact).all()

    for rule in second_rules:
        await replace_chat_id_in_database(app, rule, user_contact, 2)

    second_rules = session.query(Rule).filter(
        Rule.second_user_tg_id == user_tg_id).all()

    session.close()
    return first_rules, second_rules


async def get_chat_id_by_contact_name(app: Client, contact_name: str) -> str:
    all_chats: List[pyrogram.types.User] = await app.get_contacts()
    for chat in all_chats:
        try:
            first_name = chat.first_name
            last_name = ''
            if chat.last_name:
                last_name = chat.last_name

            if contact_name.lower() == f"{first_name} {last_name}".strip().lower():
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
    session.close()
    return chat_id


def main():
    api_id = config('API_ID', cast=int)
    api_hash = config('API_HASH', cast=str)
    phone_number = config('PHONE_NUMBER', cast=str)
    account_name = config('ACCOUNT_NAME', cast=str)

    # check if the sessinon file exists
    if not os.path.exists(f"{account_name}.session"):
        logger.critical(f"{account_name}.session not found")
        return

    app = Client(account_name, phone_number=phone_number,
                 api_hash=api_hash, api_id=api_id)

    @ app.on_message(filters.private)
    async def main_handler(client, message: pyrogram.types.messages_and_media.Message):
        session = create_session()
        user = session.query(User).filter(User.tg_id == telegram_id).all()
        session.close()

        if len(user) > 0:
            user: User = user[0]
            if not user.status:
                return False
        else:
            return False

        from_id = str(message.from_user.id)
        if message.from_user.first_name:
            if message.from_user.last_name:
                from_user_contact = f"{message.from_user.first_name} {message.from_user.last_name}"
            else:
                from_user_contact = message.from_user.first_name

        target_chat = None

        first_rules, second_rules = await get_rules_by_first_user(
            app, from_id, from_user_contact)

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
    print("Starting userbot")

    db_name = config('POSTGRES_DB', cast=str)
    db_user = config('POSTGRES_USER', cast=str)
    db_password = config('POSTGRES_PASSWORD', cast=str)
    db_host = config('DB_HOST', cast=str)
    db_port = config('POSTGRES_PORT', cast=int)
    telegram_id = config('TELEGRAM_ID', cast=str)

    global_init(db_user, db_password, db_host, db_port, db_name)
    logger.info("DB initialized")
    main()
    logger.info("Main loop finished")
    logger.info("Exiting")

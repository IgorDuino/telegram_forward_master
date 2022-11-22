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
from models import Rule, Filter, User, Forward


logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s [%(levelname)s] %(name)s :%(message)s')
logger = logging.getLogger(__name__)

api_token = config("BOT_API", cast=str)
telegram_id = config('TELEGRAM_ID', cast=str)

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


def apply_filter(trigger, action, text: str, is_fullword=False) -> Tuple[str, str]:
    status: Literal['not-applied', 'cancel-forward',
                    'disable-rule', 'replaced'] = 'not applied'

    trigger = r'{}'.format(trigger)

    if list(re.finditer(trigger, text, re.IGNORECASE)):
        if action in ['cancel-forward', 'disable-rule']:
            status = action
        else:
            status = 'replaced'

            if is_fullword:
                splited_text = text.split(' ')
                for i, word in enumerate(splited_text):
                    if trigger.lower() in word.lower():
                        splited_text[i] = action
                text = ' '.join(list(filter(('').__ne__, splited_text)))

            else:
                text = re.sub(trigger, action, text, flags=re.IGNORECASE)

    return (status, text)


async def forward_message(app: Client, message: pyrogram.types.Message, target_chat: str, rule: Rule) -> bool:
    logger.info(f"Forwarding message {message.text} to {target_chat}")

    target_chat = target_chat.split('@')[-1]

    # get filters for this rule
    session = create_session()
    filters: List[Filter] = session.query(
        Filter).filter(Filter.rule_id == rule.id).all()
    # add general filters
    filters += session.query(Filter).filter(Filter.is_general == True).all()
    session.close()

    for filter in filters:
        if not filter.is_enabled:
            continue

        # apply filter to message text
        if message.text:
            applying_filter_status, applying_filter_text = apply_filter(
                filter.replace_word, filter.to_replace_word, message.text, filter.is_fullword)

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
                filter.replace_word, filter.to_replace_word, message.caption, filter.is_fullword)

            if applying_filter_status == 'disable-rule':
                disable_rule(rule)
                send_disable_rule_notification_to_telegram(
                    rule, filter.replace_word)
                return True

            elif applying_filter_status == 'cancel-forward':
                return True

            elif applying_filter_status == 'replaced':
                message.caption = applying_filter_text

    # if messahe is reply
    if message.reply_to_message:
        # search reply message in db
        session = create_session()
        forward = session.query(Forward).filter(
            Forward.new_message_id == message.reply_to_message.id and Forward.rule_id == rule.id).first()
        forward_self = session.query(Forward).filter(
            Forward.original_message_id == message.reply_to_message.id and Forward.rule_id == rule.id).first()
        session.close()

        # if reply message is found
        if forward or forward_self:
            # reply message
            if forward:
                reply_to_message_id = forward.original_message_id
            else:
                reply_to_message_id = forward_self.new_message_id

            new_message = await message.copy(
                chat_id=int(target_chat),
                reply_to_message_id=reply_to_message_id,
            )

        else:
            # if reply message is not found
            # send copy of original message to target chat
            reply_message = message.reply_to_message

            if reply_message.text:
                datetime_srt = f'{reply_message.date: %d.%m %H:%M}'

                reply_message.text = f"[__In reply from{datetime_srt}__]\n" + \
                    reply_message.text

            new_original_message = await reply_message.copy(
                chat_id=target_chat,
                parse_mode=enums.ParseMode.MARKDOWN
            )

            new_message = await message.copy(
                int(target_chat),
            )

    else:
        #  simply copy original message to target chat
        new_message = await message.copy(
            int(target_chat),
        )

    # add forward to db
    session = create_session()
    forward = Forward(original_message_id=message.id,
                      new_message_id=new_message.id, rule_id=rule.id)
    session.add(forward)
    session.commit()
    session.close()

    return True


def is_almost_digit(text: str) -> bool:
    return set("0123456789-").issuperset(set(text))


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

    @app.on_deleted_messages()
    async def on_deleted_messages(client, messages):
        forwards = []
        new_messages_ids = []

        session = create_session()
        for message in messages:
            forward = session.query(Forward).filter(
                Forward.original_message_id == message.id).first()
            if forward:
                forwards.append(forward)
                new_messages_ids.append(forward.new_message_id)

        if forwards:
            # get rule
            rule = session.query(Rule).filter(
                Rule.id == forwards[0].rule_id).first()

            chat_id = rule.second_user_tg_id
            if "chat" in chat_id:
                chat_id = chat_id.split("@")[1]
            await app.delete_messages(chat_id, new_messages_ids)

        session.close()

    @app.on_edited_message()
    async def on_edited_message(client: Client, message: pyrogram.types.Message):
        session = create_session()
        forward = session.query(Forward).filter(
            Forward.original_message_id == message.id).first()

        if forward:
            # forward.new_message_id
            rule = session.query(Rule).filter(
                Rule.id == forward.rule_id).first()
            await app.edit_message_text(rule.second_user_tg_id, forward.new_message_id, message.text)

        session.close()

    @app.on_message(filters.group)
    async def chat_handler(client, message):
        try:
            if message.from_user.id == telegram_id:
                return
        except:
            pass
        first_rules, second_rules = await get_rules_by_first_user(
            app, f"chat@{message.chat.id}", " ")
        for rule in first_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_SECOND_TO_FIRST:
                continue

            target_chat = rule.second_user_tg_id

            await forward_message(app, message, target_chat, rule)

        for rule in second_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_FIRST_TO_SECOND:
                continue

            target_chat = rule.first_user_tg_id

            await forward_message(app, message, target_chat, rule)

    @app.on_message(filters.private)
    async def private_handler(client, message: pyrogram.types.messages_and_media.Message):
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

            if (not is_almost_digit(target_chat)) and (not target_chat.startswith("chat@")):
                target_chat = await replace_chat_id_in_database(app, rule, target_chat, 2)

            await forward_message(app, message, target_chat, rule)

        for rule in second_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_FIRST_TO_SECOND:
                continue

            target_chat = rule.first_user_tg_id
            if (not is_almost_digit(target_chat)) and (not target_chat.startswith("chat@")):
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

    global_init(db_user, db_password, db_host, db_port, db_name)
    logger.info("DB initialized")
    main()
    logger.info("Main loop finished")
    logger.info("Exiting")

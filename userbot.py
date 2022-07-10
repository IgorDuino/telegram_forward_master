from decouple import config
from typing import List, Tuple
import logging
import re
import os

from pyrogram import Client, filters
import pyrogram.types
from setuptools import PEP420PackageFinder

from db_session import global_init, create_session
from models import Rule, Filter


logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s [%(levelname)s] %(name)s :%(message)s')
logger = logging.getLogger(__name__)


def case_insensitive_replace(text: str, replace_word: str, to_replace_word: str) -> str:
    return re.compile(re.escape(replace_word), re.IGNORECASE).sub(to_replace_word, text)


async def forward_message(app, message: pyrogram.types.Message, target_chat: str, filters: List[Filter]) -> bool:
    for filter in filters:
        if not filter.is_enabled:
            continue

        if type(message.text) == str:
            if filter.replace_word in message.text:
                message.text = case_insensitive_replace(
                    message.text, filter.replace_word, filter.to_replace_word)

        if type(message.caption) == str:
            if filter.replace_word in message.caption:
                message.caption = case_insensitive_replace(
                    message.caption, filter.replace_word, filter.to_replace_word)

    await message.copy(
        int(target_chat),
    )

    return True


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

            if not rule.is_automated:
                # TODO: implement manual forwarding
                continue

            await forward_message(app, message, target_chat, rule.filters)

        for rule in second_rules:
            if not rule.is_enabled:
                continue

            if rule.direction == Rule.DIRECTION_FIRST_TO_SECOND:
                continue

            target_chat = rule.first_user_tg_id

            if not rule.is_automated:
                # TODO: implement manual forwarding
                continue

            await forward_message(app, message, target_chat, rule.filters)

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

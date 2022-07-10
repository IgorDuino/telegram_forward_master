#!venv/bin/python

from pyrogram import Client, filters
from pyrogram import types
from decouple import config

from decouple import config
import pyrogram
from db_session import global_init, create_session
from models import Rule, Filter, User

from typing import List, Tuple, Union


def get_all_rules():
    session = create_session()

    rules = session.query(Rule).all()

    return rules


async def forward_message(app, message: pyrogram.types.Message, target_chat: str, filters: List[Filter]) -> bool:
    for filter in filters:
        if not filter.is_enabled:
            continue

        if type(message.text) == str:
            if filter.replace_word in message.text:
                message.text = message.text.replace(
                    filter.replace_word, filter.to_replace_word)

    print("Forwarding message to", target_chat)

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

    app = Client("account", phone_number=phone_number,
                 api_hash=api_hash, api_id=api_id)

    @app.on_message(filters.private)
    async def main_handler(client, message: types.messages_and_media.Message):
        print("New message:", message.text)

        from_id = str(message.from_user.id)
        from_user_contact = "message.contact.first_name"

        target_chat = None

        first_rules, second_rules = get_rules_by_first_user(
            from_id, from_user_contact)

        for rule in first_rules:
            if not rule.is_enabled:
                continue

            target_chat = rule.second_user_tg_id

            if not rule.is_automated:
                continue

            await forward_message(app, message, target_chat, rule.filters)

        for rule in second_rules:
            if not rule.is_enabled:
                continue

            target_chat = rule.first_user_tg_id

            if not rule.is_automated:
                continue

            forward_message(app, message, target_chat, rule.filters)

    app.run()


if __name__ == '__main__':
    db_name = config('DB_NAME', cast=str)
    db_user = config('DB_USER', cast=str)
    db_password = config('DB_PASSWORD', cast=str)
    db_host = config('DB_HOST', cast=str)
    db_port = config('DB_PORT', cast=int)

    global_init(db_user, db_password, db_host, db_port, db_name)
    print(get_all_rules())
    main()

from pyrogram import Client, filters
from pyrogram import types
from decouple import config


def main():
    api_id = config('API_ID', cast=int)
    api_hash = config('API_HASH', cast=str)
    phone_number = config('PHONE_NUMBER', cast=str)

    app = Client("account", phone_number=phone_number,
                 api_hash=api_hash, api_id=api_id)

    @app.on_message(filters.incoming)
    async def my_handler(client, message: types.messages_and_media.Message):
        from_id = message.from_user.id
        from_user_contact = message.from_user.contact
        print(f"{from_id} {from_user_contact}")

    app.start()

    while True:
        pass


if __name__ == '__main__':
    main()

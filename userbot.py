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
        pass

    app.start()

    while True:
        pass


if __name__ == '__main__':
    main()

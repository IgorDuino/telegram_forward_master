from telethon import TelegramClient
from decouple import config


api_id = config('API_ID', cast=int)
api_hash = config('API_HASH', cast=str)
phone_number = config('PHONE_NUMBER', cast=str)


def get_code():
    code = input('Enter the code you received: ')
    return code


client = TelegramClient('account', api_id, api_hash)
client.start(phone=phone_number, code_callback=get_code)

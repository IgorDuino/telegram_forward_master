# create .session file and save it to the account_name.session
from decouple import Config, RepositoryEnv
from pyrogram import Client

DOTENV_FILE = '.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))


def create_session():
    api_id = env_config.get('API_ID', cast=int)
    api_hash = env_config.get('API_HASH', cast=str)
    phone_number = env_config.get('PHONE_NUMBER', cast=str, )
    account_name = env_config.get('ACCOUNT_NAME', cast=str)

    app = Client(account_name, phone_number=phone_number,
                 api_hash=api_hash, api_id=api_id)
    app.start()
    app.stop()


if __name__ == '__main__':
    create_session()

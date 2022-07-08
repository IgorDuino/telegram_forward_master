#!/bin/python

from threading import Thread

from userbot import main as userbot_main_function
from bot import main as bot_main_function


def main():
    userbot_thread = Thread(target=userbot_main_function)
    bot_thread = Thread(target=bot_main_function)

    userbot_thread.name = "userbot"
    bot_thread.name = "bot"

    # userbot_thread.start()
    bot_thread.start()

    # userbot_thread.join()
    bot_thread.join()


if __name__ == '__main__':
    main()

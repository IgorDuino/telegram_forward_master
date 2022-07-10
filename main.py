#  run bot and userbot

from subprocess import Popen


def run_bot():
    Popen(['python', 'bot.py'])


def run_userbot():
    Popen(['python', 'userbot.py'])


if __name__ == '__main__':
    run_bot()
    run_userbot()

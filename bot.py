from decouple import config
from data.db_session import global_init, create_session
from data.models import Rule, Filter
import sqlalchemy
import telebot
import menu
import json

api_token = config("BOT_API", cast=str)
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')
db_name = config('DB_NAME')


bot = telebot.TeleBot(api_token)

temp_rules = {}


def get_forward_from_account(message: telebot.types.Message):
    return message.forward_from


def get_rules():
    sessioin = create_session()
    rules = sessioin.query(Rule).all()
    return rules


def get_filters(rule: Rule):
    sessioin = create_session()
    filters = sessioin.query(Filter).filter(Filter.rule_id == rule.id).all()
    return filters


def add_rule_name(message: telebot.types.Message):
    temp_rules[message.chat.id] = {
        'name': message.text,
        'first_user_id': None,
        'second_user_id': None,
        'type': None,
        'filters': []
    }

    msg = bot.send_message(
        message.chat.id, "Хорошо, теперь, чтобы добавить первый контакт пользователя перешлите мне любое его сообщение")
    bot.register_next_step_handler(msg, add_rule_first_user)


def add_rule_first_user(message: telebot.types.Message):
    if not message.forward_from:
        msg = bot.send_message(
            message.chat.id, "Перешлите мне сообщение от первого пользователя")
        bot.register_next_step_handler(msg, add_rule_first_user)
        return

    temp_rules[message.chat.id]['first_user_id'] = message.forward_from.id
    msg = bot.send_message(
        message.chat.id, "Сохранил, теперь, чтобы добавить второй контакт пользователя перешлите мне любое его сообщение")
    bot.register_next_step_handler(msg, add_rule_second_user)


def add_rule_second_user(message: telebot.types.Message):
    if not message.forward_from:
        msg = bot.send_message(
            message.chat.id, "Перешлите мне сообщение от второго пользователя")
        bot.register_next_step_handler(msg, add_rule_second_user)
        return

    temp_rules[message.chat.id]['second_user_id'] = message.forward_from.id
    msg = bot.send_message(
        message.chat.id, "Окей, теперь, нужно выбрать тип пересылки.\n1. В две стороны\n2. От первого пользователя второму\n3. От второго первому\nВведите число 1, 2 или 3")
    bot.register_next_step_handler(msg, add_rule_type)


def add_rule_type(message: telebot.types.Message):
    if message.text in ['1', '2', '3']:
        temp_rules[message.chat.id]['type'] = message.text
    else:
        msg = bot.send_message(
            message.chat.id, "Введите число 1, 2 или 3")
        bot.register_next_step_handler(msg, add_rule_type)
        return

    msg = bot.send_message(
        message.chat.id, "Правило успешно добавлено", reply_markup=menu.get_menu(message.chat.id))
    bot.register_next_step_handler(msg, add_rule_replace_word)


@bot.message_handler(commands=['start', 'help'])
def handle_forwarded_message(message: telebot.types.Message):
    bot.send_message(message.chat.id, reply_markup=menu.main_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    if call.data == 'all_rules':
        rules = get_rules()
        keyboard = menu.get_rules_menu(rules)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Все правила", reply_markup=keyboard)
    elif call.data == 'add_rule':
        msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, text="Введите название правила")

        bot.register_next_step_handler(msg, add_rule_name)
    elif call.data == 'start':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Включено 🟩")
    elif call.data == 'stop':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Отключено 🟥")


if __name__ == '__main__':
    global_init(db_user, db_password, db_host, db_name)
    bot.infinity_polling()

from turtle import forward
from decouple import config
from data.db_session import global_init, create_session
from data.models import Rule, Filter, User
import telebot
import menu

api_token = config("BOT_API", cast=str)
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')
db_name = config('DB_NAME')


bot = telebot.TeleBot(api_token)

temp_rules = {}
temp_filters = {}


def add_rule(chat_id):
    temp_rule = temp_rules[chat_id]
    sessioin = create_session()
    rule = Rule(
        name=temp_rule['name'],
        first_user_tg_id=temp_rule['first_user_id'],
        second_user_tg_id=temp_rule['second_user_id'],
        direction=temp_rule['direction'],
        is_automated=temp_rule['is_automated']
    )
    sessioin.add(rule)
    sessioin.commit()
    del temp_rules[chat_id]
    return rule


def add_filter(chat_id):
    temp_filter = temp_filters[chat_id]
    sessioin = create_session()
    filter = Filter(
        rule_id=temp_filter['rule_id'],
        replace_word=temp_filter['replace_word'],
        to_replace_word=temp_filter['replace_to_word']
    )
    sessioin.add(filter)
    sessioin.commit()
    del temp_filters[chat_id]
    return filter.id


def enable_rule(rule: Rule):
    sessioin = create_session()
    rule.is_enabled = True
    sessioin.commit()
    return True


def disable_rule(rule: Rule):
    sessioin = create_session()
    rule.is_enabled = False
    sessioin.commit()
    return True


def enable_filter(filter: Filter):
    sessioin = create_session()
    filter.is_enabled = True
    sessioin.commit()
    return True


def disable_filter(filter: Filter):
    sessioin = create_session()
    filter.is_enabled = False
    sessioin.commit()
    return True


def delete_rule_by_id(rule_id):
    sessioin = create_session()
    rule = sessioin.query(Rule).filter(Rule.id == rule_id).first()
    sessioin.delete(rule)
    sessioin.commit()
    return True


def delete_filter_by_id(filter_id):
    sessioin = create_session()
    filter = sessioin.query(Filter).filter(Filter.id == filter_id).first()
    sessioin.delete(filter)
    sessioin.commit()
    return True


def set_user_status(tg_id, status):
    sessioin = create_session()
    user = sessioin.query(User).filter(User.tg_id == tg_id).first()
    user.status = status
    sessioin.commit()
    return True


def get_forward_from_account(message: telebot.types.Message):
    return message.forward_from


def get_user(tg_id):
    sessioin = create_session()
    user = sessioin.query(User).filter(User.tg_id == tg_id).first()
    return user


def get_rule_by_id(rule_id):
    sessioin = create_session()
    rule = sessioin.query(Rule).filter(Rule.id == rule_id).first()
    return rule


def get_rules():
    sessioin = create_session()
    rules = sessioin.query(Rule).all()
    return rules


def get_filter_by_id(filter_id):
    sessioin = create_session()
    filter = sessioin.query(Filter).filter(Filter.id == filter_id).first()
    return filter


def get_filters(rule: Rule):
    sessioin = create_session()
    filters = sessioin.query(Filter).filter(Filter.rule_id == rule.id).all()
    return filters


def add_filter_replace_word(message: telebot.types.Message):
    temp_filters[message.chat.id]['replace_word'] = message.text

    msg = bot.send_message(
        message.chat.id, "Сохранил, теперь напишите на что его заменять:")
    bot.register_next_step_handler(msg, add_filter_replace_to_word)


def add_filter_replace_to_word(message: telebot.types.Message):
    temp_filters[message.chat.id]['replace_to_word'] = message.text

    chat_id = message.chat.id
    filter_id = add_filter(chat_id)
    if filter_id:
        filter = get_filter_by_id(filter_id)
        msg = bot.send_message(
            message.chat.id, "Фильтр добавлен:", reply_markup=menu.filter_menu(filter))
    else:
        msg = bot.send_message(
            message.chat.id, "Что-то пошло не так, попробуйте еще раз", reply_markup=menu.main_menu(get_user(message.chat.id)))


def add_rule_first_user(message: telebot.types.Message):
    if not message.forward_from and not message.forward_sender_name:
        msg = bot.send_message(
            message.chat.id, "Перешлите мне сообщение от первого пользователя")
        bot.register_next_step_handler(msg, add_rule_first_user)
        return

    if message.forward_from:
        forward_id = message.forward_from.id
        forward_name = message.forward_from.first_name
    else:
        forward_id = message.forward_sender_name
        forward_name = message.forward_sender_name

    temp_rules[message.chat.id] = {
        'first_user_id': forward_id,
        'second_user_id': None,
        'first_user_name': forward_name,
        'second_user_name': None,
        'type': None,
        'filters': []
    }

    msg = bot.send_message(
        message.chat.id, "Сохранил, теперь, чтобы добавить второй контакт пользователя перешлите мне любое его сообщение")
    bot.register_next_step_handler(msg, add_rule_second_user)


def add_rule_second_user(message: telebot.types.Message):
    if not message.forward_from and not message.forward_sender_name:
        msg = bot.send_message(
            message.chat.id, "Перешлите мне сообщение от второго пользователя")
        bot.register_next_step_handler(msg, add_rule_second_user)
        return

    if message.forward_from:
        forward_id = message.forward_from.id
        forward_name = message.forward_from.first_name
    else:
        forward_id = message.forward_sender_name
        forward_name = message.forward_sender_name

    temp_rules[message.chat.id]['second_user_id'] = forward_id
    temp_rules[message.chat.id]['second_user_name'] = forward_name
    temp_rules[message.chat.id]['name'] = f"{temp_rules[message.chat.id]['first_user_name']} - {temp_rules[message.chat.id]['second_user_name']}"

    msg = bot.send_message(
        message.chat.id, "Выберите направление пересылки сообщений:\n1. В две стороны\n2. От первого пользователя второму\n3. От второго первому\nВведите число 1, 2 или 3")
    bot.register_next_step_handler(msg, add_rule_direction)


def add_rule_direction(message: telebot.types.Message):
    if message.text in ['1', '2', '3']:
        temp_rules[message.chat.id]['direction'] = message.text
    else:
        msg = bot.send_message(
            message.chat.id, "Введите число 1, 2 или 3")
        bot.register_next_step_handler(msg, add_rule_direction)
        return

    # add type automated or manual
    msg = bot.send_message(
        message.chat.id, "Выберите тип пересылки сообщений:\n1. Автоматическая\n2. Ручная\nВведите число 1 или 2")
    bot.register_next_step_handler(msg, add_rule_type)


def add_rule_type(message: telebot.types.Message):
    if message.text in ['1', '2']:
        temp_rules[message.chat.id]['is_automated'] = message.text == '1'
    else:
        msg = bot.send_message(
            message.chat.id, "Введите число 1 или 2")
        bot.register_next_step_handler(msg, add_rule_type)
        return

    # add rule to base
    rule = add_rule(message.chat.id)
    keyboard = menu.main_menu(get_user(message.chat.id).status)

    if rule:
        msg = bot.send_message(
            message.chat.id, "Правило успешно добавлено", reply_markup=keyboard)
    else:
        msg = bot.send_message(
            message.chat.id, "Произошла ошибка, попробуйте еще раз", reply_markup=keyboard)


@bot.message_handler(commands=['start', 'help'])
def handle_forwarded_message(message: telebot.types.Message):
    user = get_user(message.chat.id)
    if not user:
        user = User(tg_id=message.chat.id)
        sessioin = create_session()
        sessioin.add(user)
        sessioin.commit()
    bot.send_message(message.chat.id, "Главное меню",
                     reply_markup=menu.main_menu(user.status))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    if call.data == "main-menu":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Главное меню",
            reply_markup=menu.main_menu(get_user(call.message.chat.id).status)
        )
    elif call.data == 'all-rules':
        rules = get_rules()
        if len(rules) == 0:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Пока нет правил",
                reply_markup=menu.main_menu(
                    get_user(call.message.chat.id).status))
        else:
            keyboard = menu.rules_menu(rules)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Все правила", reply_markup=keyboard)

    elif call.data.startswith('filters_'):
        rule_id = call.data.split('_')[1]
        rule = get_rule_by_id(rule_id)
        if not rule:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Правило не найдено",
                reply_markup=menu.main_menu(
                    get_user(call.message.chat.id).status))
        else:
            keyboard = menu.filters_menu(rule)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтры", reply_markup=keyboard)

    elif call.data == 'add-rule':
        msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, text="Чтобы добавить первого пользователя перешлите мне любое его сообщение")

        bot.register_next_step_handler(msg, add_rule_first_user)

    elif call.data.startswith('rule_'):
        rule_id = int(call.data.split('_')[1])
        rule = get_rule_by_id(rule_id)
        if not rule:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        keyboard = menu.rule_menu(rule)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=f"Правило [{rule.id + 1}] {rule.name}", reply_markup=keyboard)

    elif call.data.startswith('filter_'):
        filter_id = int(call.data.split('_')[1])
        filter = get_filter_by_id(filter_id)
        if not filter:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        keyboard = menu.filter_menu(filter)
        title = f"{filter.replace_word} -> {filter.to_replace_word}"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=f"Фильтр {title}", reply_markup=keyboard)

    # delete rule
    elif call.data.startswith('delete-rule_'):
        rule_id = int(call.data.split('_')[1])
        rule = get_rule_by_id(rule_id)
        if not rule:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        if delete_rule_by_id(rule.id):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило удалено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # delete filter
    elif call.data.startswith('delete-filter_'):
        filter_id = int(call.data.split('_')[1])
        filter = get_filter_by_id(filter_id)
        if not filter:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        
        rule = get_rule_by_id(filter.rule_id)

        if delete_filter_by_id(filter.id):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр удален", reply_markup=menu.filters_menu(rule))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # enable rule
    elif call.data.startswith('enable-rule_'):
        rule_id = int(call.data.split('_')[1])
        rule = get_rule_by_id(rule_id)
        if not rule:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        if enable_rule(rule):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило включено", reply_markup=menu.rule_menu(rule))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # disable rule
    elif call.data.startswith('disable-rule_'):
        rule_id = int(call.data.split('_')[1])
        rule = get_rule_by_id(rule_id)
        if not rule:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило не найдено", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        if disable_rule(rule):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило выключено", reply_markup=menu.rule_menu(rule))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # enable filter
    elif call.data.startswith('enable-filter_'):
        filter_id = int(call.data.split('_')[1])
        filter = get_filter_by_id(filter_id)
        if not filter:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр не найден", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        if enable_filter(filter):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр включен", reply_markup=menu.filter_menu(filter))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # disable filter
    elif call.data.startswith('disable-filter_'):
        filter_id = int(call.data.split('_')[1])
        filter = get_filter_by_id(filter_id)
        if not filter:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр не найден", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return
        if disable_filter(filter):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр выключен", reply_markup=menu.filter_menu(filter))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
    # add filter
    elif call.data.startswith('add-filter_'):
        rule_id = int(call.data.split('_')[1])
        msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, text="Какое слово нужно заменять?")

        temp_filters[call.message.chat.id] = {'rule_id': rule_id}

        bot.register_next_step_handler(msg, add_filter_replace_word)

    elif call.data == 'start':
        set_user_status(call.message.chat.id, True)
        user = get_user(call.message.chat.id)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Бот запущен", reply_markup=menu.main_menu(user.status))
    elif call.data == 'stop':
        set_user_status(call.message.chat.id, False)
        user = get_user(call.message.chat.id)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Бот отключен", reply_markup=menu.main_menu(user.status))


if __name__ == '__main__':
    global_init(db_user, db_password, db_host, db_name)
    bot.infinity_polling()

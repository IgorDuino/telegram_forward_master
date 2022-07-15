#!venv/bin/python

from turtle import forward
from decouple import config
from db_session import global_init, create_session
from models import Rule, Filter, User
import telebot
import menu


api_token = config("BOT_API", cast=str)

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
        is_automated=True
    )
    sessioin.add(rule)
    sessioin.commit()
    del temp_rules[chat_id]
    return rule


def add_filter(chat_id):
    temp_filter = temp_filters[chat_id]
    sessioin = create_session()
    filter = Filter(
        is_general=temp_filter['is_general'],
        rule_id=temp_filter['rule_id'],
        replace_word=temp_filter['trigger'],
        to_replace_word=temp_filter['action']
    )
    sessioin.add(filter)
    sessioin.commit()
    del temp_filters[chat_id]
    fid = filter.id
    sessioin.close()

    return fid


def enable_rule(rule: Rule):
    sessioin = create_session()
    real_rule = sessioin.query(Rule).filter(Rule.id == rule.id).first()
    real_rule.is_enabled = True
    sessioin.commit()
    sessioin.close()
    return True


def disable_rule(rule: Rule):
    sessioin = create_session()
    real_rule = sessioin.query(Rule).filter(Rule.id == rule.id).first()
    real_rule.is_enabled = False
    sessioin.commit()
    sessioin.close()
    return True


def enable_filter(filter: Filter):
    sessioin = create_session()
    real_filter = sessioin.query(Filter).filter(Filter.id == filter.id).first()
    real_filter.is_enabled = True
    sessioin.commit()
    sessioin.close()
    return True


def disable_filter(filter: Filter):
    sessioin = create_session()
    real_filter = sessioin.query(Filter).filter(Filter.id == filter.id).first()
    real_filter.is_enabled = False
    sessioin.commit()
    sessioin.close()
    return True


def delete_rule_by_id(rule_id):
    sessioin = create_session()
    rule = sessioin.query(Rule).filter(Rule.id == rule_id).first()
    sessioin.delete(rule)
    sessioin.commit()
    sessioin.close()
    return True


def delete_filter_by_id(filter_id):
    sessioin = create_session()
    filter = sessioin.query(Filter).filter(Filter.id == filter_id).first()
    sessioin.delete(filter)
    sessioin.commit()
    sessioin.close()
    return True


def set_user_status(tg_id, status):
    sessioin = create_session()
    user = sessioin.query(User).filter(User.tg_id == tg_id).first()
    user.status = status
    sessioin.commit()
    sessioin.close()
    return True


def get_forward_from_account(message: telebot.types.Message):
    return message.forward_from


def get_user(tg_id):
    sessioin = create_session()
    user = sessioin.query(User).filter(User.tg_id == tg_id).first()
    sessioin.close()
    return user


def get_rule_by_id(rule_id):
    sessioin = create_session()
    rule = sessioin.query(Rule).filter(Rule.id == rule_id).first()
    sessioin.close()
    return rule


def get_rules():
    sessioin = create_session()
    rules = sessioin.query(Rule).all()
    sessioin.close()
    return rules


def get_filter_by_id(filter_id):
    sessioin = create_session()
    filter: Filter = sessioin.query(Filter).filter(
        Filter.id == filter_id).first()
    sessioin.close()
    return filter


def get_filters(rule: Rule):
    sessioin = create_session()
    filters = sessioin.query(Filter).filter(Filter.rule_id == rule.id).all()
    sessioin.close()
    return filters


def add_rule_first_user_contact_name(message: telebot.types.Message):
    temp_rules[message.chat.id]['first_user_id'] = message.text

    msg = bot.send_message(
        message.chat.id, "Сохранил, теперь, чтобы добавить второй контакт пользователя перешлите мне любое его сообщение")
    bot.register_next_step_handler(msg, add_rule_second_user)


def add_rule_second_user_contact_name(message: telebot.types.Message):
    temp_rules[message.chat.id]['second_user_id'] = message.text

    msg = bot.send_message(
        message.chat.id, "Выберите направление пересылки сообщений:\n1. В две стороны\n2. От первого пользователя второму\n3. От второго первому\nВведите число 1, 2 или 3")
    bot.register_next_step_handler(msg, add_rule_direction)


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
        # there is not all the necessary data -> request a name in contacts
        forward_name = message.forward_sender_name

        temp_rules[message.chat.id] = {
            'first_user_id': None,
            'second_user_id': None,
            'first_user_name': forward_name,
            'second_user_name': None,
            'type': None
        }
        msg = bot.send_message(
            message.chat.id, "Из-за политики приватности данного пользователя мне не удалось узнать его ID.  \n\nДля продолжения добавьте данного пользователя в контакты Telgram и пришлите мне то, как его назвали тоно.")
        bot.register_next_step_handler(msg, add_rule_first_user_contact_name)
        return

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
        # there is not all the necessary data -> request a name in contacts
        forward_name = message.forward_sender_name

        temp_rules[message.chat.id]['second_user_name'] = forward_name

        msg = bot.send_message(
            message.chat.id, "Из-за политики приватности данного пользователя мне не удалось узнать его ID.  \n\nДля продолжения добавьте данного пользователя в контакты Telgram и пришлите мне то, как его назвали тоно.")
        bot.register_next_step_handler(msg, add_rule_second_user_contact_name)
        return

    temp_rules[message.chat.id]['second_user_id'] = forward_id
    temp_rules[message.chat.id]['second_user_name'] = forward_name

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
    direction_emodji = ['🔄', '➡', '⬅']
    temp_rules[message.chat.id][
        'name'] = f"{temp_rules[message.chat.id]['first_user_name']} {direction_emodji[int(temp_rules[message.chat.id]['direction']) - 1]} {temp_rules[message.chat.id]['second_user_name']}"

    rule = add_rule(message.chat.id)
    keyboard = menu.main_menu(get_user(message.chat.id).status)

    if rule:
        msg = bot.send_message(
            message.chat.id, "Правило успешно добавлено", reply_markup=keyboard)
    else:
        msg = bot.send_message(
            message.chat.id, "Произошла ошибка, попробуйте еще раз", reply_markup=keyboard)


def add_filter_trigger_phrase(message: telebot.types.Message):
    if not message.text:
        msg = bot.send_message(
            message.chat.id, "Введите фразу для добавления в фильтр")
        bot.register_next_step_handler(msg, add_filter_trigger_phrase)
        return

    if not temp_filters.get(message.chat.id, False):
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                  get_user(message.chat.id).status))
        return

    temp_filters[message.chat.id]['trigger'] = message.text

    keyboard = menu.add_filter_action_menu()
    bot.send_message(chat_id=message.chat.id,
                     text="Выберите, что должен делать фильтр", reply_markup=keyboard)


def add_filter_action_phrase(message: telebot.types.Message):
    if not message.text:
        msg = bot.send_message(
            message.chat.id, "Введите фразу для добавления в фильтр")
        bot.register_next_step_handler(msg, add_filter_action_phrase)
        return

    if not temp_filters.get(message.chat.id, False):
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                  get_user(message.chat.id).status))
        return

    temp_filters[message.chat.id]['action'] = message.text

    if add_filter(message.chat.id):
        bot.send_message(chat_id=message.chat.id,
                         text="Фильтр успешно добавлен", reply_markup=menu.main_menu(get_user(message.chat.id).status))
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(get_user(message.chat.id).status))


@bot.message_handler(commands=['start', 'help'])
def handle_forwarded_message(message: telebot.types.Message):
    if str(message.chat.id) not in [config('TELEGRAM_ID', cast=str), config('ADMIN_TELEGRAM_ID', cast=str)]:
        bot.send_message(message.chat.id,
                         "У вас нет прав для данного действия")
        return

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
    if len(call.data.split('@')) > 1:
        call.data = call.data.split('@')[0]

    if call.data.split('_')[-1] == 'remove-temp-filter':
        try:
            del temp_rules[call.message.chat.id]
        except KeyError:
            pass

    if call.data.startswith('main-menu'):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Главное меню",
            reply_markup=menu.main_menu(get_user(call.message.chat.id).status)
        )

    elif call.data.startswith('all-rules'):
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

    # rule menu
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
            rule = get_rule_by_id(rule.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило включено", reply_markup=menu.rule_menu(rule))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # груповые чаты

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
            rule = get_rule_by_id(rule.id)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Правило выключено", reply_markup=menu.rule_menu(rule))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    elif call.data.startswith('add-rule'):
        msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, text="Чтобы добавить первого пользователя перешлите мне любое его сообщение")

        bot.register_next_step_handler(msg, add_rule_first_user)

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

    elif call.data.startswith('filters_'):
        rule_id = call.data.split('_')[1]

        session = create_session()

        if rule_id == "general":
            filters = session.query(Filter).filter(
                Filter.is_general == True).all()

        else:
            filters = session.query(Filter).filter(
                Filter.rule_id == rule_id).all()

        session.close()

        text =  "Общие фильтры:" if rule_id == "general" else "Фильтры правила: "

        keyboard = menu.filters_menu(-1 if rule_id == 'general' else rule_id, filters)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=text, reply_markup=keyboard)

    elif call.data.startswith('filter_'):
        filter_id = int(call.data.split('_')[1])
        filter = get_filter_by_id(filter_id)
        if not filter:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр не найден", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return

        keyboard = menu.filter_menu(filter)

        trigger_replace_dict = {
            "telegram": "Telegram ник",
            "phone": "Телефон",
            "mail": "Эл. почта",
            "link": "Ссылка"
        }

        trigger = trigger_replace_dict.get(
            filter.replace_word, filter.replace_word)

        action_replace_dict = {
            "": "Удалить триггер",
            "disable-rule": "Отключение правила",
            "cancel-forward": "Отмена пересылки"}

        action = action_replace_dict.get(
            filter.to_replace_word, filter.to_replace_word)

        title = f"{trigger} → {action}"

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=f"Фильтр {title}", reply_markup=keyboard)

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
            filter = get_filter_by_id(filter.id)
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
            filter = get_filter_by_id(filter.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр выключен", reply_markup=menu.filter_menu(filter))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    # add filter
    elif call.data.startswith('add-filter_'):
        rule_id = call.data.split('_')[1]

        if rule_id == "general":
            temp_filters[call.message.chat.id] = {
                'is_general': True, 'rule_id': None
            }
        else:
            temp_filters[call.message.chat.id] = {
                'is_general': False, 'rule_id': int(rule_id)}

        keyboard = menu.add_filter_trigger_menu()
        msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, text="Выберите на что должен срабатывать фильтр", reply_markup=keyboard)

    elif call.data.startswith('add-filter-trigger_'):
        trigger = call.data.split('_')[1]

        if not temp_filters.get(call.message.chat.id, False):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return

        if trigger == 'phrase':
            msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id, text="Введите слово триггер: ")
            bot.register_next_step_handler(msg, add_filter_trigger_phrase)

        else:
            temp_filters[call.message.chat.id]['trigger'] = trigger

            keyboard = menu.add_filter_action_menu()
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Выберите, что должен делать фильтр", reply_markup=keyboard)

    # add-filter-action
    elif call.data.startswith('add-filter-action_'):
        action = call.data.split('_')[1]

        if not temp_filters.get(call.message.chat.id, False):
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))
            return

        if action == 'phrase':
            msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id, text="Введите слово, фразу, номер телефона или почту на которую фильтр будет заменять триггер: ")
            bot.register_next_step_handler(msg, add_filter_action_phrase)

        else:
            temp_filters[call.message.chat.id]['action'] = '' if action == 'delete' else action

            if add_filter(call.message.chat.id):
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id, text="Фильтр добавлен", reply_markup=menu.main_menu(
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
            session = create_session()
            filters = session.query(Filter).filter(
                Filter.rule_id == rule.id).all()
            session.close()
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Фильтр удален", reply_markup=menu.filters_menu(rule.id, filters))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="Произошла ошибка, попробуйте еще раз", reply_markup=menu.main_menu(
                                      get_user(call.message.chat.id).status))

    elif call.data.startswith('enable-bot'):
        set_user_status(call.message.chat.id, True)
        user = get_user(call.message.chat.id)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Бот запущен", reply_markup=menu.main_menu(user.status))

    elif call.data.startswith('disable-bot'):
        set_user_status(call.message.chat.id, False)
        user = get_user(call.message.chat.id)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Бот отключен", reply_markup=menu.main_menu(user.status))


def main():
    db_name = config('POSTGRES_DB', cast=str)
    db_user = config('POSTGRES_USER', cast=str)
    db_password = config('POSTGRES_PASSWORD', cast=str)
    db_host = config('DB_HOST', cast=str)
    db_port = config('POSTGRES_PORT', cast=int)

    global_init(db_user, db_password, db_host, db_port, db_name)
    bot.infinity_polling()


if __name__ == '__main__':
    print("Starting bot")
    main()

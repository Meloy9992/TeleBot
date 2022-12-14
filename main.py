import telebot
from telebot import types
import psycopg2
from config import host, user, password, db_name
import json

full_name = ''
phone_number = 0
social_network = list('')
isClear = True
listUsers = dict()
data = {
    "users": []
}

bot = telebot.TeleBot("")


class Users:
    def __init__(self, full_name, phone_number, social_network):
        self.full_name = full_name
        self.phone_number = phone_number
        self.social_network = social_network


def addToDatabase():
    global isClear
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        # Создание курсора для выполнения SQL команд
        with connection.cursor() as cursor:
            soc = ', '.join(social_network)
            item = (full_name, phone_number, soc)
            sql = """INSERT INTO users (full_names, phone_numbers, social_networks) VALUES (%s, %s, %s)"""
            cursor.execute(sql, item)
            isClear = False
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def getAllUser():
    global isClear
    # global listUsers
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users1 = cursor.fetchall()
            answer = ''
            if len(users1) == 0:
                isClear = True
                question = 'Ничего не найдено'
                return question
            for row in users1:
                if row[3] != '':
                    answer += "Id= " + str(row[0]) + " Имя= " + row[1] + " Телефон= " + str(
                        row[2]) + " Социальные сети= " + row[3] + "\n"
                    listUsers[row[0]] = Users(row[1], row[2], row[3])
                else:
                    answer += "Id= " + str(row[0]) + " Имя= " + row[1] + " Телефон= " + str(row[2]) + "\n"
                    listUsers[row[0]] = Users(row[1], row[2], row[3])
            isClear = False
            return answer
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def getAllUserSorted():
    global isClear
    # global listUsers
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY full_names")
            users1 = cursor.fetchall()
            answer = ''
            if len(users1) == 0:
                isClear = True
                question = 'Ничего не найдено'
                return question
            for row in users1:
                if row[3] != '':
                    answer += "Id= " + str(row[0]) + " Имя= " + row[1] + " Телефон= " + str(
                        row[2]) + " Социальные сети= " + row[3] + "\n"
                else:
                    answer += "Id= " + str(row[0]) + " Имя= " + row[1] + " Телефон= " + str(row[2]) + "\n"
            isClear = False
            return answer
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def delete(id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        with connection.cursor() as cursor:
            sql = """DELETE FROM users WHERE id_users = %s"""
            cursor.execute(sql, (id,))

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
            print("[INFO] PostgreSQL connection closed")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Для того чтобы начать введите любую из команд: /add, /getAll, /getSorted, /delete, /write, /deleteFile")


@bot.message_handler(commands=['add'])
def echo_all(message):
    # if message.text == '/add':
    bot.send_message(message.from_user.id, "Введите ФИО")
    bot.register_next_step_handler(message, add_full_name)


@bot.message_handler(commands=['getAll'])
def echo_all(message):
    # if message.text == '/getAll':
    bot.send_message(message.from_user.id, getAllUser())


@bot.message_handler(commands=['getSorted'])
def echo_all(message):
    # if message.text == '/getAll':
    bot.send_message(message.from_user.id, getAllUserSorted())


@bot.message_handler(commands=['delete'])
def echo_all(message):
    # if message.text == '/delete':
    bot.send_message(message.from_user.id, getAllUser())
    if isClear:
        print("[INFO] Table 'users' in Database is clear")
    else:
        bot.send_message(message.from_user.id, "Введите Id для удаления")
        bot.register_next_step_handler(message, deleted)


@bot.message_handler(commands=['write'])
def echo_all(message):
    # if message.text == '/write':
    print(getAllUser())
    data['users'].clear()
    for id, users in listUsers.items():
        data['users'].append(users.__dict__)
        writeToFile(data, 'data.json')


@bot.message_handler(commands=['deleteFile'])
def echo_all(message):
    # if message.text == '/write':
    data['users'].clear()
    deleteFromFile(data, 'data.json')


def deleted(message):
    delete(message.text)
    bot.send_message(message.from_user.id, "Удалено")


def add_full_name(message):
    global full_name
    full_name = message.text
    bot.send_message(message.from_user.id, "Введите номер телефона")
    bot.register_next_step_handler(message, add_phone_number)


def add_phone_number(message):
    global phone_number
    try:
        phone_number = int(message.text)
        bot.send_message(message.from_user.id, "Введите социальные сети")
        bot.register_next_step_handler(message, add_social_network)
    except Exception:
        bot.send_message(message.from_user.id, "Введите номер телефона цифрами")
        bot.register_next_step_handler(message, add_phone_number)


def add_social_network(message):
    global social_network
    if (message.text == 'Выход'):

        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = "Ваши данные верны? ФИО: " + str(full_name) + " Номер телефона: " + str(
            phone_number)

        question_with_soc = "Ваши данные верны? ФИО: " + str(full_name) + " Номер телефона: " + str(
            phone_number) + " Ваши соц. сети: " + str(soc_network())
        if not social_network:
            bot.send_message(message.from_user.id,
                             text=question, reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id,
                             text=question_with_soc, reply_markup=keyboard)

    elif (message.text != ''):
        bot.send_message(message.from_user.id, "Введите социальные сети")
        social_network.append(message.text)
        bot.register_next_step_handler(message, add_social_network)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if (call.data == "yes"):
        addToDatabase()
        bot.send_message(call.message.chat.id, "Записано в БД")
    elif (call.data == "no"):
        bot.send_message(call.message.chat.id, "Тогда попробуйте еще раз")
        bot.send_message(call.message.chat.id, "Введите ФИО")
        bot.register_next_step_handler(call.message, add_full_name)


def writeToFile(data, fileName):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open(fileName, 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii= False)


def deleteFromFile(data, fileName):
    data = json.dumps(data)
    data = json.loads(str(data))
    with open(fileName, 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii= False)


def soc_network():
    return ', '.join(social_network)


bot.polling()

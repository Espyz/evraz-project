import json
import telebot
import time
import requests
from telebot import types
from threading import Thread
from datetime import datetime, timedelta

bot = telebot.TeleBot('6860529198:AAEBOIi3AeMLoIojev-JEztqM5DqbEO2n9s')
notify_bot = telebot.TeleBot('6171912154:AAHo24u0CnQ5XK8cF2URD5Tm66FeyMWnGhU')

employee = {}
employees = []

work_type = {}
work_types = []

conditions = {}

date = {}
grafik = []
index_global = -1

is_edit = False
next_message_on = datetime.now()

def add_employee_fio(message):
    global employee
    employee['fio'] = message.text
    bot.send_message(message.from_user.id, text='Введите должность сотрудника')
    bot.register_next_step_handler(message, add_employee_post)

def remove_employer(message):
    try:
        file = open('employees.json', 'r', encoding='utf-8')
        works = json.load(file)
        file.close()
        works.pop(int(message.text) - 1)
        file = open('employees.json', 'w', encoding='utf-8')
        json.dump(works, file, ensure_ascii=False)
        file.close()
    except:
        pass
    bot_start_window(message)


def add_employee_post(message):
    global employee
    employee['post'] = message.text
    bot.send_message(message.from_user.id, text='Укажите ссылку на профиль сотрудника в Телеграм')
    bot.register_next_step_handler(message, add_employee_link)


def add_employee_link(message):
    global employee, employees
    employee['link'] = message.text
    file = open('employees.json', 'r', encoding='utf-8')
    if file.read() != '':
        file.seek(0)
        employees = json.load(file)
    file.close()
    employees.append(employee)
    file = open('employees.json', 'w', encoding='utf-8')
    json.dump(employees, file, ensure_ascii=False)
    file.close()
    bot.send_message(message.from_user.id, text='Данные сохранены')
    print(employees)
    # message = {}
    # message['content_type'] = 'text'
    # message['from_user'] = {'id': 1130146790}
    # get_text_messages(message)
    # bot.register_next_step_handler(message, get_text_messages('/start'))
    # bot.register_next_step_handler(message, bot_start_window)
    bot_start_window(message)

def add_work_type(message):
    global work_type, work_types
    work_type['type'] = message.text
    bot.send_message(message.from_user.id, text='Укажите ограничения для проведения работ')
    bot.send_message(message.from_user.id, text='Укажите минимальную температуру, допустимую для проведения работ')
    bot.register_next_step_handler(message, add_work_conditions_min_temp)

def remove_work_type(message):
    try:
        file = open('work_types.json', 'r', encoding='utf-8')
        works = json.load(file)
        file.close()
        works.pop(int(message.text) - 1)
        file = open('work_types.json', 'w', encoding='utf-8')
        json.dump(works, file, ensure_ascii=False)
        file.close()
    except:
        pass
    bot_start_window(message)


def add_work_conditions_min_temp(message):
    global conditions
    conditions['min_temp'] = message.text
    bot.send_message(message.from_user.id, text='Укажите максимальную температуру, допустимую для проведения работ')
    bot.register_next_step_handler(message, add_work_conditions_max_temp)


keyboard1 = types.InlineKeyboardMarkup()
button11 = types.InlineKeyboardButton(text='Да', callback_data='rainfall_true')
button22 = types.InlineKeyboardButton(text='Нет', callback_data='rainfall_false')

keyboard1.add(button11, button22)

keyboard2 = types.InlineKeyboardMarkup()
button111 = types.InlineKeyboardButton(text='Да', callback_data='snow_true')
button222 = types.InlineKeyboardButton(text='Нет', callback_data='snow_false')

keyboard2.add(button111, button222)


def add_work_conditions_max_temp(message):
    global conditions
    conditions['max_temp'] = message.text
    bot.send_message(message.from_user.id, text="Уточните, возможно ли проведение работ в дождь (Да/Нет)",
                     reply_markup=keyboard1)
    # bot.register_next_step_handler(message, add_work_conditions_rainfall)


def add_work_conditions_rainfall(message):
    global conditions, keyboard1
    conditions['rainfall'] = keyboard1.callback_data
    bot.send_message(message.from_user.id, text='Уточните, возможно ли проведение работ в снегопад (Да/Нет)',
                     reply_markup=keyboard2)
    bot.register_next_step_handler(message, add_work_conditions_snow)


def add_work_conditions_snow(message):
    global conditions, keyboard2
    conditions['snow'] = keyboard2.callback_data
    bot.send_message(message.from_user.id, text='Данные сохранены')

def edit_work_type(message):
    global conditions, work_type

    work_type['type'] = message.text
    text = 'Проверьте введенные данные:\n\n\n'
    if 'type' in work_type:
        text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n\n'
    if 'min_temp' in conditions:
        text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
    if 'max_temp' in conditions:
        text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
    if 'rainfall' in conditions:
        if conditions['rainfall'] == True:
            text += 'Возможно проводить в дождь: Да' + '\n\n'
        else:
            text += 'Возможно проводить в дождь: Нет' + '\n\n'
    if 'snow' in conditions:
        if conditions['snow'] == True:
            text += 'Возможно проводить в снегопад: Да' + '\n'
        else:
            text += 'Возможно проводить в снегопад: Нет' + '\n'
    keyboard4 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
    keyboard4.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard4)


def edit_min_temp(message):
    global conditions, keyboard4
    conditions['min_temp'] = message.text
    text = 'Проверьте введенные данные:\n\n\n'
    if 'type' in work_type:
        text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n\n'
    if 'min_temp' in conditions:
        text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
    if 'max_temp' in conditions:
        text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
    if 'rainfall' in conditions:
        if conditions['rainfall'] == True:
            text += 'Возможно проводить в дождь: Да' + '\n\n'
        else:
            text += 'Возможно проводить в дождь: Нет' + '\n\n'
    if 'snow' in conditions:
        if conditions['snow'] == True:
            text += 'Возможно проводить в снегопад: Да' + '\n'
        else:
            text += 'Возможно проводить в снегопад: Нет' + '\n'
    keyboard4 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
    keyboard4.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard4)

def edit_max_temp(message):
    global conditions, keyboard4
    conditions['max_temp'] = message.text
    text = 'Проверьте введенные данные:\n\n\n'
    if 'type' in work_type:
        text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n\n'
    if 'min_temp' in conditions:
        text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
    if 'max_temp' in conditions:
        text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
    if 'rainfall' in conditions:
        if conditions['rainfall'] == True:
            text += 'Возможно проводить в дождь: Да' + '\n\n'
        else:
            text += 'Возможно проводить в дождь: Нет' + '\n\n'
    if 'snow' in conditions:
        if conditions['snow'] == True:
            text += 'Возможно проводить в снегопад: Да' + '\n'
        else:
            text += 'Возможно проводить в снегопад: Нет' + '\n'
    keyboard4 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
    keyboard4.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard4)

def edit_rainfall(message):
    global conditions, keyboard4, keyboard1
    conditions['rainfall'] = keyboard1.callback_data
    text = 'Проверьте введенные данные:\n\n\n'
    if 'type' in work_type:
        text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n\n'
    if 'min_temp' in conditions:
        text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
    if 'max_temp' in conditions:
        text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
    if 'rainfall' in conditions:
        if conditions['rainfall'] == True:
            text += 'Возможно проводить в дождь: Да' + '\n\n'
        else:
            text += 'Возможно проводить в дождь: Нет' + '\n\n'
    if 'snow' in conditions:
        if conditions['snow'] == True:
            text += 'Возможно проводить в снегопад: Да' + '\n'
        else:
            text += 'Возможно проводить в снегопад: Нет' + '\n'
    keyboard4 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
    keyboard4.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard4)

def edit_snow(message):
    global conditions, keyboard4
    conditions['snow'] = keyboard2.callback_data
    text = 'Проверьте введенные данные:\n\n\n'
    if 'type' in work_type:
        text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n\n'
    if 'min_temp' in conditions:
        text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
    if 'max_temp' in conditions:
        text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
    if 'rainfall' in conditions:
        if conditions['rainfall'] == True:
            text += 'Возможно проводить в дождь: Да' + '\n\n'
        else:
            text += 'Возможно проводить в дождь: Нет' + '\n\n'
    if 'snow' in conditions:
        if conditions['snow'] == True:
            text += 'Возможно проводить в снегопад: Да' + '\n'
        else:
            text += 'Возможно проводить в снегопад: Нет' + '\n'
    keyboard4 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
    keyboard4.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard4)

def add_date_start(message):
    global date, work_type, index_global
    file = open('work_types.json', 'r', encoding='utf-8')
    work_types = json.load(file)
    file.close()
    index_global = int(message.text) - 1
    # work_types[index]['type'] in work_types
    work_type = work_types[index_global]
    bot.send_message(message.from_user.id, text='Укажите дату начала проведения работ в формате дд.мм.гггг')
    bot.register_next_step_handler(message, add_date_end)
    # else:
    #     bot.send_message(message.from_user.id, text='Данного вида работ нет в списке')
    #     bot.register_next_step_handler(message, add_date_start)

def add_date_end(message):
    global work_type
    try: 
        datetime.strptime(message.text, '%d.%m.%Y')
        work_type['date_start'] = message.text
        bot.send_message(message.from_user.id, text='Укажите дату окончания проведения работ в формате дд.мм.гггг')
        bot.register_next_step_handler(message, all_employees)
    except:
        bot.send_message(message.from_user.id, text='Неверный формат даты. Укажите дату начала проведения работ в формате дд.мм.гггг')
        bot.register_next_step_handler(message, add_date_end)

def all_employees(message):
    global employees, employee, work_type
    try:
        datetime.strptime(message.text, '%d.%m.%Y')
        work_type['date_end'] = message.text
        text = 'Выберите ответственного сотрудника (в сообщении отправьте только номер)\n\n\n'
        file1 = open('employees.json', 'r', encoding='utf-8')
        employees = json.load(file1)
        print(employees)
        for i in range(len(employees)):
            text += str(i + 1) + '. ' + employees[i]['fio'] + '\n\n'
        bot.send_message(message.from_user.id, text=text)
        bot.register_next_step_handler(message, head_employee)
        file1.close()
    except:
        bot.send_message(message.from_user.id, text='Неверный формат даты. Укажите дату начала проведения работ в формате дд.мм.гггг')
        bot.register_next_step_handler(message, all_employees)

def head_employee(message):
    global index_global
    try:
        file = open('employees.json', 'r', encoding='utf-8')
        employees = json.load(file)
        file.close()
        index = int(message.text) - 1
        employee = employees[index]
        work_type['employer'] = employee
        file = open('work_types.json', 'r', encoding='utf-8')
        work_types = json.load(file)
        work_types[index_global] = work_type
        file.close()
        file = open('work_types.json', 'w', encoding='utf-8')
        json.dump(work_types, file, ensure_ascii=False)
        file.close()
        bot.send_message(message.from_user.id, text='Успешно')
    except:
        pass
    bot_start_window(message)

def edit_grafik(message):
    text = 'Проверьте введенные данные:\n\n\n'
    if 'work_type' in date:
        text += 'Вид проводимых работ: ' + date['work_type'] + '\n\n\n'
    if 'date_start' in date:
        text += 'Дата начала проведения работ: ' + date['date_start'] + '\n\n'
    if 'date_end' in date:
        text += 'Дата окончания проведения работ: ' + date['date_end'] + '\n\n'
    if 'head_employee' in date:
        text += 'Ответственный сотрудник: ' + date['head_employee'] + '\n\n'
    keyboard10 = types.InlineKeyboardMarkup()
    buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file1')
    buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file1')
    keyboard10.add(buttonfile, buttonfile1)
    bot.send_message(message.from_user.id, text=text, reply_markup=keyboard10)


def bot_start_window(message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Вид проводимых работ', callback_data='Вид проводимых работ')
    button2 = types.InlineKeyboardButton(text='Ответственного сотрудника',
                                         callback_data='Ответственного сотрудника')
    button3 = types.InlineKeyboardButton(text='График проведения работ',
                                         callback_data='График проведения работ')

    keyboard.add(button1, button2, button3)
    works(message)
    bot.send_message(message.from_user.id, text="Выберите, что хотите добавить/редактировать",
                     reply_markup=keyboard)

def works(message):
    file = open('work_types.json', 'r', encoding='utf-8')
    file_text = file.read()
    print(file_text)
    if file_text != '':
        file.seek(0)
        work_types = json.load(file)
        file.close()
    else:
        print('А мы на рофле')
        file.close()
        return   
    if len(work_types) > 0:
        text = 'Текущий список проводимых работ:\n\n'
        iter = 1
        for work_type in work_types:
            conditions = work_type["conditions"]
            if 'type' in work_type:
                text += str(iter) + '. Вид проводимых работ: ' + work_type['type'] + '\n'
            if 'min_temp' in conditions:
                text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n'
            if 'max_temp' in conditions:
                text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n'
            if 'rainfall' in conditions:
                if conditions['rainfall'] == True:
                    text += 'Возможно проводить в дождь: Да' + '\n'
                else:
                    text += 'Возможно проводить в дождь: Нет' + '\n'
            if 'snow' in conditions:
                if conditions['snow'] == True:
                    text += 'Возможно проводить в снегопад: Да' + '\n'
                else:
                    text += 'Возможно проводить в снегопад: Нет' + '\n'
            if 'date_start' in work_type:
                text += 'Дата начала проведения работ: ' + work_type['date_start'] + '\n'
            if 'date_end' in work_type:
                text += 'Дата окончания проведения работ: ' + work_type['date_end'] + '\n'
            if 'employer' in work_type:
                text += 'Участник: ' + work_type['employer']['fio'] + '\n'
            iter+=1
            text += '\n\n\n'
        bot.send_message(message.from_user.id, text=text)
    else:
        return    



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global keyboard1, keyboard2
    # Проверка на доступ пользователя
    file = open('admins.json', 'r', encoding='utf-8')
    admins = json.load(file)
    file.close()
    if str(message.from_user.id) not in admins.keys():
        bot.send_message(message.from_user.id, text='У Вас нет доступа')
    else:
        if message.text == '/start':
            # Создание меню с командами
            bot.set_my_commands(
                commands=[
                    types.BotCommand('/start', 'Начать работу с ботом'),
                ],
                scope=types.BotCommandScopeChat(message.chat.id)
            )
            keyboard = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text='Вид проводимых работ', callback_data='Вид проводимых работ')
            button2 = types.InlineKeyboardButton(text='Ответственного сотрудника',
                                                 callback_data='Ответственного сотрудника')
            button3 = types.InlineKeyboardButton(text='График проведения работ',
                                                 callback_data='График проведения работ')

            keyboard.add(button1, button2, button3)

            keyboard1 = types.InlineKeyboardMarkup()
            button11 = types.InlineKeyboardButton(text='Да', callback_data='rainfall_true')
            button22 = types.InlineKeyboardButton(text='Нет', callback_data='rainfall_false')

            keyboard1.add(button11, button22)

            keyboard2 = types.InlineKeyboardMarkup()
            button111 = types.InlineKeyboardButton(text='Да', callback_data='snow_true')
            button222 = types.InlineKeyboardButton(text='Нет', callback_data='snow_false')

            keyboard2.add(button111, button222)

            bot.send_message(message.from_user.id, text='Привет! Добро пожаловать')
            works(message)
            bot.send_message(message.from_user.id, text="Выберите, что хотите добавить/редактировать",
                             reply_markup=keyboard)


# Обработчик нажатия
@bot.callback_query_handler(func=lambda call: True)
# Функция обработки нажатия на кнопку
def callback_worker(call):
    global work_type, keyboard1, keyboard2, keyboard3, is_edit, keyboard
    if call.data == 'Вид проводимых работ':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить', callback_data='add_work_type')
        button2 = types.InlineKeyboardButton(text='Удалить', callback_data='remove_work_type')
        keyboard.add(button1, button2)
        bot.send_message(call.message.chat.id, text='Выберите что хотите сделать', reply_markup=keyboard)

    elif call.data == 'Ответственного сотрудника':
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Добавить', callback_data='add_empl')
        button2 = types.InlineKeyboardButton(text='Удалить', callback_data='remove_empl')
        keyboard.add(button1, button2)
        bot.send_message(call.message.chat.id, text='Выберите что хотите сделать', reply_markup=keyboard)
    elif call.data == 'add_empl':
        bot.send_message(call.message.chat.id, text='Добавьте ответственного сотрудника')
        bot.send_message(call.message.chat.id, text='Введите ФИО ответственного сотрудника')
        bot.register_next_step_handler(call.message, add_employee_fio)
    elif call.data == 'remove_empl':
        file = open('employees.json', 'r', encoding='utf-8')
        file_text = file.read()
        file.seek(0)
        if (file_text == '') or (file_text == '[]') :
            file.close()
            bot.send_message(call.message.chat.id, text='Сейчас нет проводимых работ')
            bot_start_window(call)
        else:
            works = json.load(file)
            file.close()
            text = 'Введите тип проводимых работ. Только номер'
            iter = 1
            for work in works:
                text += '\n' + str(iter) + '. ' + work['fio'] 
                iter += 1              
            bot.send_message(call.message.chat.id, text=text)
            bot.register_next_step_handler(call.message, remove_employer)
    elif call.data == 'add_work_type':
        bot.send_message(call.message.chat.id, text='Добавьте вид проводимых работ')
        bot.send_message(call.message.chat.id, text='Введите название вида работ')
        bot.register_next_step_handler(call.message, add_work_type)
    elif call.data == 'remove_work_type':
        file = open('work_types.json', 'r', encoding='utf-8')
        file_text = file.read()
        file.seek(0)
        if (file_text == '') or (file_text == '[]') :
            file.close()
            bot.send_message(call.message.chat.id, text='Сейчас нет проводимых работ')
            bot_start_window(call)
        else:
            works = json.load(file)
            file.close()
            text = 'Введите тип проводимых работ. Только номер'
            iter = 1
            for work in works:
                text += '\n' + str(iter) + '. ' + work['type'] 
                iter += 1              
            bot.send_message(call.message.chat.id, text=text)
            bot.register_next_step_handler(call.message, remove_work_type)


    elif call.data == 'rainfall_true':
        conditions['rainfall'] = True

        keyboard2 = types.InlineKeyboardMarkup()
        button11 = types.InlineKeyboardButton(text='Да', callback_data='snow_true')
        button22 = types.InlineKeyboardButton(text='Нет', callback_data='snow_false')
        keyboard2.add(button11, button22)
        if not is_edit:
            bot.send_message(call.message.chat.id, text='Уточните, возможно ли проведение работ в снег (Да/Нет)', reply_markup=keyboard2)
        else:
            text = 'Проверьте введенные данные:\n\n\n'
            if 'type' in work_type:
                text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n'
            if 'min_temp' in conditions:
                text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
            if 'max_temp' in conditions:
                text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
            if 'rainfall' in conditions:
                if conditions['rainfall'] == True:
                    text += 'Возможно проводить в дождь: Да' + '\n\n'
                else:
                    text += 'Возможно проводить в дождь: Нет' + '\n\n'
            if 'snow' in conditions:
                if conditions['snow'] == True:
                    text += 'Возможно проводить в снегопад: Да' + '\n'
                else:
                    text += 'Возможно проводить в снегопад: Нет' + '\n'
            keyboard4 = types.InlineKeyboardMarkup()
            buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
            buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
            keyboard4.add(buttonfile, buttonfile1)
            bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard4)


    elif call.data == 'rainfall_false':
        conditions['rainfall'] = False

        keyboard2 = types.InlineKeyboardMarkup()
        button11 = types.InlineKeyboardButton(text='Да', callback_data='snow_true')
        button22 = types.InlineKeyboardButton(text='Нет', callback_data='snow_false')
        keyboard2.add(button11, button22)
        if not is_edit:
            bot.send_message(call.message.chat.id, text='Уточните, возможно ли проведение работ в снег (Да/Нет)', reply_markup=keyboard2)

    elif call.data == 'snow_true' or call.data == 'snow_false':
        if call.data == 'snow_true':
            conditions['snow'] = True
        else:
            conditions['snow'] = False
        text = 'Проверьте введенные данные:\n\n\n'
        if 'type' in work_type:
            text += 'Вид проводимых работ: ' + work_type['type'] + '\n\n'
        if 'min_temp' in conditions:
            text += 'Мин. допустимая температура: ' + conditions['min_temp'] + '\n\n'
        if 'max_temp' in conditions:
            text += 'Макс. допустимая температура: ' + conditions['max_temp'] + '\n\n'
        if 'rainfall' in conditions:
            if conditions['rainfall'] == True:
                text += 'Возможно проводить в дождь: Да' + '\n\n'
            else:
                text += 'Возможно проводить в дождь: Нет' + '\n\n'
        if 'snow' in conditions:
            if conditions['snow'] == True:
                text += 'Возможно проводить в снегопад: Да' + '\n'
            else:
                text += 'Возможно проводить в снегопад: Нет' + '\n'
        keyboard4 = types.InlineKeyboardMarkup()
        buttonfile = types.InlineKeyboardButton(text='Сохранить', callback_data='save_file')
        buttonfile1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_file')
        keyboard4.add(buttonfile, buttonfile1)
        bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard4)

    if call.data == 'save_file':
        filesave = open('work_types.json', 'r', encoding='utf-8')
        worktypes = json.load(filesave)
        filesave.close()
        filesave1 = open('work_types.json', 'w', encoding='utf-8')
        worktypes.append({
            **work_type,
            "conditions": {
                **conditions
            }
        })
        json.dump(worktypes, filesave1, ensure_ascii=False)
        filesave1.close()
        bot.send_message(call.message.chat.id, text='Вид проводимых работ успешно сохранен')
        bot_start_window(call)

    if call.data == 'edit_file':
        is_edit = True
        keyboard3 = types.InlineKeyboardMarkup()
        button_edit_work_type = types.InlineKeyboardButton(text='Вид работ', callback_data='edit_file_work_type')
        button_edit_min_temp = types.InlineKeyboardButton(text='Мин. температура', callback_data='edit_file_min_temp')
        button_edit_max_temp = types.InlineKeyboardButton(text='Макс. температура', callback_data='edit_file_max_temp')
        button_edit_rainfall = types.InlineKeyboardButton(text='Дождь', callback_data='edit_file_rainfall')
        button_edit_snow = types.InlineKeyboardButton(text='Снег', callback_data='edit_file_snow')
        keyboard3.add(button_edit_work_type, button_edit_min_temp, button_edit_max_temp, button_edit_rainfall, button_edit_snow)
        bot.send_message(call.message.chat.id, text='Выберите, что редактировать', reply_markup=keyboard3)


    if call.data == 'edit_file_work_type':
        bot.send_message(call.message.chat.id, text='Введите название вида работ')
        bot.register_next_step_handler(call.message, edit_work_type)

    if call.data == 'edit_file_min_temp':
        bot.send_message(call.message.chat.id, text='Укажите минимальную температуру')
        bot.register_next_step_handler(call.message, edit_min_temp)

    if call.data == 'edit_file_max_temp':
        bot.send_message(call.message.chat.id, text='Укажите максимальную температуру')
        bot.register_next_step_handler(call.message, edit_max_temp)

    if call.data == 'edit_file_rainfall':
        bot.send_message(call.message.chat.id, text='Можно проводить в дождь',  reply_markup=keyboard1)
        bot.register_next_step_handler(call.message, edit_rainfall)

    if call.data == 'edit_file_snow':
        bot.send_message(call.message.chat.id, text='Можно проводить в снег', reply_markup=keyboard2)
        bot.register_next_step_handler(call.message, edit_snow)


    elif call.data == 'График проведения работ':
        text = 'Выберите вид работ для изменения графика проведения (в сообщении отправьте только номер)\n\n\n'
        file1 = open('work_types.json', 'r', encoding='utf-8')
        worktypes = json.load(file1)
        file1.close()
        for i in range(len(worktypes)):
            text += str(i + 1) + '. ' + worktypes[i]['type'] + '\n\n'
        bot.send_message(call.message.chat.id, text=text)
        bot.register_next_step_handler(call.message, add_date_start)

    if call.data == 'edit_file':
        is_edit = True
        keyboard11 = types.InlineKeyboardMarkup()
        # edit_file_work_type1 = types.InlineKeyboardButton(text='Вид работ', callback_data='edit_file_work_type1')
        edit_file_date_start = types.InlineKeyboardButton(text='Начало', callback_data='edit_file_date_start')
        edit_file_date_end = types.InlineKeyboardButton(text='Конец', callback_data='edit_file_date_end')

    if call.data == 'save_file1':
        filesave = open('grafik.json', 'r', encoding='utf-8')
        date = json.load(filesave)
        filesave.close()
        filesave1 = open('grafik.json', 'w', encoding='utf-8')
        json.dump(date, filesave1, ensure_ascii=False)
        filesave1.close()
        bot.send_message(call.message.chat.id, text='Вид проводимых работ успешно сохранен')

    if call.data == 'edit_file_date_start':
        bot.send_message(call.message.chat.id, text='Укажите дату начало проведения работ')
        bot.register_next_step_handler(call.message, edit_min_temp)

    if call.data == 'edit_file_date_end':
        bot.send_message(call.message.chat.id, text='Укажите дату окончания проведения работ')
        bot.register_next_step_handler(call.message, edit_max_temp)

def checkWeather():
    constparams = {
        'lat': 57.928041,
        'lon': 60.011935,
        'lang': 'ru_RU',  # язык ответа
    }
    response = requests.get('https://api.weather.yandex.ru/v2/forecast', params={
            **constparams,
            "limit": 1,
        }, headers={'X-Yandex-API-Key': 'ecb87eb8-2518-430f-b693-b6b895672814'})
    data = response.json()
    forecast = data['forecasts'][-1]
    return forecast

def periodicSendMessage():
    global next_message_on
    while True:
        if datetime.now() > next_message_on:
            next_message_on = datetime.now() + timedelta(days=1)
            file = open('work_types.json', 'r', encoding='utf-8')
            if file.read() != '':
                file.seek(0)
                work_types = json.load(file)
            file.close()

            # Сообщение с прогнозом погоды на сегодняшний день
            forecast = checkWeather()
            textWeather = 'Прогноз погоды на сегодня: \n\n'
            textWeather += 'Температура воздуха утром: ' + str(forecast['parts']['morning']['temp_avg']) + ' °C\n'
            textWeather += 'Скорость ветра утром: ' + str(forecast['parts']['morning']["wind_speed"]) + ' м/с\n\n'
            textWeather += 'Температура воздуха днём: ' + str(forecast['parts']['day']['temp_avg']) + ' °C\n'
            textWeather += 'Скорость ветра днём: ' + str(forecast['parts']['day']["wind_speed"]) + ' м/с\n\n'
            textWeather += 'Температура воздуха вечером: ' + str(forecast['parts']['evening']['temp_avg']) + ' °C\n'
            textWeather += 'Скорость ветра вечером: ' + str(forecast['parts']['evening']["wind_speed"]) + ' м/с\n\n'
            textWeather += 'Давление: ' + str(forecast['parts']['day']["pressure_mm"]) + ' мм рт. ст.\n\n'
            textWeather += 'Влажность: ' + str(forecast['parts']['day']["humidity"]) + ' %\n\n'
            textWeather += 'Время восхода: ' + str(forecast["sunrise"]) + '\n'
            textWeather += 'Время заката: ' + str(forecast["sunset"]) + '\n\n\n\n'
            avgTemp = forecast['parts']['day']['temp_avg']
            condition = forecast['parts']['day']['condition']
            for work in work_types:
                if 'employer' in work:
                    dateStart = datetime.strptime(work["date_start"], '%d.%m.%Y')
                    dateEnd = datetime.strptime(work["date_end"], '%d.%m.%Y')
                    if (datetime.today().date() < dateStart.date()) or (datetime.today().date() > dateEnd.date()):
                        continue
                    employer = work["employer"]
                    text = 'Здравствуйте, ' + employer["fio"] + ', напоминаем Вам, что сегодня Вам необходимо выполнить работу: ' + work["type"]
                    work_success = True
                    addedText = ''
                    try:
                        notify_bot.send_message(employer['link'], text)
                        notify_bot.send_message(employer['link'], textWeather)
                        # Сообщение с информацие по проведению работы 
                        if (int(work['conditions']['min_temp']) > avgTemp) or (int(work['conditions']['max_temp']) > avgTemp):
                            work_success = False
                            if int(work['conditions']['min_temp']) > avgTemp:
                                addedText += 'Температура не соответствует необходимой норме.\n Минимальная температура для выполнения работ: ' + str(work['conditions']['min_temp']) + '\nСегодняшняя средняя температура: ' + str(avgTemp) + '\n\n'
                            else:
                                addedText += 'Температура не соответствует необходимой норме.\n Максимальная температура для выполнения работ: ' + str(work['conditions']['max_temp']) + '\nСегодняшняя средняя температура: ' + str(avgTemp) + '\n\n'
                        if condition in ['rain', 'light-rain', 'heavy-rain', 'showers', 'thunderstorm-with-rain', 'thunderstorm', 'wet-snow']:
                            if not work['conditions']['rainfall']:
                                work_success = False
                                addedText += 'В дождливые дни работы не проводятся. Сегодня ожидается дождь\n\n'
                        if condition in ['wet-snow', 'light-snow', 'snow', 'snow-showers', 'hail', 'thunderstorm-with-hail' ]:
                            if not work['conditions']['snow']:
                                work_success = False
                                addedText += 'В дни снегопада работы не проводятся. Сегодня ожидается снег\n\n'
                        if not work_success:
                            notify_bot.send_message(employer['link'], 'В связи с погодными условиями работы проводиться не будут.\n\nПояснение:\n' + addedText)
                    except:
                        continue
        time.sleep(1)

if __name__ == "__main__":
    Thread(target=periodicSendMessage).start()
    bot.polling(none_stop=True, interval=0)
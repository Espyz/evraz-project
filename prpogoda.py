import requests
import telebot
import datetime
from telebot import types
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE, CallbackData
from telebot.types import CallbackQuery, ReplyKeyboardRemove

bot = telebot.TeleBot('7042146009:AAH3cpSEDCDU9y0qa9JsKBCyWXYnFgNhyDM')
# Задаем значение ключа API
api_key = 'ecb87eb8-2518-430f-b693-b6b895672814'
# Задаем URL API
url = 'https://api.weather.yandex.ru/v2/forecast'

# Создаём календарь
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")
calendar = Calendar(RUSSIAN_LANGUAGE)

#Создадим константу месяцев
months = [ '', ' января ', ' февраля ', ' марта ', ' апреля ', ' мая ', ' июня ', ' июля ', ' августа ', ' сентября ', ' октября ', ' ноября ', ]


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/start':
        # Создание меню с командами
        bot.set_my_commands(
            commands=[
                types.BotCommand('/start', 'Начать работу с ботом'),
            ],
            scope=types.BotCommandScopeChat(message.chat.id)
        )
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Сегодня', callback_data='Сегодня')
        button2 = types.InlineKeyboardButton(text='Неделя', callback_data='Неделя')

        keyboard.add(button1, button2)
        now = datetime.datetime.now()
        newCalendar = calendar.create_calendar(
                name=calendar_1.prefix, # Specify the NAME of your calendar
                year=now.year,
                month=now.month)
        bot.send_message(message.from_user.id, text='Привет! Добро пожаловать')
        bot.send_message(message.from_user.id, text="Выбери день для отображения погоды в пределах 7 дней", reply_markup=newCalendar)

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_worker(call):
    global name, data
    # bot.send_message(call.from_user.id, text='Вы нажали на кнопку - ' + call.data + ' ')
    #Обрабатываем кнопки переключения месяцев и выхода
    try:
        name, action, year, month, day = call.data.split(calendar_1.sep)
        calendar.calendar_query_handler(
            bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
        try:
            takeDate = call.data.split(':')[2::]
            takeDate = datetime.datetime.strptime('-'.join(takeDate), '%Y-%m-%d')
            now = datetime.datetime.now()
        except:
            return


        constparams = {

            'lat': 57.928041,

            'lon': 60.011935,

            'lang': 'ru_RU',  # язык ответа

        }
        delta = takeDate - now
        print(delta.days)
        if delta.days > 5:
            raise
        # Делаю +2 т.к. при количестве дней = 1 возвращаетсяя текущая дата
        response = requests.get(url, params={
            **constparams,
            "limit": delta.days + 2,
        }, headers={'X-Yandex-API-Key': api_key})

        data = response.json()
        forecast = data['forecasts'][-1]
        [day, month, year] = forecast["date"].split('-')[::-1]
        print(day, month, year)
        # Выводим данные о текущей погоде
        text = 'Дата: ' + day + months[int(month)] + year + ' года\n\n'
        text += 'Температура воздуха утром: ' + str(forecast['parts']['morning']['temp_avg']) + ' °C\n'
        text += 'Скорость ветра утром: ' + str(forecast['parts']['morning']["wind_speed"]) + ' м/с\n\n'
        text += 'Температура воздуха днём: ' + str(forecast['parts']['day']['temp_avg']) + ' °C\n'
        text += 'Скорость ветра днём: ' + str(forecast['parts']['day']["wind_speed"]) + ' м/с\n\n'
        text += 'Температура воздуха вечером: ' + str(forecast['parts']['evening']['temp_avg']) + ' °C\n'
        text += 'Скорость ветра вечером: ' + str(forecast['parts']['evening']["wind_speed"]) + ' м/с\n\n'
        text += 'Давление: ' + str(forecast['parts']['day']["pressure_mm"]) + ' мм рт. ст.\n\n'
        text += 'Влажность: ' + str(forecast['parts']['day']["humidity"]) + ' %\n\n'
        text += 'Время восхода: ' + str(forecast["sunrise"]) + '\n'
        text += 'Время заката: ' + str(forecast["sunset"]) + '\n\n\n\n'
        bot.send_message(call.from_user.id, text=text, parse_mode='Markdown')
    except:
        bot.send_message(call.from_user.id, text='Мы не можем спрогнозировать погоду на данную дату. Пожалуйста выбирайте дату в пределах 7 дней')

bot.polling(none_stop=True, interval=0)
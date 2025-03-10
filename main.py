import telebot
from telebot import types
import webbrowser
import model,model2
import warnings
warnings.filterwarnings("ignore")
import sqlite3

md = model.Model()
md2 = model2.Model()

import token
bot = telebot.TeleBot(token)

@bot.message_handler(commands=["show_data"])
def show_data(message):
    try:
        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()
        cur.execute("SELECT * from data")
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'Данные: {el[1]} ; метка: {el[2]}\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id,info)
    except Exception:
        bot.send_message(message.chat.id,"Пусто")


@bot.message_handler(commands=['users'])
def show_users(message):
    try:
        conn = sqlite3.connect('dmih.sql')
        cur = conn.cursor()
        cur.execute("SELECT * from users")
        users = cur.fetchall()
        info = ''
        for el in users:
            info += f'Имя: {el[1]}, пароль: {el[2]},tg_id: {el[3]}\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id,info)
    except Exception:
        bot.send_message(message.chat.id,"Пусто")


@bot.message_handler(commands=['registration'])
def registration(message:telebot.types.Message):

    conn = sqlite3.connect('dmih.sql')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users 
                (id int auto_increment primary key,
                name varchar(50),pass varchar(50),
                tg_id varchar(50))""")
    cur.execute("SELECT tg_id from users where tg_id = '%s'"%(message.from_user.id))
    received_id = cur.fetchall()
    print(received_id)
    
    conn.commit()
    cur.close()
    conn.close()
    if len(received_id)==0:
        bot.send_message(message.chat.id,'Привет! Сейчас зарегистрирую тебя, напиши своё имя')
        bot.register_next_step_handler(message,user_name)
    else:
        bot.send_message(message.chat.id,"Ты уже зарегистрирован!")
        
name = None
def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id,'Введите пароль')
    bot.register_next_step_handler(message,user_pass)


def user_pass(message):
    password = message.text.strip()
    tg_id = message.from_user.id
    conn = sqlite3.connect('dmih.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users(name,pass,tg_id) VALUES('%s','%s','%s')"%(name,password,tg_id))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список пользователей',callback_data='show_users'))
    bot.send_message(message.chat.id,'Вы зарегестрированы!',reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'show_users')
def callback_show_users(call):
    show_users(call.message)



@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name != None else ""
    bot.send_message(message.chat.id ,f"Привет {name} {last_name}😚😚\nПришли мне сообщение и я оценю его тональность")


    
API_KEY = "93a88a3a688731963bd9931fe60cafaa"    
import requests

user = {"state":""}
@bot.message_handler(commands=['weather'])
def get_weather(message):
    bot.send_message(message.chat.id,"Введите ваш город")
    user['state'] = 'typing city'


@bot.message_handler(content_types=['text'])
def choose_func(message):
    state = user['state']
    if state == 'typing city':
        weather(message)
        user['state'] = ""
    else:
        assess_tone(message)

import json

def weather(message):
    city = message.text.strip().lower()
    weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric")
    if weather.status_code == 200:
        data = json.loads(weather.text)
        w = data['main']['temp']
        answer = f"Сейчас : {w} градусов"
        emoji = "🥶" if w < 5 else "☺️"
        answer += emoji
        bot.reply_to(message,answer)
    else:
        bot.reply_to(message,"Город не найден🥺")

import random

text = []
def assess_tone(message):
    global text
    print(message.text)
    text = [message.text]
    prediction = md.predict(text)
    proba = md.predict_proba(text)
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Разметить самому",callback_data='mark_data')
    markup.add(button1)
    if prediction==1:
        bot.reply_to(message,f"Ваше сообщение позитивное с вероятностью {proba[1]}",reply_markup=markup)
    else:
        bot.reply_to(message, f"Ваше сообщение негативное с вероятностью {proba[0]}",reply_markup=markup)

    prediction2 = md2.predict(text)
    proba2 = md2.predict_proba(text)
    bot.reply_to(message,f"Вероятность оскорбления: {proba2[1]}",reply_markup=markup)
    if proba2[1] > 0.8 and random.randint(0,100) >= 75:
        bot.reply_to(message,"Хватит ругаться!!! Лучше почеши мне спинку")


@bot.callback_query_handler(func= lambda call: call.data == 'mark_data')
def mark_data(call):
    markup = types.InlineKeyboardMarkup()
    pos = types.InlineKeyboardButton("Позитивное",callback_data='marked_pos')
    neg = types.InlineKeyboardButton("Негативное",callback_data='marked_neg')
    offensive = types.InlineKeyboardButton("Оскорбление",callback_data='marked_off')
    difficult = types.InlineKeyboardButton("Затрудняюсь",callback_data='marked_diff')
    markup.add(pos,neg,offensive,difficult)
    bot.send_message(call.message.chat.id,"Выберите вариант разметки",reply_markup=markup)


possible_marks = ['marked_pos','marked_neg','marked_off','marked_diff'] 
    
@bot.callback_query_handler(func= lambda call: call.data in possible_marks)
def write_in_db(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == "marked_diff":
            bot.send_message(call.message.chat.id,"😔")
            return
    mark = ""
    if call.data == 'marked_pos':
        mark = 'positive'
    if call.data == 'marked_neg':    
        mark = 'negative'
    if call.data == 'marked_off':
        mark = 'offensive'
    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS data
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                mark varchar(15))
                """)
    cur.execute("INSERT INTO data (data, mark) VALUES (?, ?)", (*text, mark))
    conn.commit()
    cur.close()
    conn.close()
    


    
    


    
  




    
    
import matplotlib.pyplot as plt
import numpy as np
import os
@bot.message_handler(content_types=['photo'])
def assess_photo(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Перейти на сайт",url='https://vk.com/')
    markup.row(button1)
    bot.reply_to(message,"У вас замечательное фото!",reply_markup=markup)


    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
        title='About as simple as it gets, folks')
    ax.grid()

    fig.savefig("test.png")
    with open("test.png",'rb') as photo:
        bot.send_photo(message.chat.id,photo)
    os.remove("test.png")

    
    
@bot.callback_query_handler(func=lambda callback:True)
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id,callback.message.message_id-1)
    elif callback.data == 'edit':
        bot.edit_message_text(callback.message.chat.id,callback.message.message_id)

bot.polling(non_stop=True)
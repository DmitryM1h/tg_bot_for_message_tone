import telebot
from telebot import types
import webbrowser
import model,model2
import warnings
warnings.filterwarnings("ignore")
import sqlite3

md = model.Model()
md2 = model2.Model()
bot = telebot.TeleBot("tokenhere")

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
    markup.add(types.InlineKeyboardButton('Список пользователей',callback_data='users'))
    bot.send_message(message.chat.id,'Вы зарегестрированы!',reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('dmih.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]},tg_id: {el[3]}\n'
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id,info)



@bot.message_handler(commands=['start'])
def start(message):
    '''markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton("Перейти на сайт")
    button2 = types.KeyboardButton("Удалить фото")
    button3 = types.KeyboardButton("Изменить текст")'''
    
    '''markup.row(button1,button2)
    markup.row(button3)'''
    name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name != None else ""
    bot.send_message(message.chat.id ,f"Привет {name} {last_name}😚😚\nПришли мне сообщение и я оценю его тональность")
    #bot.register_next_step_handler(message,on_click)

def on_click(message):
    if message.text == 'Перейти на сайт':
        bot.send_message(message.chat.id,'Вебсайт открыт')
    elif message.text == 'Удалить фото':
        bot.send_message(message.chat.id,'Удалено')


import random

@bot.message_handler(content_types=['text'])
def assess_tone(message):
    print(message.text)
    text = [message.text]
    prediction = md.predict(text)
    prediction2 = md2.predict(text)
    proba2 = md2.predict_proba(text)
    proba = md.predict_proba(text)
    if prediction==1:
        bot.reply_to(message,f"1)Ваше сообщение позитивное с вероятностью {proba[1]}")
    else:
        bot.reply_to(message, f"1)Ваше сообщение негативное с вероятностью {proba[0]}")
    '''if prediction2==1:
        bot.reply_to(message,f"2)Ваше сообщение позитивное с вероятностью {proba2[1]}")
    else:
        bot.reply_to(message, f"2)Ваше сообщение негативное с вероятностью {proba2[0]}")'''
import matplotlib.pyplot as plt
import numpy as np
import os
@bot.message_handler(content_types=['photo'])
def assess_photo(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Перейти на сайт",url='https://vk.com/')
    #button2 = types.InlineKeyboardButton("Удалить фото",callback_data='delete')
    #button3 = types.InlineKeyboardButton("Изменить текст",callback_data='edit')
    markup.row(button1)
    #markup.row(button3)
    bot.reply_to(message,"У вас замечательное фото!",reply_markup=markup)
    # Data for plotting
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
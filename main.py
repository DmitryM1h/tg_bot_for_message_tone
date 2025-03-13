import telebot
from telebot import types
import model,model2
import warnings
warnings.filterwarnings("ignore")
import sqlite3
import abstract_model as abm

class curr_model(abm.Imodel):

    def set(self,model):
        self.model = model
    
    def prepare(self,text):
        return self.model.prepare(text)

    def predict(self,text):
        return self.model.predict(text)

    def predict_proba(self,text):
        return self.model.predict_proba(text)



md = curr_model()
models = {
    'tone':model.Log_reg_tone(),
    'agression':model2.Log_reg_agression() }
md.set(models['agression'])

token = None
with open("tg_token.txt") as f:
    token = f.read().strip()

bot = telebot.TeleBot(token)

@bot.message_handler(commands=["mode"])
def set_mode(message):
    markup = types.InlineKeyboardMarkup()
    tone = types.InlineKeyboardButton("Оценка тональности",callback_data="chose_tone")
    aggressive = types.InlineKeyboardButton("Оценка на агрессивность",callback_data="chose_agression")
    markup.add(tone,aggressive)
    bot.send_message(message.chat.id,"Выберите режим",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['chose_tone','chose_agression'])
def callback_chose_mode(call):
    if call.data == 'chose_tone':
        md.set(models['tone'])
    elif call.data == 'chose_agression':
        md.set(models['agression'])


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



@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name != None else ""
    bot.send_message(message.chat.id ,f"Привет {name} {last_name}😚😚\nПришли мне сообщение и я оценю его тональность")


text = []
@bot.message_handler(content_types=['text'])
def assess_tone(message):
    global text
    print(message.text)
    text = [message.text]
    print(text)
    prediction = md.predict_proba(text)
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Разметить самому",callback_data='mark_data')
    markup.add(button1)  
    bot.reply_to(message,prediction,reply_markup=markup)
    
    #bot.reply_to(message,"Хватит ругаться!!! Лучше почеши мне спинку")


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
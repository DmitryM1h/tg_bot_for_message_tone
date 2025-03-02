import telebot
import webbrowser
import model
import warnings
warnings.filterwarnings("ignore")


md = model.Model()
bot = telebot.TeleBot("#tokenHere#")

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id,f"Привет {message.from_user.first_name} {message.from_user.first_name}")

@bot.message_handler()
def info(message):
    text = [message.text]
    prediction = md.predict(text)
    proba = md.predict_proba(text)
    if prediction==1:
        bot.send_message(message.chat.id,f"Ваше сообщение позитивное с вероятностью {proba[1]}")
    else:
        bot.send_message(message.chat.id, f"Ваше сообщение негативное с вероятностью {proba[0]}")



bot.polling(non_stop=True)





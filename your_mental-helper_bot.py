from googletrans import Translator
import telebot
from telebot import types
import random
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os
from dotenv import load_dotenv
from config import (MODEL_NAME, MEDITATION_PATHS, INTERESTING_FACTS,
                    USEFUL_RESOURCES, STUDY_PATH,
                    QUESTIONS, GOOD_PHOTO_PATH,
                    NORMAL_PHOTO_PATH, BAD_PHOTO_PATH,
                    GOOD_ITOG_PATH, BAD_ITOG_PATH,
                    THANKS_PATH, GOOD_RESPONSES,
                    NORMAL_RESPONSES
                    )

load_dotenv()

# Инициализация переводчика
translator = Translator()

# Инициализация бота
TOKEN = os.getenv('MENTAL_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Загрузка предобученной модели EmoRoBERTa для анализа эмоций на английском языке
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
emotion_analysis = pipeline(
    "text-classification", 
    model=model, 
    tokenizer=tokenizer, 
    top_k=None  # Это заменяет return_all_scores=True
)

"""Функции"""

# Команда для получения интересных фактов
@bot.message_handler(func=lambda message: message.text.lower() == "факты")
def send_fact(message):
    bot.send_message(message.chat.id, random.choice(INTERESTING_FACTS))

# Команда для получения интересных статей
@bot.message_handler(func=lambda message: message.text.lower() == "статьи")
def send_articles(message):
    bot.send_message(message.chat.id, random.choice(USEFUL_RESOURCES))

# Обработчик текстовых сообщений с ключевыми словами "анализ эмоций" или "эмоция"
@bot.message_handler(func=lambda message: 'анализ эмоций' in message.text.lower() or 'эмоция' in message.text.lower())
def analyze_emotion_text(message):
    user_text = message.text
    # Перевод текста на английский
    translated_text = translator.translate(user_text, dest='en').text
    # Анализ эмоций
    emotion_result = emotion_analysis(translated_text)
    # Отправка результата анализа эмоций
    response = "Результаты анализа эмоций:\n"
    for result in emotion_result[0]:
        response += f"{result['label']}: {result['score']}\n"
    bot.reply_to(message, response)

# Команда для медитации
@bot.message_handler(func=lambda message: message.text.lower() == "медитация")
def send_meditation(message):
    with open(random.choice(MEDITATION_PATHS), 'rb') as audio:
        bot.send_audio(message.chat.id, audio)

# Функция для обработки сообщений с благодарностями
@bot.message_handler(func=lambda message: message.text.lower() in ['спасибо', 'спс'])
def thanks_message(message):
    bot.send_message(message.chat.id, "Спасибо, мне было приятно общаться с тобой!")
    # Отправка милой картинки
    with open(THANKS_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

# Команда для медитации
@bot.message_handler(func=lambda message: message.text.lower() == "учеба")
def send_study(message):
    with open(random.choice(STUDY_PATH), 'rb') as audio:
        bot.send_audio(message.chat.id, audio)

# Функция для обработки сообщений с приветствием
@bot.message_handler(func=lambda message: message.text.lower() in ['привет', 'здарова', 'хай', 'прив', 'вассап'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Хорошо")
    item2 = types.KeyboardButton("Нормально")
    item3 = types.KeyboardButton("Плохо")
    markup.add(item1, item2, item3)
    bot.reply_to(message, 'Привет, я Твой Ментальный помощник! Можешь написать такие команды: медитация, учеба, факты, статьи, анализ эмоций (после данной команды нужно сразу описать ваше настроение, в одном сообщении с командой) или просто ответить на мой вопрос. Как ваше настроение сегодня?', reply_markup=markup)

# Функция для обработки ответов пользователя
@bot.message_handler(content_types=['text'])
def handle_message(message):
    text = message.text.lower()
    chat_id = message.chat.id

    if text in ['хорошо', 'нормально', 'плохо']:
        if text == "хорошо":
            with open(random.choice(GOOD_PHOTO_PATH), 'rb') as photo:
                bot.send_photo(chat_id, photo)
            bot.send_message(chat_id, random.choice(GOOD_RESPONSES))
        elif text == "нормально":
            with open(random.choice(NORMAL_PHOTO_PATH), 'rb') as photo:
                bot.send_photo(chat_id, photo)
            bot.send_message(chat_id, random.choice(NORMAL_RESPONSES))
        elif text == "плохо":
            with open(random.choice(BAD_PHOTO_PATH), 'rb') as photo:
                bot.send_photo(chat_id, photo)
            bot.send_message(chat_id, "Не переживайте, давайте проведем небольшое тестирование, после которого я смогу попробовать Вам оперативно помочь.")
            ask_question(message, 0, 0)
    else:
        bot.reply_to(message, 'Извините, я вас не понял. Пожалуйста, напишите "привет", чтобы начать диалог.')

# Функция для задания вопросов
def ask_question(message, index, yes_count):
    chat_id1 = message.chat.id
    if index < len(QUESTIONS):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Да", "Нет")
        bot.send_message(message.chat.id, QUESTIONS[index], reply_markup=markup)
        bot.register_next_step_handler(message, lambda m: process_answer(m, index, yes_count))
    else:
        if yes_count >= 3:
            with open(random.choice(BAD_ITOG_PATH), 'rb') as photo:
                bot.send_photo(chat_id1, photo)
            bot.send_message(message.chat.id, "Уделите время своим хобби и интересам, чтобы отвлечься от учебных проблем и расслабиться. Помните, что стресс - это нормальная реакция на жизненные трудности, но важно научиться контролировать свои эмоции и реагировать на стресс в здоровой и продуктивной манере. Если вы чувствуете, что не можете справиться со стрессом самостоятельно, обратитесь за помощью к специалисту, такому как психолог. Это совсем не страшно.")
        else:
            with open(random.choice(GOOD_ITOG_PATH
                                    ), 'rb') as photo:
                bot.send_photo(chat_id1, photo)
            bot.send_message(message.chat.id, "Я посчитал, что у Вас умеренный уровень стресса, для профилактики советуем Вам попробовать уделять время практике медитации и дыхательным упражнениям, чтобы снизить уровень стресса и настроиться на позитивное мышление. А также помнить, что стресс - это нормальная реакция на жизненные трудности, но важно научиться контролировать свои эмоции и реагировать на стресс в здоровой и продуктивной манере. Напишите - медитация и бот запустит необходимое сопровождение")

# Функция для обработки ответов на вопросы
def process_answer(message, index, yes_count):
    if message.text.lower() == "да":
        yes_count += 1
    ask_question(message, index + 1, yes_count)

"""Активация бота"""

# Запуск бота
bot.polling(none_stop=True, skip_pending=True)
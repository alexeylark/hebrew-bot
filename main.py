import telebot
from telebot import types
import test_engine as te
import time
import re
import json
import db_google_cloud as db
import custom_localization as lozi
import sys, traceback
import os
from google.cloud import pubsub_v1


is_debug = False
bot = telebot.TeleBot(token=os.environ.get('TOKEN'),allow_sending_without_reply=False)
test_chat_id = os.environ.get('TEST_CHAT_ID')

project_id = os.environ.get("PROJECT_ID")
topic_id = os.environ.get("REQUEST_TOPIC_ID")
batch_settings = pubsub_v1.types.BatchSettings(max_latency=3) 
publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)
topic_path = publisher.topic_path(project_id, topic_id)


def send_message(update, message_code, sleep_time=0, markup=None, no_localization=False, force_message=False):
    chat_id = update['chat_id']
    if sleep_time != 0:
        time.sleep(sleep_time)

    if is_debug:
        chat_id = test_chat_id
    
    if no_localization:
        lang = update['lang']
    else:
        lang = db.get_language(update)
    
    if force_message:
        message = message_code
    else:
        message = lozi.get_message(message_code, lang)   
    
    bot.send_message(chat_id, message, reply_markup = markup)

    data = {'user_id': update['user_id'], 
        'chat_id': update['chat_id'],
        'username': update['username'],
        'first_name': update['first_name'],
        'last_name': update['last_name'],
        'user_lang': update['user_lang'],
        'lang': update['lang'],
        'is_callback': update['is_callback'],
        'message_id': update['message_id'],
        'message_dt': update['message_dt'], 
        "output_message": message}

    publisher.publish(topic_path, data=json.dumps(data).encode("utf-8"), event_type="on_message_sent")


def update_language(update):
    db.set_language(update)
    send_message(update, 'set_lang_success')


def update_level(update):
    db.set_level(update)
    send_message(update, 'set_level_success')


def set_language_reply(update):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='English', callback_data='en'))
    markup.add(types.InlineKeyboardButton(text='Русский', callback_data='ru'))
    send_message(update, 'set_lang', sleep_time=0.5, markup=markup)
    

def set_level_reply(update):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='א', callback_data='alef'))
    markup.add(types.InlineKeyboardButton(text='א+', callback_data='alef_plus'))
    #markup.add(types.InlineKeyboardButton(text='ב', callback_data='bet'))
    #markup.add(types.InlineKeyboardButton(text='ב+', callback_data='bet_plus'))
    send_message(update, 'set_level', sleep_time=0.5, markup=markup)


def set_test_mode_reply(update):
    markup = types.InlineKeyboardMarkup()
    lang = db.get_language(update)
    markup.add(types.InlineKeyboardButton(lozi.get_message('verbs', lang), callback_data='verbs'))
    markup.add(types.InlineKeyboardButton(lozi.get_message('nouns', lang), callback_data='nouns'))
    markup.add(types.InlineKeyboardButton(lozi.get_message('adjectives', lang), callback_data='adjectives'))
    markup.add(types.InlineKeyboardButton(lozi.get_message('shuffle', lang), callback_data='shuffle'))
    send_message(update, 'set_test_mode', sleep_time=0.5, markup=markup)


def start(update):
    db.add_user(update)
    db.add_words(update, 'alef')
    send_message(update, 'welcome', 0.5)
    send_message(update, 'lang', 1)
 #   send_message(update, 'test', 1)

    
def test(update):
    word_type, picked_words, lang = te.get_test_words(update)

    match word_type:
        case 'verb': word_code='v'
        case 'noun': word_code='n'
        case 'adjective': word_code='a'

    markup = types.InlineKeyboardMarkup()

    for i in te.get_word_order():
        markup.add(types.InlineKeyboardButton(text=picked_words[i]['word'], 
            callback_data=word_code + str(i) + lang + str(picked_words[i]['id']) + picked_words[0]['word']))

    send_message(update, picked_words[0]['translation'], 0, markup=markup, force_message=True)  


def check_result(update):
    answer_num = update['callback_data'][1]
    answer_id = re.sub("[^0-9]", "", update['callback_data'][4:])
    button_data = update['reply_markup']
    k = [obj[0].callback_data for obj in button_data]
    right_word = re.sub('[0-9]+', "", update['callback_data'][4:])
    k.sort(key=lambda x: int(x[1]))
    ids = ",".join([re.sub("[^0-9]", "", n[4:]) for n in k])
    word_type = k[0]
    update['lang'] = update['callback_data'][2:4]
    
    if int(answer_num) == 0:
        send_message(update, 'right', 0, no_localization=True)
    else:
        send_message(update, lozi.get_message('wrong', update['lang']) + right_word, 0, force_message=True)
    test(update)
    db.add_question(update, ids, answer_id, word_type)


def stop(update):
    send_message(update, 'stop')


def extract_update(request_json):
    update = telebot.types.Update.de_json(request_json)
    
    if update.callback_query is not None:
        is_callback = True
        callback = update.callback_query
    else:
        is_callback = False
        callback = None
    
    if is_callback:
        user_dict = callback.from_user.to_dict()
        callback_id = callback.id
        callback_data = callback.data
        message = callback.message
        reply_markup = message.reply_markup.keyboard
    else:
        message = update.message
        user_dict = message.from_user.to_dict()
        callback_id = None
        callback_data = None    
        reply_markup = None

    user_lang = user_dict['language_code']
    if user_lang in ('ru', 'be', 'uk'):
        lang = 'ru' 
    else:
        lang = 'en'

    event_info = {
    'user_id': user_dict['id'],
    'chat_id': message.chat.id,
    'username': user_dict['username'],
    'first_name': user_dict['first_name'], 
    'last_name': user_dict['last_name'], 
    'user_lang': user_dict['language_code'],
    'lang': lang,
    'is_callback': is_callback,
    'message_id': message.id,
    'message_dt': message.date,
    'message_text': message.text,
    'callback_id': callback_id,
    'callback_data': callback_data,
    'reply_markup': reply_markup
    }
    return event_info
    

def handler(request_json):

    update = extract_update(request_json)

    if update['is_callback'] == True:
        if lozi.get_key_by_message(update['message_text']) == 'set_lang':
            update_language(update)
        elif lozi.get_key_by_message(update['message_text']) =='set_level':
            update_level(update)
        else:
            check_result(update)

        bot.answer_callback_query(update['callback_id'])
    else:
        if update['message_text'] == '/start':
            start(update)
        if update['message_text'] == '/test_verbs':
            db.set_test_mode(update, 'verbs')
            test(update)
        if update['message_text'] == '/test_adjectives':
            db.set_test_mode(update, 'adjectives')
            test(update)
        if update['message_text'] == '/test_nouns':
            db.set_test_mode(update, 'nouns')
            test(update)
        if update['message_text'] == '/test_shuffle':
            db.set_test_mode(update, 'shuffle')
            test(update)
        if update['message_text'] == '/stop':
            stop(update)
        if update['message_text'] == '/set_language':
            set_language_reply(update)
        if update['message_text'] == '/set_level':
            set_level_reply(update)
        

def google_cloud_entry_point(event):
    try:
        request_json = event.get_json()

        publisher.publish(topic_path, json.dumps(request_json).encode("utf-8"), event_type="telegram_api_request")

        handler(request_json)
    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        try:
            db.close_connection()
        except Exception:
            traceback.print_exc(file=sys.stdout)
        return ("Success", 200)


if __name__ == "__main__":
    is_debug = True
    #db.delete_user_cascade(0)
    f = open('test_jsons/answer_callback2.json')
    test_json = json.load(f)
    f.close()
    handler(json.dumps(test_json))
    db.close_connection()

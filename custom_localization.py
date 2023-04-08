import parameters


messages={
    'ru': {
        'welcome': 'Привет! Я помогу тебе выучить глаголы на иврите.'
        ,'lang': 'Я могу разговаривать на двух языках: русском и английском. Язык можно изменить командой /set_language.'
        ,'set_lang': 'Выбери предпочитаемый язык:'
        ,'test': 'Введи команду /test чтобы начать тестирование.'
        ,'right': 'Правильно!'
        ,'wrong': 'Неверно! Правильный ответ: '
        ,'stop': 'Хорошая работа, до скорого!'
        ,'set_lang_success': 'Язык успешно обновлен! Теперь я буду спрашивать тебя на русском языке.'
        ,'set_level': 'Выбери уровень подготовки:'
        ,'set_level_success': 'Отлично! Теперь я буду тестировать тебя по глаголам на этот уровень.'
    },
    'en': {
        'welcome': "Hello! I'll help you learn hebrew verbs."
        ,'lang': 'I speak two languages: English and Russian. You can change the language with /set_language command.'
        ,'set_lang': 'Choose the language you prefer:'
        ,'test': 'Enter command /test to start testing.'
        ,'right': 'Right!'
        ,'wrong': 'Wrong! Right answer: '
        ,'stop': 'Well done, see you later!'
        ,'set_lang_success': 'Language was successfully changed! Now I will test you in English.'
        ,'set_level': 'Choose your Hebrew level:'
        ,'set_level_success': 'Great! Now I will test you with verbs for this level.'
    }
}

# messages = messages[parameters.lang]
def get_message(text, lang):
    if lang == 'ru':
        return messages['ru'][text]
    else:
        return messages['en'][text]
        


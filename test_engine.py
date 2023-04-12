import random
import db_google_cloud as db

def weighted_sample(population, weights, k):
    a = list()
    for i in range(k):
        a.append(random.choices(population, weights, k=1)[0])
        b = population.index(a[i])
        del population[b]
        del weights[b]
    return a

# start
def get_test_words(update):
    test_mode = db.get_test_mode(update)
    if test_mode is None: test_mode = 'shuffle'
    match test_mode:
        case 'nouns': word_type = 'noun'
        case 'verbs': word_type = 'verb'
        case 'adjectives': word_type = 'adjective'
        case 'shuffle': word_type = random.choice(['noun', 'verb', 'adjective'])
    known_verbs = db.get_words(update, word_type)
    lang = known_verbs[0]['lang']
    asked_verbs_dict = weighted_sample(known_verbs, [row['weight'] for row in known_verbs], k=4)
    return word_type, asked_verbs_dict, lang

def get_word_order():
    return random.sample(range(0,4), k=4)



import random
import json
import db_google_cloud as db
import parameters

def weighted_sample(population, weights, k):
    a = list()
    for i in range(k):
        a.append(random.choices(population, weights, k=1)[0])
        b = population.index(a[i])
        del population[b]
        del weights[b]
    return a

class TestEngine:

    known_verbs = list()

    # start
    def initialize_words(self, user_id):
        self.known_verbs = db.get_words(user_id, 'verb')
        self.lang = self.known_verbs[0]['lang']

    def pick_words(self):
        asked_verbs_dict = weighted_sample(self.known_verbs, [row['weight'] for row in self.known_verbs], k=4)
        return asked_verbs_dict

    def get_word_order(self):
        return random.sample(range(0,4), k=4)



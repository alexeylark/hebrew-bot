from connect_connector import connect_with_connector
import pandas as pd
import datetime

def get_conn():
    db = connect_with_connector()
    conn = db.connect()
    return conn

def select_questions():
    result = None
    with get_conn() as conn:
        try: 
            sql = f"""SELECT q.* 
                    FROM questions AS q
                    INNER JOIN 
                    (
                    SELECT DISTINCT user_id
                    FROM questions
                    WHERE question_dt BETWEEN NOW() - INTERVAL '24 hour' AND NOW()
                    ) AS u ON q.user_id = u.user_id;"""
            result = pd.read_sql(sql,conn)
        finally:
            conn.close()
    return result

def create_tmp_weights_table():
    with get_conn() as conn:
        try: 
            sql = f"""
            DROP TABLE IF EXISTS tmp_weights;
            CREATE TABLE IF NOT EXISTS tmp_weights
            (
                user_id bigint,
                word_id int,
                weight float
            );
            """
            conn.execute(sql)
        finally:
            conn.close()

def insert_weights_from_df(weights_df):
    with get_conn() as conn:
        try:
            weights_df.to_sql('tmp_weights', con = conn, if_exists='append', index=False, chunksize = 1000)
        finally:
            conn.close()

def update_weights_in_db():
    with get_conn() as conn:
        try: 
            sql = f"""
            UPDATE known_words AS k 
            SET word_weight = t.weight
            FROM tmp_weights AS t
            WHERE k.user_id = t.user_id
            AND k.word_id = t.word_id;
            DROP TABLE tmp_weights;
            """
            conn.execute(sql)
        finally:
            conn.close()

def calculate_score_per_word(word_id, right_answer_id, answer_id, check):
    if check == True:
        if answer_id == word_id:
            return 2
        else:
            return 1
    elif check == False:
        if answer_id == word_id or answer_id == right_answer_id:
            return -10  
        else:
            return -3
    else:
        return None 

def time_correct_score(score, question_dt):
    question_dt = datetime.datetime.strptime(question_dt, "%Y-%m-%d %H:%M:%S")
    td = datetime.datetime.now() - question_dt
    td = td.total_seconds()/3600 #hours
    if td < 0:
        td = 0
    elif td > 720:
        td = 720
    coef = 0.5 * (1 + (720.1 - td) / 720)
    score = int(score) * coef 
    return score
   
def calculate_weights(q):
    q['variant_ids'] = q['variant_ids'].str.split(',')
    q['right_answer_id'] = q['variant_ids'].str[0]
    q['check'] = q['answer_id'].apply(str) == q['right_answer_id']
    q2 = q['variant_ids'].apply(pd.Series).stack().reset_index(level=1, drop=True)
    q = q.join(q2.to_frame()).rename({0:"word_id"}, axis=1)
    q['score'] = q.apply(lambda x: calculate_score_per_word(str(x['word_id']), str(x['right_answer_id']), str(x['answer_id']), x['check']), axis=1)
    q['score'] = q.apply(lambda x: time_correct_score(str(x['score']), str(x['question_dt'])), axis=1)
    qt = q[['user_id', 'word_id', 'score']].groupby(['user_id', 'word_id'], as_index=False).sum()
    qtt = qt[['user_id', 'score']].groupby(['user_id'], as_index=False).agg(['min', 'max'])['score'].reset_index()
    qtt['spread'] = qtt['max'] - qtt['min']
    qtt['shift'] = qtt['min']
    qt= qt.merge(qtt, on='user_id', how='inner')
    qt['new_score'] = (qt['score'] - qt['shift']) / qt['spread']
    qt['weight'] = 1 - 0.7 * qt['new_score']
    qt = qt[['user_id', 'word_id', 'weight']]
    qt['word_id'] = qt['word_id'].astype('int')
    return qt

def main():
    q = select_questions()
    if q.empty:
        print("No updates were detected")
        return 'OK'
    qt = calculate_weights(q)
    create_tmp_weights_table()
    insert_weights_from_df(qt)
    update_weights_in_db()
    return 'OK'

if __name__ == "__main__":
    main()

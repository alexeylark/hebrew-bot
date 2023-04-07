from connect_connector import connect_with_connector

db = connect_with_connector()
conn = db.connect()

def get_conn():
    return conn

def execute_sql(sql):
    res = None
    res = get_conn().execute(sql)
    return res

def add_update(update):
    sql = f"""INSERT INTO raw_updates VALUES (NOW(), '{str(update)}');"""
    execute_sql(sql)


def add_user(in_data):
    sql = f"""INSERT INTO users VALUES
        ({in_data['user_id']}, '{in_data['username']}', '{in_data['first_name']}', '{in_data['last_name']}', '{in_data['lang']}', to_timestamp({in_data['message_dt']}), '{in_data['user_lang']}')
        ON CONFLICT (id) DO NOTHING;"""
    execute_sql(sql)

def add_words(in_data, level):
    sql = f"""INSERT INTO known_words
                    SELECT {in_data['user_id']}, word_type, word_id, word_weight
                    FROM words_by_level WHERE difficulty_level = '{level}'
                    ON CONFLICT (user_id,word_id) DO NOTHING;"""
    execute_sql(sql)

def remove_words(update, level):
    sql = f"""DELETE FROM known_words
                    WHERE user_id = {update['user_id']} 
                    AND word_id IN
                    (
                        SELECT word_id 
                        FROM words_by_level 
                        WHERE difficulty_level = '{level}'
                    );"""
    execute_sql(sql)
    
def get_words(user_id, word_type):
    sql = f"""SELECT kw.word_id, w.translation, f.spelling, kw.word_weight, u.lang
                    FROM known_words AS kw
                    INNER JOIN users AS u ON kw.user_id = u.id
                    INNER JOIN {word_type}s AS w ON kw.word_id = w.id AND w.lang = u.lang
                    INNER JOIN {word_type}s_f AS f ON w.id = f.id AND w.lang = f.lang
                    WHERE kw.user_id = {user_id} 
                        AND kw.word_type = '{word_type}'
                        
                        AND f.code = 'INF-L';
            """
    result = execute_sql(sql).fetchall()

    if result is None: # if a user was created before initialization was implemented
        add_words(user_id, "alef")
        result = execute_sql(sql).fetchall()        
    
    result_dict = [dict(zip(['id','translation','word', 'weight', 'lang'], row)) for row in result]   
    return result_dict

def add_question(in_data, ids, answer_id):
    sql = f"""INSERT INTO questions VALUES 
                    ({in_data['message_id']}, to_timestamp({in_data['message_dt']}),{in_data['user_id']},'verb','{ids}',{answer_id})
                    ON CONFLICT (user_id,message_id) DO NOTHING;
            """
    execute_sql(sql)
    
def set_language(in_data):
    sql = f"""UPDATE users
            SET lang = '{in_data['callback_data']}'
            WHERE id = {in_data['user_id']};"""
    execute_sql(sql)

def set_level(update):
    level = update['callback_data']
    if level == 'alef':
        remove_words(update, 'bet')
        remove_words(update, 'bet_plus')
        remove_words(update, 'alef_plus')
    if level == 'alef_plus':
        remove_words(update, 'bet')
        remove_words(update, 'bet_plus')
        add_words(update, 'alef_plus')
    if level == 'bet':
        add_words(update, 'bet')
        add_words(update, 'alef_plus')
        remove_words(update, 'bet_plus')
    if level == 'bet_plus':
        add_words(update, 'bet')
        add_words(update, 'alef_plus')
        add_words(update, 'bet_plus')

def get_language(update):
    user_id = update['user_id']
    sql = f"""SELECT lang 
            FROM users 
            WHERE id = {user_id};"""
    result = execute_sql(sql).fetchone()[0]
    return result

def delete_user(user_id):
    sql = f"""DELETE FROM questions
            WHERE user_id = {user_id};"""
    execute_sql(sql)

    sql = f"""DELETE FROM known_words
            WHERE user_id = {user_id};"""
    execute_sql(sql)

    sql = f"""DELETE FROM users
            WHERE id = {user_id};"""
    execute_sql(sql)

def terminate_idle_backend():
    sql = f"""SELECT pg_terminate_backend(pid) FROM pg_stat_Activity where datname = 'hebrew' AND state = 'idle';"""
    execute_sql(sql)

def close_connection():
    db.dispose()

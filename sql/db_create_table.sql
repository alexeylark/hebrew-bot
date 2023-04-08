
CREATE TABLE public.adjectives (
    id integer,
    lang character varying,
    model character varying,
    root character varying,
    translation character varying
);


CREATE TABLE public.adjectives_f (
    id integer,
    lang character varying,
    code character varying,
    spelling character varying,
    transcription character varying,
    plurality character varying,
    sex character varying,
    search_string character varying
);


CREATE TABLE public.nouns (
    id integer,
    lang character varying,
    model character varying,
    root character varying,
    translation character varying,
    sex character varying
);


CREATE TABLE public.nouns_f (
    id integer,
    lang character varying,
    code character varying,
    spelling character varying,
    transcription character varying,
    plurality character varying,
    state character varying,
    search_string character varying
);


CREATE TABLE public.verbs (
    id integer,
    lang character varying,
    binyan character varying,
    root character varying,
    translation character varying
);


CREATE TABLE public.verbs_f (
    id integer,
    lang character varying,
    code character varying,
    spelling character varying,
    transcription character varying,
    plurality character varying,
    timesig character varying,
    person character varying,
    state character varying,
    sex character varying,
    search_string character varying
);



CREATE TABLE public.words_by_level (
    word_type character varying NOT NULL,
    word_id integer NOT NULL,
    difficulty_level character varying NOT NULL,
    word_weight double precision
);


CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying,
    first_name character varying,
    last_name character varying,
    lang character varying,
    joined_dt timestamp without time zone,
    user_lang character varying
);


CREATE TABLE public.known_words (
    user_id bigint NOT NULL,
    word_type character varying,
    word_id integer NOT NULL,
    word_weight double precision
);


CREATE TABLE public.questions (
    message_id character varying NOT NULL,
    question_dt timestamp without time zone,
    user_id bigint NOT NULL,
    word_type character varying,
    variant_ids character varying,
    answer_id integer
);


CREATE TABLE public.raw_updates (
    update_dt timestamp without time zone NOT NULL,
    update_json jsonb NOT NULL
);


ALTER TABLE ONLY public.known_words
    ADD CONSTRAINT known_words_pkey PRIMARY KEY (user_id, word_id);


ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (message_id, user_id);


ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.words_by_level
    ADD CONSTRAINT words_by_level_pkey PRIMARY KEY (word_id, difficulty_level);


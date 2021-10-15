import sqlite3
import zipfile
import json
import pandas as pd
import requests

class DBUtil:
    db_path = 'source/dictionary.db'

    all_sentences_json_url = 'https://sentencesearch.neocities.org/data/all_v11.json'

    jlpt_path = 'source/jlpt_words.xlsx'
    reibun_path = 'source/reibun.zip'
    frequency_lists = [
        'source/frequency/Anime and Drama/Anime&Drama V2.zip',
        'source/frequency/Wikipedia/Wikipedia v2.zip',
        'source/frequency/Novels/Novels.zip',
        'source/frequency/Netflix/Netflix V2.zip'
    ]
    
    _con = None

    @staticmethod
    def get_con():
        if not DBUtil._con:
            DBUtil._con = sqlite3.connect(DBUtil.db_path)
        return DBUtil._con

    @staticmethod
    def close_con():
        if DBUtil._con:
            DBUtil._con.close()
            DBUtil._con = None

    @staticmethod
    def load_jlpt_words():
        print('Loading JLPT words')
        con = DBUtil.get_con()
        cur = con.cursor()

        sheets = [('JLPT N5', 5), ('JLPT N4', 4), ('JLPT N3', 3), ('JLPT N2', 2), ('JLPT N1', 1)]
        for sheet in sheets:
            df = pd.read_excel(DBUtil.jlpt_path, sheet_name=sheet[0])
            df['jlpt_level'] = sheet[1]
            df = df.drop(['JLPT'], axis=1, errors='ignore')
            df = df[['Word', 'Reading', 'Meaning', 'jlpt_level']]
            
            cur.executemany('INSERT INTO dict_jlpt_words(word, reading, meaning, jlpt_level) VALUES (?, ?, ?, ?)', df.values.tolist())

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_reibun():
        print('Loading example sentences')
        con = DBUtil.get_con()
        cur = con.cursor()

        sentences = requests.get(DBUtil.all_sentences_json_url).json()
        rows = map(lambda x: (x['jap'], x['eng'], x['audio_jap'], x['source']), sentences)
        cur.executemany('INSERT INTO dict_reibun(jp, en, audio_jp, source) VALUES (?, ?, ?, ?)', rows)

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def load_frequency_lists():
        print('Loading frequency lists')
        con = DBUtil.get_con()
        cur = con.cursor()

        for freq in DBUtil.frequency_lists:
            with zipfile.ZipFile(freq, 'r') as f:
                index_json = json.loads(f.read('index.json').decode('utf-8'))
                title = index_json['title']
                for name in f.namelist():
                    if name != 'index.json':
                        data_json = json.loads(f.read(name).decode('utf-8'))
                        data_mapped = map(lambda x: (x[0], x[2], title), data_json)
                        cur.executemany('INSERT INTO dict_frequency(word, freq, dict) VALUES (?, ?, ?)', data_mapped)

        con.commit()
        cur.close()
        DBUtil.close_con()

    @staticmethod
    def setup_db():
        print('Setting up DB')
        con = DBUtil.get_con()
        cur = con.cursor()

        # Create JLPT words table
        print('Setting up JLPT words table')
        cur.execute(
            '''
            CREATE TABLE dict_jlpt_words(
                id INTEGER PRIMARY KEY,
                word TEXT,
                reading TEXT,
                meaning TEXT,
                jlpt_level INTEGER
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_jlpt_word ON dict_jlpt_words (word)')
        cur.execute('CREATE INDEX dict_idx_jlpt_reading ON dict_jlpt_words (reading)')

        # Create example sentences table
        print('Setting up example sentences table')
        cur.execute(
            '''
            CREATE TABLE dict_reibun(
                id INTEGER PRIMARY KEY,
                jp TEXT,
                en TEXT,
                audio_jp TEXT,
                source TEXT
            )
            '''
        )

        # Create frequency table
        print('Setting up frequency table')
        cur.execute(
            '''
            CREATE TABLE dict_frequency(
                id INTEGER PRIMARY KEY,
                word TEXT,
                freq INTEGER,
                dict TEXT
            )
            '''
        )
        cur.execute('CREATE INDEX dict_idx_frequency_word ON dict_frequency (word)')
        con.commit()
        cur.close()
        DBUtil.close_con()

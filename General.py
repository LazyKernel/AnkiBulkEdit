import sqlite3
import json
from DBUtil import DBUtil

class General:

    def get_frequencies_for_word(self, word: str):
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT freq, dict FROM dict_frequency WHERE word = ?', [word]).fetchall()
        rows_dict = map(lambda x: {'freq': x[0], 'dict': x[1]}, rows)
        cur.close()
        return list(rows_dict)
    
    def get_pitches_for_word(self, word: str):
        con = DBUtil.get_con()
        cur = con.cursor()
        rows = cur.execute('SELECT pitches FROM dict_pitch_accent WHERE word = ?', [word]).fetchall()
        rows_dict = map(lambda x: json.loads(x[0]), rows)
        cur.close()
        return list(rows_dict)

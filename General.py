import sqlite3
from DBUtil import DBUtil

class General:
    
    def get_frequencies_for_word(self, word: str):
        cur = DBUtil.get_con()
        rows = cur.execute('SELECT freq, dict FROM dict_frequency WHERE word = ?', [word])
        rows_dict = map(lambda x: {'freq': x[0], 'dict': x[1]}, rows)
        cur.close()
        return rows_dict
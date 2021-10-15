import pandas as pd
import requests
import sqlite3
from DBUtil import DBUtil
from sudachipy import tokenizer
from sudachipy import dictionary

class Reibun:

    def __init__(self):
        self.tokenizer = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C

    def get_example_sentences(self, word: str, jlpt_level: int = None):
        cur = DBUtil.get_con()

        rows = cur.execute("SELECT jp, en FROM dict_reibun WHERE instr(jp, ?) > 0", [word])

        if jlpt_level:
            rows_with_freqs = []
            for row in rows:
                score = 0
                for word in self.tokenizer(row, self.mode):
                    cur.execute('SELECT jlpt_level')
        
        cur.close()
        return rows[:2]

import pandas as pd
import requests
import sqlite3
from DBUtil import DBUtil
from General import General
from sudachipy import tokenizer
from sudachipy import dictionary

class Reibun:

    def __init__(self):
        self.tokenizer = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C
        self.general = General()

    def get_example_sentences(self, word: str, jlpt_level: int = None):
        cur = DBUtil.get_con()

        rows = cur.execute('SELECT jp, en FROM dict_reibun WHERE instr(jp, ?) > 0', [word])
        rows = map(lambda x: {'jp': x[0], 'en': x[1]}, rows)

        if jlpt_level:
            rows_with_scores = []
            for row in rows:
                # smaller is better
                score = 0
                words = self.tokenizer(row, self.mode)
                for word in words:
                    freqs = self.general.get_frequencies_for_word(word.dictionary_form())
                    avg = sum(map(lambda x: x['freq']), freqs) / len(freqs)
                    score += avg
                # dont overvalue short sentences
                score /= len(words)
                rows_with_scores.append({'score': score, **row})

            rows_with_scores = sorted(rows_with_scores, lambda x: x['score'])
            rows = rows_with_scores

        cur.close()
        return rows[:3]

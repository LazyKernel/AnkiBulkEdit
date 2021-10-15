import pandas as pd
import requests

class Reibun:
    base_audio_url = 'https://receptomanijalogi.web.app/audio/'
    all_sentences_json_url = 'https://sentencesearch.neocities.org/data/all_v11.json'
    jlpt_path = 'source/jlpt_words.xlsx'
    reibun_path = 'source/reibun.zip'
    db_path = 'source/dictionary.db'

    def get_example_sentences(self):
        sentences_json = requests.get(Reibun.all_sentences_json_url)
        sentences_df = pd.DataFrame(data=sentences_json)
        return sentences_df

    def get_audio_for_uri(self, uri):
        url = Reibun.base_audio_url + uri
        result = requests.get(url)
        # TODO: check this later
        print(result)

    @staticmethod
    def load_jlpt_words():
        pass

    @staticmethod
    def load_reibun():
        pass

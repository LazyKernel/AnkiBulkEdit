# coding=utf8

import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn

from Anki import Anki
from Forvo import Forvo
from DBUtil import DBUtil
from General import General
from Reibun import Reibun

def update_deck1():
    anki = Anki()
    forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan'])
    general = General()
    reibun = Reibun()
    anki.open_package('Active Decks__N2 Vocab_new.apkg')
    notes = anki.get_notes()

    words_not_in_forvo = []
    dropped_words = []
    for note in notes:
        word = note.fields[1]

        freqs = general.get_frequencies_for_word(word)
        freqs_vals = map(lambda x: x['freq'], freqs)

        # If it exceeds 15k on any domain remove it. But if it has a frequency of 7k in a single domain keep it
        if any([val > 15000 for val in freqs_vals]) and not any([val < 7000 for val in freqs_vals]):
            anki.delete_note(note.guid)
            dropped_words.append(word)
            continue

        examples = reibun.get_example_sentences(word)
        if len(examples) > 0:
            examples_list = []
            for example in examples:
                examples_list.append(example['jp'])
                examples_list.append(example['en'])
            anki.set_field('\n'.join(examples_list), note.guid, 6)
        else:
            print('No examples for word', word)

        mp3_file = forvo.get_audio_for_word(word)
        if mp3_file:
            anki.add_audio_to_field(mp3_file, word + '.mp3', note.guid, 5)
        else:
            words_not_in_forvo.append(word)

    anki.close_package()
    print('words_not_in_forvo', words_not_in_forvo)
    print('dropped_words', dropped_words)

def update_deck2():
    anki = Anki()
    forvo = Forvo(['poyotan', 'strawberrybrown', 'straycat88', 'le_temps_perdu', 'kyokotokyojapan', 'Akiko3001'])
    general = General()
    reibun = Reibun()
    anki.open_package('source/Vocab_Deck_ao_bunko.apkg')
    notes = anki.get_notes()

    words_not_in_forvo = []
    for note in notes:
        word = note.fields[1]

        if re.match(r'[ァ-ヶｦ-ﾟ]+', word):
            #anki.delete_note(note.guid)
            continue

        # not getting properly if not in dict form
        mp3_file = forvo.get_audio_for_word(word)
        if mp3_file:
            anki.add_audio_to_field(mp3_file, word + '.mp3', note.guid, 5)
        else:
            words_not_in_forvo.append(word)
            #anki.delete_note(note.guid)
            continue

        examples = reibun.get_example_sentences(word)
        if len(examples) > 0:
            examples_list = []
            for example in examples:
                examples_list.append(example['jp'])
                examples_list.append(example['en'])
            anki.set_field('\n'.join(examples_list), note.guid, 6)
        else:
            print('No examples for word', word)

        pitches = general.get_pitches_for_word(word)
        pitches_str = '\n'.join([f'{pitch["reading"]}: {", ".join([str(p["position"]) for p in pitch["pitches"]])}' for pitch in pitches])
        anki.set_field(pitches_str, note.guid, 7)

    anki.close_package()
    print('words_not_in_forvo', words_not_in_forvo)

def setup_db():
    DBUtil.setup_db()
    DBUtil.load_jlpt_words()
    DBUtil.load_frequency_lists()
    DBUtil.load_reibun()

def get_stats():
    general = General()
    inp = pd.read_csv('source/novels_5k.csv', encoding='utf-8')
    df = pd.DataFrame(columns=['dict', 'freq'])

    for note in inp['Vocab Root']:
        word = note
        freqs = general.get_frequencies_for_word(word)
        df = df.append(freqs)

    print(df)
    seaborn.set()
    print(df.groupby('dict').max())
    df['freq'].hist(by=df['dict'], bins=[0, 7000, 10000, 15000, 25000, 40000])
    #plt.hist(df[df.dict == 'Anime & J-drama']['freq'], bins=10)
    plt.show()

def create_deck_csv():
    def get_1_from_lemma(val):
        split = re.split(r',|、|，', val)
        return split[0]

    def join_with_nan(row):
        return '\n'.join(row.dropna().tolist())

    core5k_df = pd.read_csv('source/new_vocab_for_ao_buta_yarou.csv', sep=',', encoding='utf-8')
    bank_df = pd.read_csv('source/sentence_bank.csv', sep='	', encoding='utf-8')

    # TODO: get dictionary forms for all

    # convert lemma column to one suitable for merging
    #core5k_df['lemma_merge'] = core5k_df['Lemma'].apply(get_1_from_lemma)
    core5k_df = core5k_df.merge(bank_df, how='left', left_on='word', right_on='word')

    # create freqs df
    #freq_df = pd.read_sql('SELECT word, freq, dict FROM dict_frequency', DBUtil.get_con())
    #freq_df = freq_df.pivot_table(index='word', columns='dict', values='freq')

    #core5k_df = core5k_df.merge(freq_df, how='left', left_on='lemma_merge', right_on='word')
    #core5k_df = core5k_df[(core5k_df['Anime & J-drama'] > 3000) & (core5k_df['Netflix'] > 3000) & (core5k_df['Novels'] > 3000) & (core5k_df['Wikipedia'] > 3000)]

    #core5k_df['content'] = core5k_df['content'].combine_first(core5k_df['English Gloss'])
    #core5k_df['examples'] = core5k_df[['Illustrative example','Illustrative Example Translation','Illustrative Example 2','Illustrative Example 2 Translation']].agg(join_with_nan, axis=1)
    core5k_df = core5k_df[['word', 'reading', 'content', 'examples', 'tag']]
    core5k_df.to_csv('source/new_ao_buta_yarou.csv')

if __name__ == '__main__':
    update_deck2()

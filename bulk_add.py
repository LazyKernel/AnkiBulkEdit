from Anki import Anki
from Forvo import Forvo
from DBUtil import DBUtil
from General import General

def update_deck1():
    anki = Anki()
    forvo = Forvo()
    general = General()
    anki.open_package('Active Decks__N2 Vocab_new.apkg')
    notes = anki.get_notes()

    words_not_in_forvo = []
    for note in notes:
        word = note.fields[1]

        freqs = general.get_frequencies_for_word(word)
        freqs_vals = map(lambda x: x['freq'], freqs)

        # If it exceeds 15k on any domain remove it. But if it has a frequency of 7k in a single domain keep it
        if any([val > 15000 for val in freqs_vals]) and not any([val < 7000 for val in freqs_vals]):
            anki.delete_note(note.guid)
            continue

        mp3_file = forvo.get_audio_for_word(word)
        if mp3_file:
            anki.add_audio_to_field(mp3_file, word + '.mp3', note.guid, 5)
        else:
            words_not_in_forvo.append(word)

    anki.close_package()
    print(words_not_in_forvo)

def setup_db():
    DBUtil.setup_db()
    DBUtil.load_jlpt_words()
    DBUtil.load_frequency_lists()
    DBUtil.load_reibun()


if __name__ == '__main__':
    setup_db()

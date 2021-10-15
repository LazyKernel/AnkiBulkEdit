from Anki import Anki
from Forvo import Forvo

anki = Anki()
forvo = Forvo()
anki.open_package('Active Decks__N2 Vocab_new.apkg')
notes = anki.get_notes()

words_not_in_forvo = []

for note in notes:
    word = note.fields[1]
    mp3_file = forvo.get_audio_for_word(word)
    if mp3_file:
        anki.add_audio_to_field(mp3_file, word + '.mp3', note.guid, 5)
    else:
        words_not_in_forvo.append(word)

anki.close_package()
print(words_not_in_forvo)

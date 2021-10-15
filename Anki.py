import sqlite3
import zipfile
import random
import json
import functools
import shutil

class AnkiNote:
    def __init__(self, row: tuple):
        self.guid = row[1]
        self.fields = row[6].split('\x1f')
        

class Anki:
    """
    TODO: Stuff will break if media doesn't exist

    sqlite db struct: https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
    """

    collection_path = 'collection.anki2'
    media_path = 'media'

    def open_package(self, package_path: str):
        self.original_file = package_path.split('/')[-1].replace('.apkg', '')
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            self.temp_path = self.get_random_dirname()
            zip_ref.extractall(self.temp_path)

        self.con = sqlite3.connect(f'{self.temp_path}/{Anki.collection_path}')

        with open(f'{self.temp_path}/{Anki.media_path}', 'r') as f:
            self.media_json = json.loads(f.read())
            self.media_counter = functools.reduce(lambda acc, val: max(acc, int(val)), self.media_json.keys(), 0)

    def get_random_dirname(self):
        return str(random.getrandbits(32))

    # TODO: Field indexes to field names
    def add_audio_to_field(self, data: bytes, filename: str, note_guid: str, field_idx: int):
        self.media_counter += 1
        with open(f'{self.temp_path}/{self.media_counter}', 'wb') as f:
            f.write(data)
        self.media_json[str(self.media_counter)] = filename

        cur = self.con.cursor()
        row = cur.execute('SELECT * FROM notes WHERE guid=:guid', {'guid': note_guid}).fetchone()
        note = AnkiNote(row)
        note.fields[field_idx] += f'[sound:{filename}]'
        cur.execute('UPDATE notes SET flds=:flds WHERE guid=:guid', {'flds': '\x1f'.join(note.fields), 'guid': note_guid})
        self.con.commit()
        cur.close()

    def set_field(self, content: str, note_guid: str, field_idx: int):
        cur = self.con.cursor()
        row = cur.execute('SELECT * FROM notes WHERE guid=:guid', {'guid': note_guid}).fetchone()
        note = AnkiNote(row)
        note.fields[field_idx] = content
        cur.execute('UPDATE notes SET flds=:flds WHERE guid=:guid', {'flds': '\x1f'.join(note.fields), 'guid': note_guid})
        self.con.commit()
        cur.close()

    def get_notes(self):
        cur = self.con.cursor()
        # TODO: order by actual card order?
        rows = [AnkiNote(row) for row in cur.execute('SELECT * FROM notes ORDER BY sfld')]
        cur.close()
        return rows

    def close_package(self):
        self.con.close()
        with open(f'{self.temp_path}/{Anki.media_path}', 'w') as f:
            f.write(json.dumps(self.media_json))
        
        shutil.make_archive(f'{self.original_file}_new.apkg', 'zip', self.temp_path)
        shutil.rmtree(self.temp_path)

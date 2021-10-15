import re
import cloudscraper
import base64
import browser_cookie3
from bs4 import BeautifulSoup

class Forvo:
    base_url = 'https://forvo.com/search'
    lang = 'ja/'

    audio_base_url1 = 'https://audio00.forvo.com/audios/mp3'
    audio_base_url2 = 'https://audio00.forvo.com/mp3'
    audio_regex = re.compile(r"Play\(\d+?,'(.*?)','.*?',(?:false|true),'(.*?)','.+?'\)")

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def download_audio(self, mp3_path: str, word: str):
        data = self.scraper.get(mp3_path)
        if data.status_code != 200:
            print('something broke with', word, 'path', mp3_path)
            return None
        return data.content

    def get_audio_for_word(self, word: str):
        page = self.scraper.get(f'{Forvo.base_url}/{word}/{Forvo.lang}')
        soup = BeautifulSoup(page.text, 'html.parser')
        play_buttons = soup.find_all('span', {'class': 'play'})
        
        audio = None
        if len(play_buttons) > 0:
            btn = play_buttons[0]
            match = Forvo.audio_regex.match(btn['onclick'])
            if match:
                base = Forvo.audio_base_url1
                filename = match.group(2)
                prio2 = match.group(1)

                if not filename or not filename.strip():
                    base = Forvo.audio_base_url2
                    filename = prio2

                decoded_url = base64.b64decode(filename).decode('ascii')
                audio = self.download_audio(f'{base}/{decoded_url}', word)

        if not audio:
            print('No audio for word', word)
        
        return audio

# https://audio00.forvo.com/audios/mp3/s/n/sn_9072967_76_38391_1.mp3

# Play(772680,'OTA3Mjk2Ny83Ni85MDcyOTY3Xzc2XzM4MzkxXzEubXAz','OTA3Mjk2Ny83Ni85MDcyOTY3Xzc2XzM4MzkxXzEub2dn',false,'cy9uL3NuXzkwNzI5NjdfNzZfMzgzOTFfMS5tcDM=','cy9uL3NuXzkwNzI5NjdfNzZfMzgzOTFfMS5vZ2c=','h');return false;
import re
import cloudscraper
import base64
import browser_cookie3
import bs4
from bs4 import BeautifulSoup

class Forvo:
    base_url = 'https://forvo.com/word'
    lang = '#ja'

    audio_base_url1 = 'https://audio00.forvo.com/audios/mp3'
    audio_base_url2 = 'https://audio00.forvo.com/mp3'
    audio_regex = re.compile(r"Play\(\d+?,'(.*?)','.*?',(?:false|true),'(.*?)','.+?'\)")

    def __init__(self, user_priority_list=[]):
        self.scraper = cloudscraper.create_scraper()
        self.user_prio_list = user_priority_list

    def download_audio(self, mp3_path: str, word: str):
        data = self.scraper.get(mp3_path)
        if data.status_code != 200:
            print('something broke with', word, 'path', mp3_path)
            return None
        return data.content

    def get_audio_for_word(self, word: str):
        def find_user(element: bs4.Tag):
            if element:
                return element.text
            return ''

        def sort_users(item):
            size = len(self.user_prio_list)
            if item['user'] in self.user_prio_list:
                value = size - self.user_prio_list.index(item['user'])
                return value
            return -1

        page = self.scraper.get(f'{Forvo.base_url}/{word}/{Forvo.lang}')
        soup = BeautifulSoup(page.text, 'html.parser')
        play_buttons = soup.find_all('span', {'class': 'play'})
        list_of_audio = [{'user': find_user(button.find_next_sibling('span', {'class': 'ofLink'})), 'elem': button} for button in play_buttons]

        list_of_audio = sorted(list_of_audio, key=sort_users, reverse=True)

        audio = None
        if len(list_of_audio) > 0 and list_of_audio[0]['user'] in self.user_prio_list:
            btn = list_of_audio[0]['elem']
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
import requests
from downloader_types import MangaDownloader
import re

ZENKO_API_URL = "https://zenko-api.onrender.com"
ZENKO_PROXY_URL = "https://zenko.online/api/proxy?url=https://zenko.b-cdn.net"

# chapters = requests.get(f"{ZENKO_API_URL}/titles/{title}/chapters").json()

class ZenkoDownloader(MangaDownloader):
    pattern = r"(https://)?zenko\.online/titles/(?P<title>\d+)/?(?P<chapter>(\d+)?).*"
    match = False
    def is_chapter_match(self, url: str):
        self.match = re.search(self.pattern, url)
        if not self.match:
            return False
        return True

    def get_chapter_image_urls(self, url: str):
        chapter = requests.get(f"https://zenko-api.onrender.com/chapters/{self.match.group('chapter')}").json()
        pages_data = chapter["pages"]
        images = []
        for page in pages_data:
            imgId = page["imgUrl"]
            images.append(f"https://zenko.online/api/proxy?url=https://zenko.b-cdn.net/{imgId}?optimizer=image&width=auto&quality=70&height=auto")
        return images

    def get_chapter_name(self, url: str):
        chapter = requests.get(f"https://zenko-api.onrender.com/chapters/{self.match.group('chapter')}").json()
        return chapter['name'].replace('@#%&;№%#&**#!@', ' Том Розділ ')

import requests
from bs4 import BeautifulSoup
import re
from downloader_types import MangaDownloader

BASE_CHAPTER_URI = (
        "https://manga.in.ua/engine/ajax/controller.php?mod=load_chapters_image"
    )

def get_chapter_image_urls(chapter_url: str):
    soup = BeautifulSoup(requests.get(chapter_url).text, "html.parser")
    page_imgs = soup.find_all("img")
    page_urls = []
    for page_img in page_imgs:
        page_urls.append(page_img["data-src"])
    return page_urls

def get_manga_in_ua_hash():
    home_page = requests.get("https://manga.in.ua").text
    login_hash = r".*site_login_hash = \'(?P<login_hash>.+)\'.*"
    match = re.search(login_hash, home_page)
    if not match:
        return False
    return match.group("login_hash")

class MangaInUADownloader(MangaDownloader):
    pattern = r"(https://)?manga\.in\.ua/chapters/(?P<chapter>\d+)-(?P<manga_name>.+).html"
    match = False
    def is_chapter_match(self, url: str):
        self.match = re.search(self.pattern, url)
        if not self.match:
            return False
        return True
    
    def get_chapter_image_urls(self, chapter_url: str):
        chapter_id = self.match.group("chapter")
        user_hash = get_manga_in_ua_hash()
        chapter_url = f"{BASE_CHAPTER_URI}&news_id={chapter_id}&action=show&user_hash={user_hash}"
        return get_chapter_image_urls(chapter_url)
    
    def get_chapter_name(self):
        return self.match.group('manga_name')
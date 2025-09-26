import requests
from bs4 import BeautifulSoup
import re
from downloader_types import MangaDownloader

def get_chapter_image_urls(page_data: str):
    soup = BeautifulSoup(page_data, "html.parser")
    page_imgs = soup.find_all("img", class_="wp-manga-chapter-img")
    page_urls = []
    for page_img in page_imgs:
        page_urls.append(page_img["src"])
    
    return page_urls

def get_comic_id(page: str):
    comic_id = r"\"id\": \"(?P<comic_id>.+)*\","
    match = re.search(comic_id, page)
    if not match:
        return False
    return match.group('comic_id')

class ZazaManga(MangaDownloader):
    pattern = r"(https://)?www.zazamanga.com/manga/(?P<manga_name>.+)/chapter-(?P<chapter>.*)"
    match = False
    comic_id = ''
    def is_chapter_match(self, url: str):
        self.match = re.search(self.pattern, url)
        if not self.match:
            return False
        return True
    
    def get_headers(self):
        return {'Referer': 'https://www.zazamanga.com/'}
    
    def get_chapter_image_urls(self, chapter_url: str):
        page_data = requests.get(chapter_url).text
        self.comic_id=get_comic_id(page_data)
        return get_chapter_image_urls(page_data)
    
    def get_chapters_urls(self):
        chapters_data = requests.get(f'https://www.zazamanga.com/Comic/Services/ComicService.asmx/ProcessChapterList?comicId={self.comic_id}').json()
        result_chapters = []
        if(chapters_data['success']):
            for chapter in chapters_data['chapters']:
                result_chapters.append({'chapter_id': chapter['chapterId'],
                                    'chapter_url': 'https://www.zazamanga.com/manga'+ chapter['url']})
        result_chapters.reverse()
        return result_chapters

    def get_chapter_name(self, url: str):
        return self.match.group('manga_name') + '-' + self.match.group('chapter')
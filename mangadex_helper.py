from re import search
import requests
import re
from downloader_types import MangaDownloader

API_URL = "https://api.mangadex.org"

def format_chapter_uri(chapter_id: str):
    return f"{API_URL}/at-home/server/{chapter_id}?forcePort443=false"

def get_volumes_data(manga_id: str, scanlation_group: str, translated_language: str):
    aggregate_url = f"{API_URL}/manga/{manga_id}/aggregate"
    aggregate_url += f"?groups[]={scanlation_group}"
    aggregate_url += f"&translatedLanguage[]={translated_language}"
    volumes_data = requests.get(aggregate_url).json()["volumes"]
    return volumes_data

def get_chapters_uris(manga_id: str, scanlation_group: str, translated_language: str):
    volumes_data = get_volumes_data(manga_id, scanlation_group, translated_language)
    result_chapters = []
    for volume in volumes_data.values():
        for chapter in volume["chapters"].values():
            result_chapters.append(format_chapter_uri(chapter['id']))
    result_chapters.reverse()
    return result_chapters


def get_chapter_data(chapter_id: str):
    chapter_url = f"{API_URL}/chapter/{chapter_id}"
    chapter_data = requests.get(chapter_url).json()["data"]
    return chapter_data


def get_scanlation_group(chapter_id: str):
    chapter_data = get_chapter_data(chapter_id)
    scanlation_group = chapter_data["relationships"][0]["id"]
    manga_id = chapter_data["relationships"][1]["id"]
    translated_language = chapter_data["attributes"]["translatedLanguage"]
    return [scanlation_group, translated_language, manga_id]

def extract_chapter_id(url: str):
    match = re.match(r"(https://)?mangadex\.org/chapter/(?P<chapter_id>.+)*", url)
    return match.group('chapter_id')

def get_pages_by_url(pages_url: str):
    chapter_id = extract_chapter_id(pages_url)
    pages_url = format_chapter_uri(chapter_id)
    pages_data = requests.get(pages_url).json()
    pages_urls = []
    for page_url in pages_data["chapter"]["data"]:
        pages_urls.append(pages_data["baseUrl"] + "/data/" + pages_data["chapter"]["hash"] + "/" + page_url)
    return pages_urls

class MangadexDownloader(MangaDownloader):
    chapter_id = ''
    def is_chapter_match(self, url: str):
        mangadex_pattern = r"(https://)?mangadex\.org/chapter/(?P<chapter_id>.+)*"
        match = re.search(mangadex_pattern, url)
        if not match:
            return False
        self.chapter_id = match.group('chapter_id')
        return True
    
    def get_chapters_urls(self):
        [scanlation_group, translated_language, manga_id] = get_scanlation_group(self.chapter_id)
        return get_chapters_uris(manga_id, scanlation_group, translated_language)
    
    def get_chapter_image_urls(self, url: str):
        return get_pages_by_url(url)
    
    def get_chapter_name(self, pages_url: str):
        chapter_attributes = get_chapter_data(self.chapter_id)['attributes']
        volume = chapter_attributes['volume']
        chapter = chapter_attributes['chapter']
        title = chapter_attributes['title']
        return f'{volume} Том {chapter} Розділ - {title}'

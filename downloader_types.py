from typing import Protocol

class MangaDownloader(Protocol):
    def is_chapter_match(url: str):
        return False
    def get_chapters_urls(self):
        return []
    def get_chapter_image_urls(url: str):
        return []
    def get_chapter_name(chapter_url: str):
        return ""
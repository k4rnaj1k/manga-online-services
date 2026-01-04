import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from downloader_types import MangaDownloader

BASE_SITE_URL = "https://manga.in.ua"
BASE_IMAGES_AJAX = "https://manga.in.ua/engine/ajax/controller.php?mod=load_chapters_image"
BASE_CHAPTERS_AJAX = "https://manga.in.ua/engine/ajax/controller.php?mod=load_chapters"


def fetch_html(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def fetch_soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch_html(url), "html.parser")


def get_return_to_series_href_from_soup(soup: BeautifulSoup):
    a = soup.select_one("div.returntoseries a[href]")
    return a["href"] if a else None


def get_manga_in_ua_hash(session: requests.Session | None = None) -> str:
    s = session or requests.Session()
    home = s.get(BASE_SITE_URL)
    home.raise_for_status()
    m = re.search(r"site_login_hash\s*=\s*'(?P<login_hash>[^']+)'", home.text)
    if not m:
        raise RuntimeError("Could not find site_login_hash on manga.in.ua home page")
    return m.group("login_hash")


def extract_chapter_id(url: str) -> str:
    """
    Compatible with MangadexDownloader style: extracts chapter id from URL.
    For manga.in.ua it's the numeric id after /chapters/.
      https://manga.in.ua/chapters/58657-something.html -> 58657
    """
    m = re.search(r"(https://)?manga\.in\.ua/chapters/(?P<chapter_id>\d+)-", url)
    if not m:
        raise ValueError(f"Could not extract chapter_id from url: {url}")
    return m.group("chapter_id")


def extract_series_id_from_series_url(series_url: str) -> str:
    """
    Extracts manga 'news_id' from a series URL. Tolerant of different path shapes.
      https://manga.in.ua/mangas/.../58656-name.html -> 58656
      https://manga.in.ua/58656-name.html -> 58656
      /mangas/.../58656-name.html -> 58656
    """
    path = urlparse(series_url).path
    m = re.search(r"/(?P<id>\d+)-", path)
    if not m:
        raise ValueError(f"could not extract news_id from series url path: {path!r}")
    return m.group("id")


def build_ajax_chapter_images_url(chapter_id: str, user_hash: str) -> str:
    # GET endpoint returning HTML with <img data-src="...">
    return f"{BASE_IMAGES_AJAX}&news_id={chapter_id}&action=show&user_hash={user_hash}"


def post_chapters_list(session: requests.Session, news_id: str, user_hash: str, news_category: str = "1", this_link: str = "") -> str:
    """
    POST form-data to load_chapters.
    """
    payload = {
        "action": "show",
        "news_id": str(news_id),
        "news_category": str(news_category),
        "this_link": this_link,
        "user_hash": user_hash,
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        # Referer helps sometimes; set later to the series page when available
    }
    r = session.post(BASE_CHAPTERS_AJAX, data=payload, headers=headers)
    r.raise_for_status()
    return r.text


def parse_chapters_from_html(html: str) -> list[dict]:
    """
    Returns the same shape as Mangadex get_chapters_uris():
      {'chapter_id': ..., 'chapter_url': ..., 'volume': ..., 'chapter': ...}
    """
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []

    for item in soup.select("div.ltcitems"):
        vol = item.get("manga-tom")
        ch = item.get("manga-chappter")  # site typo
        a = item.select_one("a[href]")
        if not a:
            continue

        href = (a.get("href") or "").strip()
        if not href:
            continue

        chapter_url = urljoin(BASE_SITE_URL, href)

        # Extract numeric chapter_id from the chapter_url
        try:
            chapter_id = extract_chapter_id(chapter_url)
        except ValueError:
            # If it ever deviates, skip rather than crash the whole list
            continue

        out.append(
            {
                "chapter_id": chapter_id,
                "chapter_url": chapter_url,
                "volume": vol,
                "chapter": ch,
            }
        )

    # site is commonly newest-first
    out.reverse()
    return out


def get_pages_by_url(pages_url: str, session: requests.Session | None = None) -> list[str]:
    """
    Mangadex-compatible: takes a chapter page url and returns list of image urls.
    For manga.in.ua we call load_chapters_image (GET) and parse <img data-src>.
    """
    s = session or requests.Session()
    chapter_id = extract_chapter_id(pages_url)
    user_hash = get_manga_in_ua_hash(s)

    ajax_url = build_ajax_chapter_images_url(chapter_id, user_hash)
    html = s.get(ajax_url)
    html.raise_for_status()

    soup = BeautifulSoup(html.text, "html.parser")
    return [img["data-src"] for img in soup.select("img[data-src]")]


def get_series_url_from_chapter_url(chapter_url: str, session: requests.Session | None = None) -> str:
    s = session or requests.Session()
    soup = BeautifulSoup(s.get(chapter_url).text, "html.parser")
    href = get_return_to_series_href_from_soup(soup)
    if not href:
        raise RuntimeError("Could not find return-to-series link on chapter page")
    return urljoin(BASE_SITE_URL, href)


def get_chapters_uris(chapter_url: str, session: requests.Session | None = None) -> list[dict]:
    """
    Mangadex-compatible: returns list of chapters dicts.
    We start from a chapter url, find series url, extract news_id, POST chapters list, parse.
    """
    s = session or requests.Session()

    series_url = get_series_url_from_chapter_url(chapter_url, s)
    news_id = extract_series_id_from_series_url(series_url)

    user_hash = get_manga_in_ua_hash(s)

    # Use series page as referer (some sites care)
    # (requests.Session keeps headers per call; we pass it via headers in post if needed)
    html = post_chapters_list(s, news_id=news_id, user_hash=user_hash, news_category="1", this_link="")
    return parse_chapters_from_html(html)


def get_chapter_name(chapter_url: str, session: requests.Session | None = None) -> str:
    """
    MangadexDownloader equivalent: returns a readable chapter name.
    We'll use the visible link text from the chapter page if possible,
    otherwise fallback to slug.
    """
    s = session or requests.Session()
    soup = BeautifulSoup(s.get(chapter_url).text, "html.parser")

    # Often there is a chapter title header; this is best-effort.
    h1 = soup.select_one("h1")
    if h1:
        txt = h1.get_text(" ", strip=True)
        if txt:
            return txt

    # fallback: use URL slug
    m = re.search(r"/chapters/\d+-(?P<slug>.+)\.html", chapter_url)
    return m.group("slug") if m else chapter_url


class MangaInUADownloader(MangaDownloader):
    """
    Same API as MangadexDownloader:
      - is_chapter_match(url) -> bool (stores chapter_id)
      - get_chapters_urls() -> list[{'chapter_id','chapter_url','volume','chapter'}]
      - get_chapter_image_urls(url) -> list[str]
      - get_chapter_name(url) -> str
    """
    chapter_id = ""

    def __init__(self):
        self._matched_url: str | None = None
        self._session = requests.Session()

    def is_chapter_match(self, url: str):
        pattern = r"(https://)?manga\.in\.ua/chapters/(?P<chapter_id>\d+)-.+\.html"
        m = re.search(pattern, url)
        if not m:
            return False
        self.chapter_id = m.group("chapter_id")
        self._matched_url = url
        return True

    def get_chapters_urls(self):
        if not self._matched_url:
            return []
        return get_chapters_uris(self._matched_url, self._session)

    def get_chapter_image_urls(self, url: str):
        return get_pages_by_url(url, self._session)

    def get_chapter_name(self, pages_url: str):
        return get_chapter_name(pages_url, self._session)

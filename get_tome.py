from PIL import Image
import requests
import uuid
import re
from bs4 import BeautifulSoup
import argparse
import os

import mangadex_helper


def write_image_data(imgId: str, imgUrl: str):
    result = requests.get(imgUrl)
    filename = f"temp/{imgId if imgId.endswith('.png') else f'{imgId}.png'}"
    with open(filename, "wb+") as file:
        file.write(result.content)
    return filename


def save_to_pdf(filename, image_files: list[str]):
    images = [Image.open(f).convert("RGB") for f in image_files]

    pdf_path = f"result/{filename}"

    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )
    return filename


def remove_temp_images(images: list[str]):
    for image in images:
        os.remove(image)


# zenko
def write_zenko_data(imgId):
    imgUrl = f"https://zenko.online/api/proxy?url=https://zenko.b-cdn.net/{imgId}?optimizer=image&width=auto&quality=70&height=auto"
    return write_image_data(imgId, imgUrl)


def get_chapters_data(url: str):
    return requests.get(url).json()


def download_zenko_chapter(chapter_id: str):
    chapter = get_chapters_data(f"https://zenko-api.onrender.com/chapters/{chapter_id}")
    pages_data = chapter["pages"]
    images = []
    for page in pages_data:
        images.append(write_zenko_data(page["imgUrl"]))
    result = save_to_pdf(f"{chapter['name']}.pdf", images)
    remove_temp_images(images)
    return result


def download_zenko_title(title: str):
    chapters = get_chapters_data(
        f"https://zenko-api.onrender.com/titles/{title}/chapters"
    )
    result = []
    for chapter in chapters:
        result.append(download_zenko_chapter(chapter["id"]))
    return result


def download_zenko_manga(manga_url: str):
    zenko_pattern = (
        r"(https://)?zenko\.online/titles/(?P<title>\d+)(?P<chapter>(/\d+)?).*"
    )
    match = re.search(zenko_pattern, manga_url)

    if not match:
        return False
    title = match.group("title")
    try:
        chapter = match.group("chapter")[1:]
        return [download_zenko_chapter(chapter)]
    except Exception:
        return download_zenko_title(title)


# manga in ua


def get_manga_in_ua_pages_data(chapter_url: str):
    soup = BeautifulSoup(requests.get(chapter_url).text, "html.parser")
    page_imgs = soup.find_all("img")
    page_urls = []
    for page_img in page_imgs:
        page_urls.append(page_img["data-src"])
    return page_urls


def get_manga_in_ua_pdf(chapter_url: str, manga_name: str):
    page_urls = get_manga_in_ua_pages_data(chapter_url)
    pages = []
    for page_url in page_urls:
        page_id = str(uuid.uuid4())
        pages.append(write_image_data(page_id, page_url))
    file_name = manga_name + ".pdf"

    result = save_to_pdf(file_name, pages)
    remove_temp_images(pages)
    return [result]


def get_manga_in_ua_hash():
    home_page = requests.get("https://manga.in.ua").text
    login_hash = r".*site_login_hash = \'(?P<login_hash>.+)\'.*"
    match = re.search(login_hash, home_page)
    if not match:
        return False
    return match.group("login_hash")


def download_manga_in_ua(manga_url: str):
    BASE_CHAPTER_URI = (
        "https://manga.in.ua/engine/ajax/controller.php?mod=load_chapters_image"
    )

    manga_in_ua_pattern = (
        r"(https://)?manga\.in\.ua/chapters/(?P<chapter>\d+)-(?P<manga_name>.+).html"
    )

    match = re.search(manga_in_ua_pattern, manga_url)

    if not match:
        return False
    chapter_id = match.group("chapter")
    user_hash = get_manga_in_ua_hash()
    if not user_hash:
        return False
    chapter_url = (
        f"{BASE_CHAPTER_URI}&news_id={chapter_id}&action=show&user_hash={user_hash}"
    )
    manga_name = match.group("manga_name")

    return get_manga_in_ua_pdf(chapter_url, manga_name)


def get_chapters_mangadex(manga_url: str):
    mangadex_pattern = r"(https://)?mangadex\.org/chapter/(?P<chapter_id>.+)*"
    match = re.search(mangadex_pattern, manga_url)
    if not match:
        return False
    chapter_id = match.group("chapter_id")
    [scanlation_group, translated_language, manga_id] = (
        mangadex_helper.get_scanlation_group(chapter_id)
    )

    chapters = mangadex_helper.get_chapters_ids(
        manga_id, scanlation_group, translated_language
    )
    return chapters


def download_mangadex(manga_url: str):
    chapters = get_chapters_mangadex(manga_url)
    if not chapters:
        return False
    for index, chapter_data in enumerate(chapters):
        [baseUrl, chapter_pages, chapter_title] = mangadex_helper.get_pages(
            chapter_data["chapter_id"]
        )
        pages = []
        for chapter_page in chapter_pages:
            pages.append(write_image_data(chapter_page, f"{baseUrl}/{chapter_page}"))
        save_to_pdf(f"{index}-{chapter_title}.pdf", pages)
        remove_temp_images(pages)


def download_mangadex_single(manga_url: str):
    [baseUrl, chapter_pages, chapter_title, volume] = mangadex_helper.get_pages_by_url(
        manga_url
    )
    pages = []
    for chapter_page in chapter_pages:
        pages.append(write_image_data(chapter_page, f"{baseUrl}/{chapter_page}"))
    save_to_pdf(f"{volume}-{chapter_title}.pdf", pages)
    remove_temp_images(pages)
    return f"{volume}-{chapter_title}.pdf"


def download_mangadex_chapter(chapter_id: str):
    [baseUrl, chapter_pages, chapter_title] = mangadex_helper.get_pages(chapter_id)
    pages = []
    for chapter_page in chapter_pages:
        pages.append(write_image_data(chapter_page, f"{baseUrl}/{chapter_page}"))
    pdf_name = f"{chapter_title}.pdf"
    save_to_pdf(pdf_name, pages)
    remove_temp_images(pages)
    return pdf_name


def download_manga(manga_url: str):
    zenko_manga = download_zenko_manga(manga_url)
    if zenko_manga:
        return zenko_manga
    miu_manga = download_manga_in_ua(manga_url)
    if miu_manga:
        return miu_manga
    return download_mangadex(manga_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manga_url",
        help="Manga url to be downloaded. Currently works with zenko and manga in ua manga links",
        type=str,
    )

    args = parser.parse_args()
    download_manga(args.manga_url)

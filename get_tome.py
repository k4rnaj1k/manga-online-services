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
    print(filename)


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
    save_to_pdf(f"{chapter['name']}.pdf", images)
    remove_temp_images(images)


def download_zenko_title(title: str):
    chapters = get_chapters_data(
        f"https://zenko-api.onrender.com/titles/{title}/chapters"
    )
    for chapter in chapters:
        download_zenko_chapter(chapter["id"])


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
        download_zenko_chapter(chapter)
    except Exception:
        download_zenko_title(title)


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

    save_to_pdf(file_name, pages)
    remove_temp_images(pages)


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
    user_hash = "3dc43ae45a8750d1cae8bc7f56386a1a8578517c"
    chapter_url = (
        f"{BASE_CHAPTER_URI}&news_id={chapter_id}&action=show&user_hash={user_hash}"
    )
    manga_name = match.group("manga_name")

    get_manga_in_ua_pdf(chapter_url, manga_name)


def download_mangadex(manga_url: str):
    mangadex_pattern = r"(https://)?mangadex\.org/chapter/(?P<chapter_id>.+)*"
    match = re.search(mangadex_pattern, manga_url)
    print(match)
    if not match:
        return False
    chapter_id = match.group("chapter_id")
    [scanlation_group, manga_id] = mangadex_helper.get_scanlation_group(chapter_id)

    chapters = mangadex_helper.get_chapters_ids(manga_id, scanlation_group)
    print(chapters)
    for index, chapter in enumerate(chapters):
        [baseUrl, chapter_pages, chapter_title] = mangadex_helper.get_pages(
            chapter["id"]
        )
        print(baseUrl)
        pages = []
        for chapter_page in chapter_pages:
            pages.append(write_image_data(chapter_page, f"{baseUrl}/{chapter_page}"))
        save_to_pdf(f"{index+1}-{chapter_title}.pdf", pages)
        remove_temp_images(pages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manga_url",
        help="Manga url to be downloaded. Currently works with zenko and manga in ua manga links",
        type=str,
    )

    args = parser.parse_args()
    if not download_zenko_manga(args.manga_url):
        if not download_manga_in_ua(args.manga_url):
            download_mangadex(args.manga_url)

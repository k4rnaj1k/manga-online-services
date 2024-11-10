import requests
import get_tome

ZENKO_API_URL = "https://zenko-api.onrender.com"
ZENKO_PROXY_URL = "https://zenko.online/api/proxy?url=https://zenko.b-cdn.net"


def download_zenko_chapter(chapter_id: str):
    chapter = requests.get(f"{ZENKO_API_URL}/chapters/{chapter_id}").json()
    pages_data = chapter["pages"]
    images = []
    for page in pages_data:
        imgId = page["imgUrl"]
        imgUrl = f"{ZENKO_PROXY_URL}/{imgId}?optimizer=image&width=auto&quality=70&height=auto"
        images.append(get_tome.write_image_data(imgId, imgUrl))
    result = get_tome.save_to_pdf(f"{chapter['name']}.pdf", images)
    get_tome.remove_temp_images(images)
    return result


def download_zenko_title(title: str):
    chapters = requests.get(f"{ZENKO_API_URL}/titles/{title}/chapters").json()

    result = []
    for chapter in chapters:
        result.append(download_zenko_chapter(chapter["id"]))
    return result

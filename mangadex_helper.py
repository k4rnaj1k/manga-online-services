import requests

API_URL = "https://api.mangadex.org"


def get_chapters_ids(manga_id: str, scanlation_group: str):
    aggregate_url = f"{API_URL}/manga/{manga_id}/aggregate"
    aggregate_url += f"?groups[]={scanlation_group}"
    volumes_data = requests.get(aggregate_url).json()["volumes"]
    result_chapters = []
    for volume in volumes_data.values():
        for chapter in volume["chapters"].values():
            result_chapters.append(chapter)
    result_chapters.reverse()
    return result_chapters


# def get_chapters(manga_id: str, scanlation_group: str, results=[], offset=0):
#     feed_url = f"{API_URL}/manga/{manga_id}/feed"
#     feed_url += f"?offset={offset}"
#     print(feed_url)
#     chapters_data = requests.get(feed_url).json()
#     chapters = chapters_data["data"]
#     if len(chapters) == 0:
#         return results
#     for chapter in chapters:
#         if (
#             chapter["type"] == "chapter"
#             and chapter["attributes"]["translatedLanguage"] == "en"
#             and chapter["relationships"][0]["id"] == scanlation_group
#         ):
#             results.append(chapter)
#     return get_chapters(manga_id, scanlation_group, results, offset + 100)


def get_chapter_data(chapter_id: str):
    chapter_url = f"{API_URL}/chapter/{chapter_id}"

    chapter_data = requests.get(chapter_url).json()["data"]
    return chapter_data


def get_scanlation_group(chapter_id: str):
    chapter_data = get_chapter_data(chapter_id)
    scanlation_group = chapter_data["relationships"][0]["id"]
    manga_id = chapter_data["relationships"][1]["id"]
    return [scanlation_group, manga_id]


def get_pages(chapter_id: str):
    pages_url = f"{API_URL}/at-home/server/{chapter_id}?forcePort443=false"

    pages_data = requests.get(pages_url).json()
    base_url = pages_data["baseUrl"] + "/data/" + pages_data["chapter"]["hash"]
    pages_ids = pages_data["chapter"]["data"]
    chapter_data = get_chapter_data(chapter_id)
    chapter_title = chapter_data["attributes"]["title"]
    return [base_url, pages_ids, chapter_title]

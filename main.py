from downloader_types import MangaDownloader
import uuid
from pdf_helper import write_image_data, save_to_pdf, remove_temp_images
import argparse
from zenko_helper import ZenkoDownloader
from manga_in_ua_helper import MangaInUADownloader
from mangadex_helper import MangadexDownloader

def get_manga_pdf(chapter_url: str, helper: MangaDownloader):
    #TODO: better error handling
    pages_urls = helper.get_chapter_image_urls(chapter_url)
    print('Starting download of the given chapter...')
    print('Downloading pages...')
    pages = []
    for index, page_url in enumerate(pages_urls):
        pages.append(write_image_data(page_url))
        print(f'{index}/{len(pages_urls)} downloaded')
    print('All pages downloaded...')
    file_name = helper.get_chapter_name(chapter_url) + ".pdf"
    result = save_to_pdf(file_name, pages)
    print('Saved to pdf... Removing the temp images...')
    remove_temp_images(pages)
    return [result]

helpers = [MangadexDownloader(), MangaInUADownloader(), ZenkoDownloader()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manga_url",
        help="Manga url to be downloaded. Currently works with zenko, manga in ua and mangadex manga links",
        type=str,
    )
    
    args = parser.parse_args()
    for helper in helpers:
        if(helper.is_chapter_match(args.manga_url)):
            get_manga_pdf(args.manga_url, helper)
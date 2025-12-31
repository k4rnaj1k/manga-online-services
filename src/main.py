from downloader_types import MangaDownloader
import uuid
from utils.pdf_helper import write_image_data, save_to_pdf, remove_temp_images
import argparse
from helpers.zenko_helper import ZenkoDownloader
from helpers.manga_in_ua_helper import MangaInUADownloader
from helpers.mangadex_helper import MangadexDownloader
from helpers.zazamanga_helper import ZazaManga

def get_manga_pdf(chapter_url: str, helper: MangaDownloader):
    #TODO: better error handling
    pages_urls = helper.get_chapter_image_urls(chapter_url)
    print('Starting download of the given chapter...', end="\r", flush=True)
    pages = []
    for index,page_url in enumerate(pages_urls):
        print(f'{index + 1}/{len(pages_urls)} downloaded', end="\r", flush=True)
        pages.append(write_image_data(page_url, helper.get_headers()))
    file_name = helper.get_chapter_name(chapter_url) + ".pdf"
    result = save_to_pdf(file_name, pages)
    print(f'\nSaved to pdf... {file_name} Removing the temp images...')
    remove_temp_images(pages)
    return result

helpers = [MangadexDownloader(), MangaInUADownloader(), ZenkoDownloader(), ZazaManga()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manga_url",
        help="Manga url to be downloaded. Currently works with zenko, manga in ua and mangadex manga links",
        type=str,
    )
    
    parser.add_argument(
        "mode",
        help="Mode. Can be bulk. Single by default",
        type=str,
        default="single"
    )
    
    args = parser.parse_args()
    if args.mode == 'single':
        for helper in helpers:
            if(helper.is_chapter_match(args.manga_url)):
                get_manga_pdf(args.manga_url, helper)
                
    else:
        for helper in helpers:
            if(helper.is_chapter_match(args.manga_url)):
                helper.get_chapter_image_urls(args.manga_url)
                chapters = helper.get_chapters_urls()
                for index, chapter in enumerate(chapters):
                    print('downloading chapter ' + str(index + 1) + ' of ' + str(chapters.__len__()))
                    helper.is_chapter_match(chapter['chapter_url'])
                    get_manga_pdf(chapter['chapter_url'], helper)
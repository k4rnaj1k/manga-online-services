from PIL import Image
import requests
import os
import uuid
from pathlib import Path

def create_dir_if_not_exists(dir: str):
    Path(dir).mkdir(exist_ok=True, parents=True)

def write_image_data(imgUrl: str):
    result = requests.get(imgUrl)
    imgId = uuid.uuid4()
    create_dir_if_not_exists('temp')
    filename = f"temp/{imgId}.png"
    with open(filename, "wb+") as file:
        file.write(result.content)
    return filename

def save_to_pdf(filename, image_files: list[str]):
    images = [Image.open(f).convert("RGB") for f in image_files]
    
    create_dir_if_not_exists('result')
    pdf_path = f"result/{filename}"

    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )
    return filename

def remove_temp_images(images: list[str]):
    for image in images:
        os.remove(image)

from PIL import Image
import requests



def write_image_data(imgId):
    result = requests.get(f'https://zenko.online/api/proxy?url=https://zenko.b-cdn.net/{imgId}?optimizer=image&width=auto&quality=70&height=auto')
    with open('temp/' + imgId + '.png', 'wb+') as file:
        print('Writing page data for imgId ' + imgId)
        file.write(result.content)


def save_images(images_data):
    result = []
    for image_data in images_data:
        result.append(image_data['imgUrl'])
        write_image_data(image_data['imgUrl'])
    return result

# save_images()
def save_to_pdf(filename, image_files: []):
    images = [
    Image.open('temp/'+ f + '.png').convert('RGB')
    for f in image_files
    ]

    pdf_path = f"result/{filename}"
    
    images[0].save(
        pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )
# https://zenko-api.onrender.com/chapters/23397
def get_pages_data(url: str):
    pages_data = requests.get(url)
    return pages_data.json()['pages']

print(get_pages_data('https://zenko-api.onrender.com/chapters/23397'))

# print('Starting...')
# images = save_images()
# print('Saving to pdf...')
# save_to_pdf('lookback.pdf', images)
# print('Done')

# images_data.sort(lambda image_data: image_data['id'])
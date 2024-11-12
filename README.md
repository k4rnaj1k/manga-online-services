# **M**anga **O**nline **S**ervice**s**

<p align="center">
  <img alt="Service's mascot, hope repo will not go down because of it lmao" src="moss_image.webp" />
</p>

> Moss, get it? :D

A small script/service that can download manga off of a few popular services. Currently supports:
1. [mangadex.org](https://mangadex.org)
1. [zenko.online](https://zenko.online/)
1. [manga.in.ua](https://manga.in.ua/)

To download a chapter - simply run:
```sh
python main.py <your chapter url here>
```

<details>
  <summary>Might need to install dependencies</summary>
  
  ```sh
  # python -m venv .
  pip install BeautifulSoup4 requests Pillow stomp.py
  ```

</details>

There is also a way of integrating it via ActiveMQ, but it's not finalized yet
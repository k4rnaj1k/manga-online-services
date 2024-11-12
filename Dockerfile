FROM python:3.11
RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip install Pillow BeautifulSoup4 requests stomp.py
CMD python listener.py
FROM python:3.8
RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip install Pillow BeatifulSoup4 requests stomp.py
CMD python listener.py
FROM python:3.11-bullseye
ENV TZ=America/Argentina/Mendoza
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .

RUN mkdir /app/tmp
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY code/ .
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]

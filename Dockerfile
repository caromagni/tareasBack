FROM python:3.11
ENV TZ=America/Argentina/Mendoza

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .

RUN mkdir /app/tmp
RUN apt update
RUN apt install uwsgi-plugin-python3
RUN python3 -m pip install --upgrade pip --progress-bar off
RUN pip install -r requirements.txt --progress-bar off
#ppp

COPY code/ .
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]
      
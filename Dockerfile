FROM python:3.7.9
ENV TZ=America/Argentina/Mendoza

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .

RUN mkdir /app/tmp
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
#ppp

COPY code/ .
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]
    
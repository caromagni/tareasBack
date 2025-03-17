FROM python:3.11
ENV TZ=America/Argentina/Mendoza

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .

RUN mkdir /app/tmp
RUN python3 -m pip install --upgrade pip
<<<<<<< HEAD
RUN pip install -r requirements.txt
=======
RUN pip install --progress-bar off -r requirements.txt
>>>>>>> main
#ppp

COPY code/ .
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]
      
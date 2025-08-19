FROM python:3.11-bullseye
ENV TZ=America/Argentina/Mendoza

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .


RUN mkdir /app/tmp
RUN python3 -m pip install --upgrade pip
RUN pip install --progress-bar off -r requirements.txt
#RUN pip install -r requirements.txt
#ppp

COPY app/ .
#RUN make html
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]
  

FROM python:3.11


ENV TZ=America/Argentina/Mendoza


WORKDIR /app


COPY ./requirements.txt .
COPY ./uwsgi.ini .

RUN mkdir -p /app/tmp

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        uwsgi-plugin-python3 && \
    curl -fsSL https://ftp-master.debian.org/keys/archive-key-12.asc | gpg --no-tty --dearmor -o /usr/share/keyrings/debian-archive-keyring.gpg && \
    curl -fsSL https://ftp-master.debian.org/keys/archive-key-12-security.asc | gpg --no-tty --dearmor -o /usr/share/keyrings/debian-security-keyring.gpg && \
    apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN python3 -m pip install --upgrade pip --progress-bar off && \
    pip install -r requirements.txt --progress-bar off


COPY code/ .


CMD ["uwsgi", "--wsgi-file", "main.py", "--ini", "uwsgi.ini"]

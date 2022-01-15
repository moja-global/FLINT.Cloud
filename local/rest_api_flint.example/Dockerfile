#FROM mojaglobal/flint
FROM ghcr.io/moja-global/flint.example:master

#ENV APP_HOME /app
WORKDIR /server

RUN set -xe \
    && apt-get update \
    && easy_install pip
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

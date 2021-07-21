#FROM mojaglobal/flint
FROM tlazypanda/gcbm

#ENTRYPOINT ["./moja.cli"]

#ENV APP_HOME /app
WORKDIR /app

RUN set -xe \
    && apt-get update \
    && easy_install pip
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
ENV PORT 8080

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

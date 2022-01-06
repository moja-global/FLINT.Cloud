#FROM mojaglobal/flint
FROM tlazypanda/gcbm

#ENTRYPOINT ["./moja.cli"]

#ENV APP_HOME /app
WORKDIR /app

RUN set -xe \
    && apt-get update \
    && easy_install pip
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

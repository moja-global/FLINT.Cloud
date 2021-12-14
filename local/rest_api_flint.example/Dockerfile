#FROM mojaglobal/flint
FROM shubhamkarande13/flint.example:bionic

#ENV APP_HOME /app
WORKDIR /server

RUN set -xe \
    && apt-get update \
    && easy_install pip
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV PORT 8080

COPY . .

CMD ["exec", "gunicorn", "--bind", ":$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

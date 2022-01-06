# Official Python image
FROM python:3.9

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Disable interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update -y && \
apt-get install -y --no-install-recommends python3-gdal libgdal-dev

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
WORKDIR /
COPY requirements.txt ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD ["exec", "gunicorn", "--bind", ":$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "main:app"]
# GCBM Image
FROM gcr.io/flint-cloud/gcbm:latest

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN python3 -m pip install --upgrade pip && \
python3 -m pip install --upgrade setuptools && \
python3 -m pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run startup script
CMD python3 main.py
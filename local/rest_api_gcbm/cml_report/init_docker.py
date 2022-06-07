import os

os.system("docker build --build-arg BUILD_TYPE=RELEASE --build-arg NUM_CPU=4 -t gcbm-api .")
os.system("docker run --rm -p 8080:8080 gcbm-api")


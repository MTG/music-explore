FROM tiangolo/uwsgi-nginx-flask:python3.12
LABEL maintainer="Philip Tovstogan <phil.tovstogan@gmail.com>"

# generate requirements.txt from uv.lock
RUN --mount=from=ghcr.io/astral-sh/uv:0.9.6,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-emit-workspace --no-dev --no-editable -o /app/requirements.txt

RUN pip install -r /app/requirements.txt

# uwsgi log dir
RUN mkdir -p /var/log/uwsgi

COPY app /app/app
ENV STATIC_PATH=/app/app/static
COPY main.py /app
# make sure we don't copy symlink from dev environment
RUN rm -f /app/static/audio

COPY config-docker.py /app/instance/config.py

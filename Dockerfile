FROM tiangolo/uwsgi-nginx-flask:python3.8
MAINTAINER Philip Tovstogan "philip.tovstogan@upf.edu"

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# uwsgi log dir
RUN mkdir -p /var/log/uwsgi

COPY app /app/app
ENV STATIC_PATH /app/app/static
COPY main.py /app
# make sure we don't copy symlink from dev environment
RUN rm -f /app/static/audio

COPY config-docker.py /app/instance/config.py

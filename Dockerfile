FROM tiangolo/uwsgi-nginx-flask:python3.7
MAINTAINER Philip Tovstogan "philip.tovstogan@upf.edu"

COPY ./app /app
# make sure we don't copy symlink from dev environment
RUN rm -f /app/static/audio
COPY ./requirements.txt /app/requirements.txt
COPY config-docker.py /app/instance/config.py
RUN pip install -r /app/requirements.txt

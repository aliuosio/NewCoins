ARG PY_VERSION
FROM python:${PY_VERSION:-3.13.3-slim-bookworm}

LABEL maintainer="Osiozekhai Aliu"

RUN apt update && apt upgrade -y && \
    apt install -y cron postgresql-client nano && \
    apt clean && \
    rm -rf /var/lib/apt/lis ts/*

RUN service cron start

RUN echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab -

RUN echo 'export EDITOR=nano' >> /root/.bashrc
RUN echo 'export EDITOR=nano' >> /root/.profile

COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

CMD ["cron", "-f"]
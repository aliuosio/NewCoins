ARG PY_VERSION
FROM python:${PY_VERSION:-3.13.3-slim-bookworm}

LABEL maintainer="Osiozekhai Aliu"

RUN apt update && apt full-upgrade -y && \
    apt install -y \
        cron \
        curl \
        postgresql-client \
        nano \
        uvicorn && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab - && \
    echo 'export EDITOR=nano' >> /root/.bashrc && \
    echo 'export EDITOR=nano' >> /root/.profile

CMD ["cron", "-f"]

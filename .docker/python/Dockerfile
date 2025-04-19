ARG PY_VERSION
FROM python:${PY_VERSION:-3.13.3-slim-bookworm}

LABEL maintainer="Osiozekhai Aliu"

RUN apt update && apt install -y curl gnupg ca-certificates lsb-release && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt update && apt install -y cron postgresql-client nano nodejs && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab - && \
    echo 'export EDITOR=nano' >> /root/.bashrc && \
    echo 'export EDITOR=nano' >> /root/.profile

CMD ["cron", "-f"]

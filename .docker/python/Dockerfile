ARG PY_VERSION
FROM python:${PY_VERSION:-3.13.3-slim-bookworm}

LABEL maintainer="Osiozekhai Aliu"

RUN apt update && apt full-upgrade -y && \
    apt install -y cron curl postgresql-client nano uvicorn bash-completion git unzip && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab - && \
    echo 'export EDITOR=nano' >> /root/.bashrc && \
    echo 'export EDITOR=nano' >> /root/.profile && \
    echo 'if [ -f /usr/share/bash-completion/bash_completion ]; then . /usr/share/bash-completion/bash_completion; fi' >> /root/.bashrc

# --- Automate mexc-api-sdk Python install ---
RUN git clone https://github.com/mxcdevelop/mexc-api-sdk.git /src/mexc-api-sdk && \
    cd /src/mexc-api-sdk/dist/python && \
    tar -xzf mexc-sdk-*.tar.gz

CMD ["cron", "-f"]

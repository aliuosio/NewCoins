ARG PY_VERSION
FROM python:${PY_VERSION:-3.13.3-slim-bookworm}

LABEL maintainer="Osiozekhai Aliu"

RUN apt update && apt full-upgrade -y && \
apt install -y cron curl postgresql-client nano uvicorn bash-completion git unzip && \
apt clean && \
rm -rf /var/lib/apt/lists/*

RUN echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab - && \
echo 'alias ll="ls -la"' >> /root/.bashrc && \
echo 'export EDITOR=nano' >> /root/.bashrc && \
echo 'export EDITOR=nano' >> /root/.profile && \
echo 'if [ -f /usr/share/bash-completion/bash_completion ]; then . /usr/share/bash-completion/bash_completion; fi' >> /root/.bashrc && \
echo 'source /root/.bashrc && source /root/.profile'

# Install Node.js (required for mexc_sdk jsii dependency)
RUN apt update && \
curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
apt install -y nodejs && \
apt clean && \
rm -rf /var/lib/apt/lists/*

COPY requirements-1.txt requirements-2.txt /tmp/

RUN  pip install --upgrade pip && \
pip install -r /tmp/requirements-1.txt && \
pip install -r /tmp/requirements-2.txt && \
rm -rf /tmp/requirements-1.txt /tmp/requirements-2.txt

RUN git clone https://github.com/mxcdevelop/mexc-api-sdk.git /tmp/mexc-api-sdk && \
cd /tmp/mexc-api-sdk/dist/python && \
tar -xzf *.tar.gz && \
pip install /tmp/mexc-api-sdk/dist/python/mexc_sdk-1.0.0-py3-none-any.whl && \
rm -rf /tmp/mexc-api-sdk

CMD ["cron", "-f"]

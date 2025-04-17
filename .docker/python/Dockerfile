FROM python:3.13.3-slim-bookworm

LABEL maintainer="Osiozekhai Aliu"

# Install cron, sudo, and dependencies
RUN apt update && apt upgrade -y && \
    apt install -y cron postgresql-client nano && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Start cron service
RUN service cron start

# Add cron job to run every minute
RUN echo "* * * * * echo 'Cron is running' >> /var/log/cron.log 2>&1" | crontab -

# Set nano as the default editor
RUN echo 'export EDITOR=nano' >> /root/.bashrc
RUN echo 'export EDITOR=nano' >> /root/.profile

# Ensure cron starts on container startup
CMD ["cron", "-f"]
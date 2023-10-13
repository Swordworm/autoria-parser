FROM python:3.11.0
SHELL ["/bin/bash", "-l", "-c"]

ARG TZ=UTC
ENV TZ ${TZ}

RUN apt-get update && apt-get install -y curl wget gnupg2 systemd gettext-base
RUN set -eu && \
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash && \
    export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" && \
    nvm install 16.20.0 && \
    npm install -g pm2

RUN python -m pip install --upgrade pip && python -m pip install poetry
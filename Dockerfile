# 每日黃曆 — Docker 開發／建置環境
# 線上 GitHub Pages 仍為純靜態檔，不受此 Dockerfile 影響。
#
# targets:
#   tools  — Python + git，跑 rebuild 腳本、測試
#   web    — nginx 靜態預覽（可直接 compose up）

# ---------- tools：建置與開發腳本 ----------
FROM python:3.12-slim-bookworm AS tools

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      curl \
      openssh-client \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI（可選：docker compose run tools gh ...）
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# 原始碼以 volume 掛載為主；COPY 僅供無掛載時的離線建置
COPY . .

# 預設進入 shell，方便互動開發
CMD ["bash"]

# ---------- web：靜態站預覽（nginx）----------
FROM nginx:1.27-alpine AS web

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
# 映像內含一份靜態檔；compose 會用 volume 覆蓋為本機最新碼
COPY . /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

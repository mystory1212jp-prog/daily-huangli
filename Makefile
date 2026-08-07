# 每日黃曆 — Docker 開發快捷指令
# 線上 GitHub Pages 流程不變：改完 → commit → push main 即可。

PORT ?= 8765
export HUANGLI_PORT := $(PORT)

.PHONY: help docker-build docker-up docker-down docker-logs docker-shell \
	docker-rebuild-db docker-rebuild-personal docker-rebuild-all \
	docker-test docker-ps status

help:
	@echo "每日黃曆 Docker 指令"
	@echo ""
	@echo "  make docker-build           建置 web + tools 映像"
	@echo "  make docker-up              啟動預覽 http://localhost:$(PORT)"
	@echo "  make docker-down            停止預覽"
	@echo "  make docker-logs            看 web 日誌"
	@echo "  make docker-shell           進入 tools 容器 bash"
	@echo "  make docker-rebuild-db      重建 core-db / huangli-db（節氣精算）"
	@echo "  make docker-rebuild-personal 重建個人運勢 daily-facts"
	@echo "  make docker-rebuild-all     重建全部資料 + 嵌入節氣養生"
	@echo "  make docker-test            跑節氣／八字快速檢驗"
	@echo ""
	@echo "上傳 GitHub（在主機或 tools 內皆可）："
	@echo "  git add -A && git commit -m '...' && git push origin main"
	@echo "GitHub Pages 會自動部署靜態檔，無需 Docker 在線上執行。"

docker-build:
	docker compose build web
	docker compose --profile tools build tools

docker-up:
	docker compose up -d web
	@echo "預覽：http://localhost:$(PORT)"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f web

docker-shell:
	docker compose --profile tools run --rm tools bash

docker-rebuild-db:
	docker compose --profile tools run --rm tools python scripts/build_db.py

docker-rebuild-personal:
	docker compose --profile tools run --rm tools python scripts/build_personal_system.py

docker-rebuild-jieqi:
	docker compose --profile tools run --rm tools python scripts/embed_jieqi_yangsheng.py

docker-rebuild-all: docker-rebuild-db docker-rebuild-personal docker-rebuild-jieqi
	@echo "全部資料已重建（寫回本機 ./data ./lib）"

docker-test:
	docker compose --profile tools run --rm tools python scripts/verify_calendar.py

docker-ps:
	docker compose ps -a

status:
	@echo "本機 git:"; git status -sb || true
	@echo "compose:"; docker compose ps -a 2>/dev/null || true

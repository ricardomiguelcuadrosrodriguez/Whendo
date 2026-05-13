.PHONY: help install install-web dev dev-web test up down logs clean

help:
	@echo "whendo — make targets"
	@echo ""
	@echo "Backend (server/):"
	@echo "  make install      Install Python deps"
	@echo "  make dev          Run server with auto-reload on :8000"
	@echo "  make test         Run pytest"
	@echo ""
	@echo "Frontend (web/):"
	@echo "  make install-web  Install npm deps"
	@echo "  make dev-web      Run Next.js dev server on :3000"
	@echo ""
	@echo "Full stack:"
	@echo "  make up           Start everything with docker compose"
	@echo "  make down         Stop docker compose"
	@echo "  make logs         Tail server logs"
	@echo "  make clean        Remove caches and the local DB"

install:
	cd server && pip install -r requirements.txt

install-web:
	cd web && npm install

dev:
	cd server && python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd web && npm run dev

test:
	cd server && pytest -v

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	rm -rf data/whendo.db

PYTHON ?= python3

.PHONY: dev start stop logs test

dev:
	./scripts/dev_start.sh

start:
	./scripts/dev_start.sh

stop:
	-pkill -f "uvicorn apps.api.main"
	-docker-compose down || true

logs:
	tail -n 200 -f logs/uvicorn.log

test:
	SKIP_HEAVY_DEPS=1 pytest -q

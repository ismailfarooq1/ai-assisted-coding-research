PYTHON ?= python3

.PHONY: setup check doctor backend-test frontend-install frontend-check
setup:
	$(PYTHON) ../../tools/setup.py setup prepared-context
check:
	$(PYTHON) ../../tools/setup.py check prepared-context
doctor:
	$(PYTHON) ../../tools/setup.py doctor
backend-test:
	cd project && go test ./...
frontend-install:
	cd project/web && pnpm install --frozen-lockfile
frontend-check:
	cd project/web && pnpm lint && pnpm test && pnpm build

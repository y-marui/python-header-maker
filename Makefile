.PHONY: build desktop install lint format type test all update-charter

build:
	uv sync
	uv run header-maker build
	uv run header-maker install-app --force

desktop:
	uv run header-maker desktop --force

install: build desktop

lint:
	uv run ruff check .

format:
	uv run ruff format .

type:
	uv run mypy src

test:
	uv run pytest

all: lint type test

update-charter:
	curl -fsSL https://raw.githubusercontent.com/y-marui/dev-charter/main/scripts/install.sh | CHARTER_UPDATE_ONLY=1 bash

.PHONY: build desktop install lint format type test all setup-charter update-charter

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

## dev-charter helpers
setup-charter:
	git remote add dev-charter https://github.com/y-marui/dev-charter
	git fetch dev-charter
	git subtree add --prefix=docs/dev-charter dev-charter main --squash

update-charter:
	git subtree pull --prefix=docs/dev-charter dev-charter main --squash

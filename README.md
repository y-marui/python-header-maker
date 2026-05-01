# python-header-maker

> **This is the reference (English) version.**
> The canonical (Japanese) version is [README-jp.md](README-jp.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/y-marui/python-header-maker/actions/workflows/ci.yml/badge.svg)](https://github.com/y-marui/python-header-maker/actions/workflows/ci.yml)
[![Charter Check](https://github.com/y-marui/python-header-maker/actions/workflows/dev-charter-check.yml/badge.svg)](https://github.com/y-marui/python-header-maker/actions/workflows/dev-charter-check.yml)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/y-marui?style=social)](https://github.com/sponsors/y-marui)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-yellow.svg)](https://www.buymeacoffee.com/y.marui)

GUI tool for creating note.com article header images (1280×670). Drag & drop images onto the macOS app to add titles, themes, and period labels with crop control.

## Setup

```sh
git clone https://github.com/y-marui/python-header-maker.git
cd python-header-maker
make install
```

`make install` builds the Automator app, installs it to `/Applications/Note Header Maker/`, and creates a shortcut on the Desktop.

## Usage

Launch `Note Header.app` from the Desktop or Applications, or drag image files directly onto the app icon.

| Command | Description |
|---|---|
| `make build` | Build Automator app and install to `/Applications/Note Header Maker/` |
| `make desktop` | Create Desktop shortcut |
| `make install` | `build` + `desktop` |
| `make lint` | `ruff check .` |
| `make type` | `mypy src` |
| `make test` | `pytest` |
| `make all` | lint + type + test |

## Requirements

- macOS (Automator / osascript)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

## License

MIT License — see [LICENSE](LICENSE)

---
*This document has a Japanese canonical version [README-jp.md](README-jp.md). Update both in the same commit when editing.*

# python-header-maker

> **このファイルは正本（日本語版）です。**
> 英語版（参照）は [README.md](README.md) を参照してください。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/y-marui/python-header-maker/actions/workflows/ci.yml/badge.svg)](https://github.com/y-marui/python-header-maker/actions/workflows/ci.yml)
[![Charter Check](https://github.com/y-marui/python-header-maker/actions/workflows/dev-charter-check.yml/badge.svg)](https://github.com/y-marui/python-header-maker/actions/workflows/dev-charter-check.yml)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/y-marui?style=social)](https://github.com/sponsors/y-marui)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-yellow.svg)](https://www.buymeacoffee.com/y.marui)

note.com 用記事ヘッダー画像（1280×670）を作成する GUI ツール。macOS アプリに画像をドラッグ&ドロップして、タイトル・テーマ・期間ラベルをクロップ位置を調整しながら合成できます。

## Setup

```sh
git clone https://github.com/y-marui/python-header-maker.git
cd python-header-maker
make install
```

`make install` は Automator アプリのビルド・`/Applications/Note Header Maker/` へのインストール・デスクトップへのショートカット作成を一括で行います。

## Usage

デスクトップまたは Applications の `Note Header.app` を起動するか、アプリアイコンに画像ファイルをドラッグ&ドロップしてください。

| コマンド | 内容 |
|---|---|
| `make build` | Automator アプリをビルドして `/Applications/Note Header Maker/` にインストール |
| `make desktop` | デスクトップにショートカットを作成 |
| `make install` | `build` + `desktop` |
| `make lint` | `ruff check .` |
| `make type` | `mypy src` |
| `make test` | `pytest` |
| `make all` | lint + type + test |

## Requirements

- macOS（Automator / osascript）
- Python 3.11 以上
- [uv](https://github.com/astral-sh/uv)

## License

MIT License — [LICENSE](LICENSE) を参照

---
*この文書には英語版 [README.md](README.md) があります。編集時は同一コミットで更新してください。*

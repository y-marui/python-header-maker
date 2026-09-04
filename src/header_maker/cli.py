import plistlib
import shutil
import subprocess
from importlib.metadata import version as _pkg_version
from pathlib import Path

import typer

from .core import launch_gui

APP_NAME = "Note Header.app"
APP_INSTALL_DIR = Path("/Applications/Note Header Maker")

app = typer.Typer(no_args_is_help=True, add_completion=True)


def _shell_quote_for_applescript(path: str) -> str:
    """Shell-quote path for embedding in an AppleScript string literal."""
    shell_quoted = "'" + path.replace("'", "'\\''") + "'"
    return shell_quoted.replace('"', '\\"')


def _build_app() -> None:
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    app_path = build_dir / APP_NAME

    if app_path.exists():
        shutil.rmtree(app_path)

    cmd = shutil.which("header-maker")
    if not cmd:
        raise RuntimeError("header-maker not found in PATH")

    safe_cmd = _shell_quote_for_applescript(cmd)
    script = f"""
    on run
        do shell script "{safe_cmd} gui"
    end run

    on open dropped_items
        set cmd_str to "{safe_cmd} gui"
        repeat with f in dropped_items
            set cmd_str to cmd_str & " " & quoted form of (POSIX path of f)
        end repeat
        do shell script cmd_str
    end open
    """

    result = subprocess.run(
        ["osacompile", "-o", str(app_path), "-e", script],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"osacompile failed:\n{result.stderr}")

    _patch_info_plist(app_path)
    print("built:", app_path)


def _patch_info_plist(app_path: Path) -> None:
    plist_path = app_path / "Contents" / "Info.plist"

    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)

    plist["CFBundleDocumentTypes"] = [
        {
            "CFBundleTypeName": "Image",
            "CFBundleTypeRole": "Viewer",
            "LSHandlerRank": "Owner",
            "LSItemContentTypes": ["public.image"],
        }
    ]
    plist["NSAppleEventsUsageDescription"] = "Receive dropped files"

    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)


def _install_app(force: bool = False) -> None:
    src = Path("build") / APP_NAME
    if not src.exists():
        raise RuntimeError(f"'{src}' not found — run build first")

    APP_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    dst = APP_INSTALL_DIR / APP_NAME

    if dst.exists() or dst.is_symlink():
        if not force:
            print("already installed:", dst)
            return
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)

    shutil.copytree(src, dst)
    print("installed:", dst)


def _create_desktop_shortcut(force: bool = False) -> None:
    src = APP_INSTALL_DIR / APP_NAME
    if not src.exists():
        raise RuntimeError(f"'{src}' not found — run install-app first")

    dst = Path.home() / "Desktop" / APP_NAME

    if dst.exists() or dst.is_symlink():
        if not force:
            print("already exists:", dst)
            return
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)

    dst.symlink_to(src)
    print("shortcut created:", dst)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(_pkg_version("header-maker"))
        raise typer.Exit()


@app.callback()
def _main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """GUI tool for creating note.com article header images."""


@app.command()
def gui(
    files: list[Path] = typer.Argument(
        None, help="Image files to open (e.g. via drag & drop)."
    ),
) -> None:
    """Launch the GUI."""
    launch_gui([str(f) for f in files] if files else None)


@app.command(name="build")
def build() -> None:
    """Build the Automator app bundle."""
    _build_app()


@app.command(name="install-app")
def install_app(
    force: bool = typer.Option(
        False, "--force", help="Overwrite an existing installation."
    ),
) -> None:
    """Install the built app to /Applications."""
    _install_app(force)


@app.command(name="desktop")
def desktop(
    force: bool = typer.Option(
        False, "--force", help="Overwrite an existing shortcut."
    ),
) -> None:
    """Create a Desktop shortcut to the installed app."""
    _create_desktop_shortcut(force)


def main() -> None:
    app()

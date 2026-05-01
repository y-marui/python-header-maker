import argparse
import plistlib
import shutil
import subprocess
from pathlib import Path

from .core import launch_gui

APP_NAME = "Note Header.app"
APP_INSTALL_DIR = Path("/Applications/Note Header Maker")


def _shell_quote_for_applescript(path: str) -> str:
    """Shell-quote path for embedding in an AppleScript string literal."""
    shell_quoted = "'" + path.replace("'", "'\\''") + "'"
    return shell_quoted.replace('"', '\\"')


def build_app() -> None:
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


def install_app(force: bool = False) -> None:
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


def create_desktop_shortcut(force: bool = False) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("gui")
    sub.add_parser("build")

    p_install = sub.add_parser("install-app")
    p_install.add_argument("--force", action="store_true")

    p_desktop = sub.add_parser("desktop")
    p_desktop.add_argument("--force", action="store_true")

    args, rest = parser.parse_known_args()

    if args.cmd == "build":
        build_app()

    elif args.cmd == "install-app":
        install_app(args.force)

    elif args.cmd == "desktop":
        create_desktop_shortcut(args.force)

    elif args.cmd == "gui":
        launch_gui(rest or None)

    else:
        parser.print_help()

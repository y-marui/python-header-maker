import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageTk

BASE_WIDTH = 1280
BASE_HEIGHT = 670

_FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴ ProN W6.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Cache/Hiragino Sans GB W6.otf",
]


def _find_font() -> str | None:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def _applescript_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def send_macos_notification(title: str, message: str) -> None:
    safe_title = _applescript_escape(title)
    safe_message = _applescript_escape(message)
    script = f'display notification "{safe_message}" with title "{safe_title}"'
    subprocess.run(["osascript", "-e", script], check=False)


def _crop_image(
    img: Image.Image,
    base_width: int,
    base_height: int,
    crop_x: float = 0.5,
    crop_y: float = 0.5,
) -> Image.Image:
    """crop_x/crop_y: 0.0=左/上寄せ, 0.5=中央, 1.0=右/下寄せ"""
    src_w, src_h = img.size
    target_ratio = base_width / base_height

    if src_w / src_h > target_ratio:
        new_w = int(src_h * target_ratio)
        left = int((src_w - new_w) * crop_x)
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = int((src_h - new_h) * crop_y)
        img = img.crop((0, top, src_w, top + new_h))

    return img.resize((base_width, base_height), Image.Resampling.LANCZOS)


def _render_image(
    background_path: str,
    title: str,
    theme: str,
    period: str,
    crop_x: float = 0.5,
    crop_y: float = 0.5,
) -> Image.Image:
    font_path = _find_font()

    with Image.open(background_path) as src:
        img = _crop_image(src.convert("RGB"), BASE_WIDTH, BASE_HEIGHT, crop_x, crop_y)

    draw = ImageDraw.Draw(img)

    text_color = "white"
    edge_color = "#4e454a"

    def draw_text_with_border(
        text: str,
        position: tuple[float, float],
        font: ImageFont.FreeTypeFont,
        edge_width: int,
        anchor: str,
    ) -> None:
        x, y = position
        for adj_x in range(-edge_width, edge_width + 1):
            for adj_y in range(-edge_width, edge_width + 1):
                if adj_x == 0 and adj_y == 0:
                    continue
                draw.text(
                    (x + adj_x, y + adj_y),
                    text,
                    font=font,
                    fill=edge_color,
                    anchor=anchor,
                    align="center",
                )
        draw.text(
            position, text, font=font, fill=text_color, anchor=anchor, align="center"
        )

    def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        if font_path:
            return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()

    if theme:
        theme_font = load_font(int(BASE_HEIGHT * 0.10))
        assert isinstance(theme_font, ImageFont.FreeTypeFont)
        draw_text_with_border(
            theme,
            (BASE_WIDTH / 2 - BASE_HEIGHT * 0.88, BASE_HEIGHT * 0.10),
            theme_font,
            3,
            "la",
        )

    if period:
        period_font = load_font(int(BASE_HEIGHT * 0.10))
        assert isinstance(period_font, ImageFont.FreeTypeFont)
        draw_text_with_border(
            period,
            (BASE_WIDTH / 2 + BASE_HEIGHT * 0.88, BASE_HEIGHT * 0.90),
            period_font,
            3,
            "rs",
        )

    if title and font_path:
        title_max_width = BASE_HEIGHT * 1.76
        title_font_size = 10
        last_good_size = title_font_size
        title_font = ImageFont.truetype(font_path, title_font_size)

        def get_multiline_width(text: str, font: ImageFont.FreeTypeFont) -> float:
            lines = text.split("\n")
            return max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)

        while get_multiline_width(title, title_font) < title_max_width:
            if title_font_size > BASE_HEIGHT * 0.30:
                break
            last_good_size = title_font_size
            title_font_size += 2
            title_font = ImageFont.truetype(font_path, title_font_size)

        title_font = ImageFont.truetype(font_path, max(10, last_good_size))
        draw_text_with_border(
            title,
            (BASE_WIDTH / 2, BASE_HEIGHT / 2),
            title_font,
            6,
            "mm",
        )

    return img


def generate_styled_news_card(
    background_path: str,
    title: str,
    theme: str,
    period: str,
    crop_x: float = 0.5,
    crop_y: float = 0.5,
) -> None:
    output_path = Path(background_path).stem + "_add_char.png"
    output_path = str(Path(background_path).parent / output_path)

    try:
        img = _render_image(background_path, title, theme, period, crop_x, crop_y)
    except Exception as e:
        messagebox.showerror("Error", f"画像の読み込み失敗: {e}")
        return

    try:
        img.save(output_path)
    except Exception as e:
        messagebox.showerror("Error", f"保存失敗: {e}")
        return

    send_macos_notification("画像生成完了", f"{Path(output_path).name} を保存しました")


def _quit(root: tk.Tk) -> None:
    root.destroy()
    sys.exit()


def _show_title_screen(root: tk.Tk) -> None:
    for w in root.winfo_children():
        w.destroy()

    root.title("Note Header Maker")

    tk.Label(root, text="Note Header Maker", font=("Hiragino Sans", 22, "bold")).pack(
        expand=True
    )
    tk.Label(
        root,
        text="画像をドロップするか、ファイルを選択してください",
        fg="#666",
        font=("Hiragino Sans", 11),
    ).pack()

    def select_file() -> None:
        root.attributes("-topmost", False)
        paths = filedialog.askopenfilenames(
            title="画像を選択",
            filetypes=[
                ("画像ファイル", "*.png *.jpg *.jpeg *.webp"),
                ("すべて", "*.*"),
            ],
        )
        root.attributes("-topmost", True)
        if paths:
            _show_input_screen(root, list(paths))

    tk.Button(
        root, text="ファイルを選択", command=select_file, width=20, height=2
    ).pack(pady=30)


def _show_input_screen(root: tk.Tk, file_paths: list[str]) -> None:
    for w in root.winfo_children():
        w.destroy()

    root.title("一括テキスト入力")

    current_file = file_paths[0]
    remaining = file_paths[1:]
    has_more = len(remaining) > 0

    PREVIEW_W = 520
    PREVIEW_H = int(PREVIEW_W * BASE_HEIGHT / BASE_WIDTH)

    preview_frame = tk.Frame(root, width=PREVIEW_W, height=PREVIEW_H, bg="#333")
    preview_frame.pack_propagate(False)
    preview_frame.pack(pady=(10, 4))
    preview_label = tk.Label(preview_frame, bg="#333")
    preview_label.pack(fill="both", expand=True)
    photo_ref: list[ImageTk.PhotoImage | None] = [None]

    tk.Label(
        root, text="1行目: タイトル / 2行目: テーマ / 3行目: 期間", fg="#666"
    ).pack()

    txt_input = tk.Text(root, width=50, height=4, font=("Hiragino Sans", 14))
    txt_input.pack(padx=20, pady=5)
    txt_input.insert("1.0", "タイトル\nテーマ\n期間")
    txt_input.focus_set()

    tk.Label(root, text=current_file, fg="#666", wraplength=500).pack()

    status_label = tk.Label(root, text="", fg="red", wraplength=500)
    status_label.pack()

    crop_pos: list[float] = [0.5, 0.5]

    def get_inputs() -> tuple[str, str, str]:
        raw = txt_input.get("1.0", "end-1c").splitlines()
        title = raw[0].replace("\\n", "\n") if len(raw) > 0 else ""
        theme = raw[1] if len(raw) > 1 else ""
        period = raw[2] if len(raw) > 2 else ""
        return title, theme, period

    def update_preview() -> None:
        try:
            img = _render_image(
                current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1]
            )
            status_label.configure(text="")
        except Exception as e:
            status_label.configure(text=f"プレビューエラー: {e}")
            return
        img = img.resize((PREVIEW_W, PREVIEW_H), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        photo_ref[0] = photo
        preview_label.configure(image=photo)
        update_crop_indicator()

    MINI_W, MINI_H = 160, 120
    orig_w: int
    orig_h: int
    orig_thumb: Image.Image | None
    try:
        with Image.open(current_file) as _orig:
            converted = _orig.convert("RGB")
            orig_w, orig_h = converted.size
            converted.thumbnail((MINI_W, MINI_H), Image.Resampling.LANCZOS)
            orig_thumb = converted.copy()
    except Exception:
        orig_thumb, orig_w, orig_h = None, 1, 1
    thumb_w, thumb_h = orig_thumb.size if orig_thumb else (MINI_W, MINI_H)

    indicator_photo: list[ImageTk.PhotoImage | None] = [None]

    def update_crop_indicator() -> None:
        if orig_thumb is None:
            return
        thumb = orig_thumb.copy().convert("RGBA")
        tw, th = thumb.size
        target_ratio = BASE_WIDTH / BASE_HEIGHT
        sx, sy = tw / orig_w, th / orig_h

        if orig_w / orig_h > target_ratio:
            cw = orig_h * target_ratio
            left = (orig_w - cw) * crop_pos[0]
            rx0, ry0 = int(left * sx), 0
            rx1, ry1 = int((left + cw) * sx), th
        else:
            ch = orig_w / target_ratio
            top = (orig_h - ch) * crop_pos[1]
            rx0, ry0 = 0, int(top * sy)
            rx1, ry1 = tw, int((top + ch) * sy)

        gray = Image.new("RGBA", (tw, th), (128, 128, 128, 160))
        gray.paste((0, 0, 0, 0), (rx0, ry0, rx1, ry1))
        thumb = Image.alpha_composite(thumb, gray)

        ind_photo = ImageTk.PhotoImage(thumb.convert("RGB"))
        indicator_photo[0] = ind_photo
        indicator_label.configure(image=ind_photo)

    def move_crop(dx: float, dy: float) -> None:
        crop_pos[0] = max(0.0, min(1.0, crop_pos[0] + dx))
        crop_pos[1] = max(0.0, min(1.0, crop_pos[1] + dy))
        update_crop_indicator()
        update_preview()

    def reset_crop() -> None:
        crop_pos[0] = 0.5
        crop_pos[1] = 0.5
        update_crop_indicator()
        update_preview()

    dpad_row = tk.Frame(root)
    dpad_row.pack(pady=4)

    dpad = tk.Frame(dpad_row)
    dpad.pack(side="left", padx=(0, 12))
    tk.Button(dpad, text="↑", width=3, command=lambda: move_crop(0, -1)).grid(
        row=0, column=1, pady=1
    )
    tk.Button(dpad, text="←", width=3, command=lambda: move_crop(-1, 0)).grid(
        row=1, column=0, padx=1
    )
    tk.Button(dpad, text="中央", width=4, command=reset_crop).grid(row=1, column=1)
    tk.Button(dpad, text="→", width=3, command=lambda: move_crop(1, 0)).grid(
        row=1, column=2, padx=1
    )
    tk.Button(dpad, text="↓", width=3, command=lambda: move_crop(0, 1)).grid(
        row=2, column=1, pady=1
    )

    indicator_frame = tk.Frame(dpad_row, width=thumb_w, height=thumb_h, bg="#333")
    indicator_frame.pack_propagate(False)
    indicator_frame.pack(side="left")
    indicator_label = tk.Label(indicator_frame, bg="#333", cursor="fleur")
    indicator_label.pack(fill="both", expand=True)

    drag_start: list[float] = [0.0, 0.0, 0.5, 0.5]

    def on_drag_start(event: Any) -> None:
        drag_start[0] = event.x
        drag_start[1] = event.y
        drag_start[2] = crop_pos[0]
        drag_start[3] = crop_pos[1]

    def on_drag_motion(event: Any) -> None:
        dx = event.x - drag_start[0]
        dy = event.y - drag_start[1]
        target_ratio = BASE_WIDTH / BASE_HEIGHT
        sx = thumb_w / orig_w
        sy = thumb_h / orig_h
        if orig_w / orig_h > target_ratio:
            avail = (orig_w - orig_h * target_ratio) * sx
            crop_pos[0] = max(
                0.0, min(1.0, drag_start[2] + (dx / avail if avail > 0 else 0))
            )
        else:
            avail = (orig_h - orig_w / target_ratio) * sy
            crop_pos[1] = max(
                0.0, min(1.0, drag_start[3] + (dy / avail if avail > 0 else 0))
            )
        update_crop_indicator()

    def on_drag_end(_event: Any) -> None:
        update_preview()

    indicator_label.bind("<ButtonPress-1>", on_drag_start)
    indicator_label.bind("<B1-Motion>", on_drag_motion)
    indicator_label.bind("<ButtonRelease-1>", on_drag_end)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)

    if not has_more:

        def generate_and_title() -> None:
            generate_styled_news_card(
                current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1]
            )
            _show_title_screen(root)

        def generate_and_close() -> None:
            generate_styled_news_card(
                current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1]
            )
            _quit(root)

        root.bind("<Command-Return>", lambda _e: generate_and_close())

        tk.Button(btn_frame, text="更新", command=update_preview).grid(
            row=0, column=0, padx=3
        )
        tk.Button(btn_frame, text="生成", command=generate_and_title).grid(
            row=0, column=1, padx=3
        )
        tk.Button(btn_frame, text="生成して閉じる", command=generate_and_close).grid(
            row=0, column=2, padx=3
        )
        tk.Button(
            btn_frame, text="タイトル", command=lambda: _show_title_screen(root)
        ).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="終了", command=lambda: _quit(root)).grid(
            row=0, column=4, padx=3
        )
    else:

        def generate_and_next() -> None:
            generate_styled_news_card(
                current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1]
            )
            _show_input_screen(root, remaining)

        def skip_and_next() -> None:
            _show_input_screen(root, remaining)

        root.bind("<Command-Return>", lambda _e: generate_and_next())

        tk.Button(btn_frame, text="更新", command=update_preview).grid(
            row=0, column=0, padx=3
        )
        tk.Button(btn_frame, text="生成", command=generate_and_next).grid(
            row=0, column=1, padx=3
        )
        tk.Button(btn_frame, text="スキップして次", command=skip_and_next).grid(
            row=0, column=2, padx=3
        )
        tk.Button(
            btn_frame, text="タイトル", command=lambda: _show_title_screen(root)
        ).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="終了", command=lambda: _quit(root)).grid(
            row=0, column=4, padx=3
        )

    root.after(50, update_preview)


def launch_gui(file_paths: list[str] | None = None) -> None:
    root = tk.Tk()

    window_width = 560
    window_height = 680

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.attributes("-topmost", True)

    if file_paths:
        _show_input_screen(root, file_paths)
    else:
        _show_title_screen(root)

    root.mainloop()

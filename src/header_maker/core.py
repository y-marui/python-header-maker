import os
import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import subprocess

CROP_STEP = 0.1


def send_macos_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script])


def _crop_image(img, base_width, base_height, crop_x=0.5, crop_y=0.5):
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


def _render_image(background_path, title, theme, period, crop_x=0.5, crop_y=0.5):
    base_width, base_height = 1280, 670
    with Image.open(background_path) as img:
        img = img.convert("RGB")
        img = _crop_image(img, base_width, base_height, crop_x, crop_y)
        draw = ImageDraw.Draw(img)

    font_path = "/System/Library/Fonts/Cache/Hiragino Sans GB W6.otf"
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

    text_color = "white"
    edge_color = "#4e454a"

    def draw_text_with_border(draw, text, position, font, text_color, edge_color, edge_width, anchor):
        x, y = position
        for adj_x in range(-edge_width, edge_width + 1):
            for adj_y in range(-edge_width, edge_width + 1):
                if adj_x == 0 and adj_y == 0:
                    continue
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=edge_color, anchor=anchor, align="center")
        draw.text(position, text, font=font, fill=text_color, anchor=anchor, align="center")

    if theme:
        theme_font = ImageFont.truetype(font_path, int(base_height * 0.10))
        draw_text_with_border(draw, theme, (base_width / 2 - base_height * 0.88, base_height * 0.10), theme_font, text_color, edge_color, 3, "la")

    if period:
        period_font = ImageFont.truetype(font_path, int(base_height * 0.10))
        draw_text_with_border(draw, period, (base_width / 2 + base_height * 0.88, base_height * 0.90), period_font, text_color, edge_color, 3, "rs")

    if title:
        title_max_width = base_height * 1.76
        title_font_size = 10
        title_font = ImageFont.truetype(font_path, title_font_size)

        def get_multiline_width(text, font):
            lines = text.split('\n')
            return max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)

        while get_multiline_width(title, title_font) < title_max_width:
            if title_font_size > base_height * 0.30:
                break
            title_font_size += 2
            title_font = ImageFont.truetype(font_path, title_font_size)

        title_font = ImageFont.truetype(font_path, max(10, title_font_size - 2))
        draw_text_with_border(draw, title, (base_width / 2, base_height / 2), title_font, text_color, edge_color, 6, "mm")

    return img


def generate_styled_news_card(background_path, title, theme, period, crop_x=0.5, crop_y=0.5):
    base, _ = os.path.splitext(background_path)
    output_path = f"{base}_add_char.png"

    try:
        img = _render_image(background_path, title, theme, period, crop_x, crop_y)
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Error", f"画像の読み込み失敗: {e}")
        return

    img.save(output_path, quality=95)
    send_macos_notification("画像生成完了", f"{os.path.basename(output_path)} を保存しました")


def _show_title_screen(root):
    for w in root.winfo_children():
        w.destroy()

    root.title("Note Header Maker")

    tk.Label(root, text="Note Header Maker", font=("Hiragino Sans", 22, "bold")).pack(expand=True)
    tk.Label(root, text="画像をドロップするか、ファイルを選択してください", fg="#666", font=("Hiragino Sans", 11)).pack()

    def select_file():
        root.attributes("-topmost", False)
        paths = filedialog.askopenfilenames(
            title="画像を選択",
            filetypes=[("画像ファイル", "*.png *.jpg *.jpeg *.webp"), ("すべて", "*.*")],
        )
        root.attributes("-topmost", True)
        if paths:
            _show_input_screen(root, list(paths))

    tk.Button(root, text="ファイルを選択", command=select_file, width=20, height=2).pack(pady=30)


def _show_input_screen(root, file_paths):
    for w in root.winfo_children():
        w.destroy()

    root.title("一括テキスト入力")

    current_file = file_paths[0]
    remaining = file_paths[1:]
    has_more = len(remaining) > 0

    PREVIEW_W = 520
    PREVIEW_H = int(PREVIEW_W * 670 / 1280)

    preview_label = tk.Label(root, bg="#333", width=PREVIEW_W, height=PREVIEW_H)
    preview_label.pack(pady=(10, 4))
    photo_ref = [None]

    tk.Label(root, text="1行目: タイトル / 2行目: テーマ / 3行目: 期間", fg="#666").pack()

    txt_input = tk.Text(root, width=50, height=4, font=("Hiragino Sans", 14))
    txt_input.pack(padx=20, pady=5)
    txt_input.insert("1.0", "タイトル\nテーマ\n期間")
    txt_input.focus_set()

    tk.Label(root, text=current_file, fg="#666", wraplength=500).pack()

    crop_pos = [0.5, 0.5]

    def get_inputs():
        raw = txt_input.get("1.0", "end-1c").splitlines()
        title = raw[0].replace("\\n", "\n") if len(raw) > 0 else ""
        theme = raw[1] if len(raw) > 1 else ""
        period = raw[2] if len(raw) > 2 else ""
        return title, theme, period

    def update_preview():
        try:
            img = _render_image(current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1])
        except Exception:
            return
        img = img.resize((PREVIEW_W, PREVIEW_H), Image.Resampling.LANCZOS)
        photo_ref[0] = ImageTk.PhotoImage(img)
        preview_label.configure(image=photo_ref[0])
        update_crop_indicator()

    MINI_W, MINI_H = 160, 120
    try:
        with Image.open(current_file) as _orig:
            _orig = _orig.convert("RGB")
            orig_w, orig_h = _orig.size
            _orig.thumbnail((MINI_W, MINI_H), Image.Resampling.LANCZOS)
            orig_thumb = _orig.copy()
    except Exception:
        orig_thumb, orig_w, orig_h = None, 1, 1
    thumb_w, thumb_h = orig_thumb.size if orig_thumb else (MINI_W, MINI_H)

    indicator_photo = [None]

    def update_crop_indicator():
        if orig_thumb is None:
            return
        thumb = orig_thumb.copy().convert("RGBA")
        tw, th = thumb.size
        target_ratio = 1280 / 670
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

        indicator_photo[0] = ImageTk.PhotoImage(thumb.convert("RGB"))
        indicator_label.configure(image=indicator_photo[0])

    def move_crop(dx, dy):
        crop_pos[0] = max(0.0, min(1.0, crop_pos[0] + dx))
        crop_pos[1] = max(0.0, min(1.0, crop_pos[1] + dy))
        update_crop_indicator()
        update_preview()

    def reset_crop():
        crop_pos[0] = 0.5
        crop_pos[1] = 0.5
        update_crop_indicator()
        update_preview()

    dpad_row = tk.Frame(root)
    dpad_row.pack(pady=4)

    dpad = tk.Frame(dpad_row)
    dpad.pack(side="left", padx=(0, 12))
    tk.Button(dpad, text="↑", width=3, command=lambda: move_crop(0, -1)).grid(row=0, column=1, pady=1)
    tk.Button(dpad, text="←", width=3, command=lambda: move_crop(-1, 0)).grid(row=1, column=0, padx=1)
    tk.Button(dpad, text="中央", width=4, command=reset_crop).grid(row=1, column=1)
    tk.Button(dpad, text="→", width=3, command=lambda: move_crop(1, 0)).grid(row=1, column=2, padx=1)
    tk.Button(dpad, text="↓", width=3, command=lambda: move_crop(0, 1)).grid(row=2, column=1, pady=1)

    indicator_label = tk.Label(dpad_row, bg="#333", width=thumb_w, height=thumb_h, cursor="fleur")
    indicator_label.pack(side="left")

    drag_start = [0, 0, 0.5, 0.5]

    def on_drag_start(event):
        drag_start[0] = event.x
        drag_start[1] = event.y
        drag_start[2] = crop_pos[0]
        drag_start[3] = crop_pos[1]

    def on_drag_motion(event):
        dx = event.x - drag_start[0]
        dy = event.y - drag_start[1]
        target_ratio = 1280 / 670
        sx = thumb_w / orig_w
        sy = thumb_h / orig_h
        if orig_w / orig_h > target_ratio:
            avail = (orig_w - orig_h * target_ratio) * sx
            crop_pos[0] = max(0.0, min(1.0, drag_start[2] + (dx / avail if avail > 0 else 0)))
        else:
            avail = (orig_h - orig_w / target_ratio) * sy
            crop_pos[1] = max(0.0, min(1.0, drag_start[3] + (dy / avail if avail > 0 else 0)))
        update_crop_indicator()

    def on_drag_end(_event):
        update_preview()

    indicator_label.bind("<ButtonPress-1>", on_drag_start)
    indicator_label.bind("<B1-Motion>", on_drag_motion)
    indicator_label.bind("<ButtonRelease-1>", on_drag_end)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)

    if not has_more:
        def generate_and_title():
            generate_styled_news_card(current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1])
            _show_title_screen(root)

        def generate_and_close():
            generate_styled_news_card(current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1])
            sys.exit()

        root.bind("<Command-Return>", lambda e: generate_and_close())

        tk.Button(btn_frame, text="更新", command=update_preview).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="生成", command=generate_and_title).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="生成して閉じる", command=generate_and_close).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="タイトル", command=lambda: _show_title_screen(root)).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="終了", command=sys.exit).grid(row=0, column=4, padx=3)
    else:
        def generate_and_next():
            generate_styled_news_card(current_file, *get_inputs(), crop_x=crop_pos[0], crop_y=crop_pos[1])
            _show_input_screen(root, remaining)

        def skip_and_next():
            _show_input_screen(root, remaining)

        root.bind("<Command-Return>", lambda e: generate_and_next())

        tk.Button(btn_frame, text="更新", command=update_preview).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="生成", command=generate_and_next).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="スキップして次", command=skip_and_next).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="タイトル", command=lambda: _show_title_screen(root)).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="終了", command=sys.exit).grid(row=0, column=4, padx=3)

    root.after(50, update_preview)


def launch_gui(file_paths=None):
    root = tk.Tk()

    window_width = 560
    window_height = 660

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

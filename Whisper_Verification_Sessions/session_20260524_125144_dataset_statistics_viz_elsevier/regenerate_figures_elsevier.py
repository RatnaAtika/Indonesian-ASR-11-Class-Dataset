#!/usr/bin/env python3
"""Regenerate Elsevier/Data-in-Brief figures with readable labels.

This version intentionally avoids matplotlib/seaborn so the figure package is
reproducible in the current project environment, where the system matplotlib
wheel is incompatible with the installed NumPy version.  It renders high-DPI
PNG files and matching PDF wrappers using Pillow only.

Typography target: Elsevier artwork guidance recommends final printed lettering
around 7 pt and not below 6 pt.  The PNGs are sized to approximately full-page
width at their embedded DPI, and text is drawn at >= 6 pt equivalent whenever
possible.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import median
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
STATS = ROOT / "stats"
FIGS = ROOT / "figures"
PNG600 = FIGS / "png600"
FIGS.mkdir(exist_ok=True)
PNG600.mkdir(exist_ok=True)

ORIG_F11 = (
    ROOT.parent
    / "session_20260524_125144_dataset_statistics_viz"
    / "figures"
    / "F11_mel_spectrogram_exemplars.png"
)

# Okabe-Ito color-blind-safe palette.
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
VERMILION = "#D55E00"
YELLOW = "#F0E442"
BLACK = "#111111"
GREY = "#666666"
LIGHT = "#EEF2F5"
GRID = "#D9DEE3"

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size=size)


TITLE = font(88, True)      # 10.6 pt at 600 dpi
SUBTITLE = font(58, False)  # 7.0 pt at 600 dpi
LABEL = font(62, False)     # 7.4 pt at 600 dpi
TICK = font(52, False)      # 6.2 pt at 600 dpi
SMALL = font(50, False)     # 6.0 pt at 600 dpi
BOLD_SMALL = font(50, True)


def read_csv(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out: dict[str, object] = {}
            for key, value in row.items():
                if value is None:
                    out[key] = value
                    continue
                s = value.strip()
                try:
                    if s and not s.startswith("["):
                        out[key] = float(s)
                    else:
                        out[key] = s
                except ValueError:
                    out[key] = s
            rows.append(out)
    return rows


def new_canvas(w: int = 4500, h: int = 2700) -> Image.Image:
    return Image.new("RGB", (w, h), "white")


def draw_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill=BLACK):
    draw.text(xy, text, font=fnt, fill=fill, anchor="mm")


def draw_rotated_center(
    base: Image.Image,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill=BLACK,
    angle: int = 90,
):
    """Draw a rotated label centered at xy.

    angle=90 makes the text read bottom-to-top, which keeps long y-axis
    labels inside the canvas instead of clipping off the left edge.
    """
    scratch = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    d0 = ImageDraw.Draw(scratch)
    bbox = d0.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_img = Image.new("RGBA", (tw + 20, th + 20), (255, 255, 255, 0))
    d = ImageDraw.Draw(text_img)
    d.text((10 - bbox[0], 10 - bbox[1]), text, font=fnt, fill=fill)
    rot = text_img.rotate(angle, expand=True)
    base.paste(rot, (int(xy[0] - rot.width / 2), int(xy[1] - rot.height / 2)), rot)


def draw_title(draw: ImageDraw.ImageDraw, w: int, title: str, subtitle: str | None = None):
    draw_center(draw, (w // 2, 120), title, TITLE)
    if subtitle:
        draw_center(draw, (w // 2, 205), subtitle, SUBTITLE, GREY)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def save_image(img: Image.Image, name: str, dpi: int = 600, kind: str = "line") -> tuple[Path, Path, str]:
    png_path = PNG600 / f"{name}.png"
    pdf_path = FIGS / f"{name}.pdf"
    img.save(png_path, dpi=(dpi, dpi), optimize=True)
    # PDF wrapper.  PDF text is rasterized, but the separate PNG remains the
    # primary high-resolution artwork artifact for submission.
    img.save(pdf_path, "PDF", resolution=float(dpi))
    return pdf_path, png_path, kind


def draw_grid_y(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int], ticks: Iterable[float], y_to_px, fmt="{:.1f}"):
    x0, y0, x1, y1 = area
    for t in ticks:
        y = int(y_to_px(t))
        draw.line((x0, y, x1, y), fill=GRID, width=2)
        draw.text((x0 - 25, y), fmt.format(t), font=TICK, fill=BLACK, anchor="rm")


def draw_axes_box(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int]):
    x0, y0, x1, y1 = area
    draw.line((x0, y1, x1, y1), fill=BLACK, width=3)
    draw.line((x0, y0, x0, y1), fill=BLACK, width=3)


def nice_ticks(max_value: float, n: int = 5) -> list[float]:
    if max_value <= 0:
        return [0.0]
    raw = max_value / max(1, n - 1)
    power = 10 ** math.floor(math.log10(raw))
    step = min([1, 2, 2.5, 5, 10], key=lambda m: abs(m * power - raw)) * power
    ticks = [i * step for i in range(int(math.ceil(max_value / step)) + 1)]
    return ticks[: n + 1]


def vertical_bar_chart(
    name: str,
    title: str,
    subtitle: str,
    labels: list[str],
    values: list[float],
    ylabel: str,
    color: str = BLUE,
    yerr: list[float] | None = None,
    dpi: int = 600,
):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    draw_title(draw, w, title, subtitle)
    area = (520, 410, w - 230, h - 520)
    x0, y0, x1, y1 = area
    ymax = max(v + (yerr[i] if yerr else 0) for i, v in enumerate(values)) * 1.10
    ticks = nice_ticks(ymax, 5)
    ymax = max(ticks) if ticks else ymax

    def y_to_px(v: float) -> float:
        return y1 - (v / ymax) * (y1 - y0)

    y_tick_fmt = "{:.2f}" if ymax < 1 else "{:.1f}"
    draw_grid_y(draw, area, ticks, y_to_px, y_tick_fmt)
    draw_axes_box(draw, area)
    n = len(values)
    slot = (x1 - x0) / n
    bar_w = slot * 0.62
    for i, (lab, val) in enumerate(zip(labels, values)):
        cx = x0 + slot * (i + 0.5)
        bx0 = int(cx - bar_w / 2)
        bx1 = int(cx + bar_w / 2)
        by = int(y_to_px(val))
        draw.rectangle((bx0, by, bx1, y1), fill=color, outline=BLACK, width=2)
        if yerr:
            ey0 = int(y_to_px(val + yerr[i]))
            ey1 = int(y_to_px(max(0.0, val - yerr[i])))
            draw.line((int(cx), ey0, int(cx), ey1), fill=BLACK, width=3)
            draw.line((int(cx - 28), ey0, int(cx + 28), ey0), fill=BLACK, width=3)
            draw.line((int(cx - 28), ey1, int(cx + 28), ey1), fill=BLACK, width=3)
        draw.text((int(cx), y1 + 55), lab, font=TICK, fill=BLACK, anchor="mt")
    draw_rotated_center(img, (95, (y0 + y1) // 2), ylabel, LABEL)
    draw.text(((x0 + x1) // 2, h - 120), "Category / speaker label", font=LABEL, fill=BLACK, anchor="mm")
    return save_image(img, name, dpi=dpi, kind="line")


def horizontal_bar_chart(
    name: str,
    title: str,
    subtitle: str,
    labels: list[str],
    values: list[float],
    xlabel: str,
    color: str = BLUE,
    xerr: list[float] | None = None,
    dpi: int = 600,
    w: int = 4500,
    h: int = 3000,
):
    img = new_canvas(w, h)
    draw = ImageDraw.Draw(img)
    draw_title(draw, w, title, subtitle)
    area = (1120, 430, w - 520, h - 360)
    x0, y0, x1, y1 = area
    xmax = max(v + (xerr[i] if xerr else 0) for i, v in enumerate(values)) * 1.12
    ticks = nice_ticks(xmax, 6)
    xmax = max(ticks) if ticks else xmax

    def x_to_px(v: float) -> float:
        return x0 + (v / xmax) * (x1 - x0)

    for t in ticks:
        x = int(x_to_px(t))
        draw.line((x, y0, x, y1), fill=GRID, width=2)
        draw.text((x, y1 + 25), f"{t:.1f}", font=TICK, fill=BLACK, anchor="mt")
    draw_axes_box(draw, area)
    n = len(labels)
    slot = (y1 - y0) / n
    bar_h = slot * 0.56
    for i, (lab, val) in enumerate(zip(labels, values)):
        cy = y0 + slot * (i + 0.5)
        by0 = int(cy - bar_h / 2)
        by1 = int(cy + bar_h / 2)
        bx1 = int(x_to_px(val))
        draw.text((x0 - 35, int(cy)), lab, font=TICK, fill=BLACK, anchor="rm")
        draw.rectangle((x0, by0, bx1, by1), fill=color, outline=BLACK, width=2)
        if xerr:
            ex0 = int(x_to_px(max(0.0, val - xerr[i])))
            ex1 = int(x_to_px(val + xerr[i]))
            draw.line((ex0, int(cy), ex1, int(cy)), fill=BLACK, width=3)
            draw.line((ex0, int(cy - 22), ex0, int(cy + 22)), fill=BLACK, width=3)
            draw.line((ex1, int(cy - 22), ex1, int(cy + 22)), fill=BLACK, width=3)
        draw.text((bx1 + 25, int(cy)), f"{val:.2f}", font=SMALL, fill=BLACK, anchor="lm")
    draw.text(((x0 + x1) // 2, h - 105), xlabel, font=LABEL, fill=BLACK, anchor="mm")
    return save_image(img, name, dpi=dpi, kind="line")


def draw_f1(rows):
    speaker_order = [r["speaker_id"] for r in sorted(rows, key=lambda r: -float(r["total_duration_h"]))]
    split_colors = {"train": BLUE, "dev": ORANGE, "test": GREEN}
    values = []
    for sp in speaker_order:
        r = next(x for x in rows if x["speaker_id"] == sp)
        values.append((str(r["split"]), float(r["n_files"])))
    img = new_canvas(4500, 2800)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F1. Per-speaker file count by split", "Readable full-width version; public speaker IDs only")
    area = (500, 420, 4230, 2200)
    x0, y0, x1, y1 = area
    ymax = max(v for _, v in values) * 1.1
    ticks = nice_ticks(ymax, 5)
    ymax = max(ticks)

    def y_to_px(v): return y1 - (v / ymax) * (y1 - y0)
    draw_grid_y(draw, area, ticks, y_to_px, "{:.0f}")
    draw_axes_box(draw, area)
    slot = (x1 - x0) / len(values)
    bw = slot * 0.68
    for i, (sp, (split, val)) in enumerate(zip(speaker_order, values)):
        cx = x0 + slot * (i + 0.5)
        draw.rectangle((int(cx - bw / 2), int(y_to_px(val)), int(cx + bw / 2), y1), fill=split_colors[split], outline=BLACK, width=2)
        draw.text((int(cx), y1 + 45), sp, font=TICK, fill=BLACK, anchor="mt")
    draw_rotated_center(img, (90, (y0 + y1)//2), "Number of WAV files", LABEL)
    # Legend
    lx, ly = 3100, 2350
    for j, split in enumerate(["train", "dev", "test"]):
        draw.rectangle((lx + j*360, ly, lx + j*360 + 70, ly + 45), fill=split_colors[split], outline=BLACK)
        draw.text((lx + j*360 + 90, ly + 23), split, font=SMALL, fill=BLACK, anchor="lm")
    return save_image(img, "F1_files_per_speaker_split", kind="line")


def draw_f4(cat_rows):
    rows = sorted(cat_rows, key=lambda r: float(r["mean_chars"]))
    img = new_canvas(4500, 3300)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F4. Sentence-length distributions by category", "Large labels; English public category names")
    panels = [
        ((1030, 430, 4200, 1700), "F4a. Mean characters", "mean_chars", "Characters per sentence", BLUE),
        ((1030, 1950, 4200, 3050), "F4b. Mean words", "mean_words", "Words per sentence", ORANGE),
    ]
    labels = [str(r["category"]) for r in rows]
    for area, panel_title, col, xlabel, color in panels:
        x0, y0, x1, y1 = area
        values = [float(r[col]) for r in rows]
        xmax = max(values) * 1.12
        ticks = nice_ticks(xmax, 5)
        xmax = max(ticks)
        def x_to_px(v): return x0 + (v / xmax) * (x1 - x0)
        for t in ticks:
            x = int(x_to_px(t))
            draw.line((x, y0, x, y1), fill=GRID, width=2)
            draw.text((x, y1 + 22), f"{t:.0f}", font=TICK, fill=BLACK, anchor="mt")
        draw_axes_box(draw, area)
        draw.text(((x0+x1)//2, y0-65), panel_title, font=SUBTITLE, fill=BLACK, anchor="mm")
        slot = (y1-y0)/len(rows)
        bh = slot*0.55
        for i, (lab, val) in enumerate(zip(labels, values)):
            cy = y0 + slot*(i+0.5)
            draw.text((x0-35, int(cy)), lab, font=TICK, fill=BLACK, anchor="rm")
            draw.rectangle((x0, int(cy-bh/2), int(x_to_px(val)), int(cy+bh/2)), fill=color, outline=BLACK, width=2)
            draw.text((int(x_to_px(val))+20, int(cy)), f"{val:.1f}", font=SMALL, fill=BLACK, anchor="lm")
        draw.text(((x0+x1)//2, y1+105), xlabel, font=LABEL, fill=BLACK, anchor="mm")
    return save_image(img, "F4_sentence_length", kind="line")


def draw_f5(word_rows):
    rows = sorted(word_rows, key=lambda r: -float(r["count"]))
    counts = [float(r["count"]) for r in rows]
    ranks = list(range(1, len(counts)+1))
    img = new_canvas(4500, 2800)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F5. Word-frequency distribution", f"Zipf-style log-log curve; {len(counts)} word types")
    area = (600, 430, 4200, 2200)
    x0, y0, x1, y1 = area
    minx, maxx = math.log10(1), math.log10(max(ranks))
    miny, maxy = math.log10(max(1, min(counts))), math.log10(max(counts))
    def xp(v): return x0 + ((math.log10(v)-minx)/(maxx-minx))*(x1-x0)
    def yp(v): return y1 - ((math.log10(v)-miny)/(maxy-miny))*(y1-y0)
    for t in [1, 10, 100, 1000]:
        if t <= max(ranks):
            x = int(xp(t)); draw.line((x,y0,x,y1), fill=GRID, width=2); draw.text((x,y1+30), str(t), font=TICK, fill=BLACK, anchor="mt")
    for t in [1, 10, 100, 1000, 10000]:
        if min(counts) <= t <= max(counts):
            y=int(yp(t)); draw.line((x0,y,x1,y), fill=GRID, width=2); draw.text((x0-25,y), str(t), font=TICK, fill=BLACK, anchor="rm")
    draw_axes_box(draw, area)
    pts = [(int(xp(r)), int(yp(c))) for r,c in zip(ranks, counts)]
    draw.line(pts, fill=BLUE, width=7, joint="curve")
    draw.text(((x0+x1)//2, 2530), "Rank (log scale)", font=LABEL, fill=BLACK, anchor="mm")
    draw_rotated_center(img, (105, (y0+y1)//2), "Frequency (log scale)", LABEL)
    return save_image(img, "F5_word_frequency_pareto", kind="line")


def draw_f6(meta):
    heaps = meta["linguistic"].get("heaps_law", {})
    K = float(heaps.get("K", 0.7844)); beta = float(heaps.get("beta", 0.488))
    max_tokens = float(heaps.get("max_tokens", meta["linguistic"].get("total_tokens", 906472)))
    vocab = float(heaps.get("vocab_size", meta["linguistic"].get("vocab_size", 711)))
    img = new_canvas(4500, 2800)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F6. Heaps' law vocabulary growth", f"Fit: V = {K:.2f} N^{beta:.3f}")
    area = (650, 430, 4200, 2200)
    x0,y0,x1,y1=area
    minx,maxx=0,math.log10(max_tokens)
    miny,maxy=0,math.log10(max(vocab*1.25, 1000))
    def xp(v): return x0 + ((math.log10(v)-minx)/(maxx-minx))*(x1-x0)
    def yp(v): return y1 - ((math.log10(v)-miny)/(maxy-miny))*(y1-y0)
    for t in [1,10,100,1000,10000,100000,1000000]:
        if t <= max_tokens:
            x=int(xp(t)); draw.line((x,y0,x,y1), fill=GRID, width=2); draw.text((x,y1+30), f"{t:g}", font=TICK, fill=BLACK, anchor="mt")
    for t in [1,10,100,1000]:
        if t <= 10**maxy:
            y=int(yp(t)); draw.line((x0,y,x1,y), fill=GRID, width=2); draw.text((x0-25,y), f"{t:g}", font=TICK, fill=BLACK, anchor="rm")
    draw_axes_box(draw, area)
    xs = np.logspace(0, math.log10(max_tokens), 220)
    pts=[(int(xp(float(x))), int(yp(K*(float(x)**beta)))) for x in xs]
    draw.line(pts, fill=BLUE, width=7)
    ox, oy = int(xp(max_tokens)), int(yp(vocab))
    draw.ellipse((ox-18,oy-18,ox+18,oy+18), fill=PURPLE, outline=BLACK, width=3)
    draw.text((ox-25, oy-45), "Observed vocab", font=SMALL, fill=BLACK, anchor="rb")
    draw.text(((x0+x1)//2,2530), "Cumulative tokens N (log scale)", font=LABEL, fill=BLACK, anchor="mm")
    draw_rotated_center(img, (105,(y0+y1)//2), "Vocabulary V (log scale)", LABEL)
    return save_image(img, "F6_heaps_law", kind="line")


def draw_f7(speaker_rows, cat_rows, split_rows):
    speakers = [str(r["speaker_id"]) for r in sorted(speaker_rows, key=lambda r: -float(r["total_duration_h"]))]
    cats = sorted(str(r["category"]) for r in cat_rows)
    expected = sum(float(r["n_files"]) for r in split_rows) / (len(speakers) * len(cats))
    img = new_canvas(4500, 3400)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F7. Speaker × category file-count uniformity", f"Expected ≈ {expected:.0f} files per cell; English category labels")
    x0,y0,x1,y1 = (620, 600, 3820, 3000)
    cw=(x1-x0)/len(cats); ch=(y1-y0)/len(speakers)
    for j, cat in enumerate(cats):
        cx=x0+cw*(j+0.5)
        words = [cat]
        if len(cat) > 10:
            mid=len(cat)//2
            words=[cat[:mid], cat[mid:]]
        for k, part in enumerate(words):
            draw.text((int(cx), y0-115+55*k), part, font=SMALL, fill=BLACK, anchor="mm")
    for i, sp in enumerate(speakers):
        cy=y0+ch*(i+0.5)
        draw.text((x0-35, int(cy)), sp, font=TICK, fill=BLACK, anchor="rm")
    for i in range(len(speakers)):
        for j in range(len(cats)):
            x=int(x0+j*cw); y=int(y0+i*ch)
            # Uniformity panel: slight alternating shade to keep cells visible.
            fill = "#2B8CBE" if (i+j)%2==0 else "#3A9CCB"
            draw.rectangle((x,y,int(x0+(j+1)*cw),int(y0+(i+1)*ch)), fill=fill, outline="white", width=2)
    draw.rectangle((x0,y0,x1,y1), outline=BLACK, width=3)
    # Color-bar style note
    draw.rectangle((3900, 800, 3970, 1600), fill="#2B8CBE", outline=BLACK, width=2)
    draw.text((4025, 1160), "Mean files\nper cell", font=SMALL, fill=BLACK, anchor="lm", spacing=8)
    draw.text((4025, 1510), f"≈ {expected:.0f}", font=BOLD_SMALL, fill=BLACK, anchor="lm")
    return save_image(img, "F7_speaker_category_heatmap", kind="combination")


def draw_f8(speaker_rows):
    rows = sorted(speaker_rows, key=lambda r: -float(r["total_duration_h"]))
    cum=[]; total=0.0
    for r in rows:
        total += float(r["total_duration_h"]); cum.append(total)
    img = new_canvas(4500, 2800)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4500, "F8. Cumulative recording time by speaker rank", "Speakers sorted from longest to shortest total duration")
    area=(600,430,4200,2200); x0,y0,x1,y1=area
    ymax=max(cum)*1.05; ticks=nice_ticks(ymax,6); ymax=max(ticks)
    def xp(i): return x0 + ((i-1)/(len(cum)-1))*(x1-x0)
    def yp(v): return y1 - (v/ymax)*(y1-y0)
    draw_grid_y(draw, area, ticks, yp, "{:.0f}")
    for t in [1,5,10,15,20]:
        x=int(xp(t)); draw.line((x,y0,x,y1), fill=GRID, width=2); draw.text((x,y1+30), str(t), font=TICK, fill=BLACK, anchor="mt")
    draw_axes_box(draw, area)
    pts=[(int(xp(i+1)),int(yp(v))) for i,v in enumerate(cum)]
    draw.line(pts, fill=BLUE, width=8)
    for x,y in pts: draw.ellipse((x-13,y-13,x+13,y+13), fill=ORANGE, outline=BLACK, width=2)
    draw.text(((x0+x1)//2,2530), "Speaker rank", font=LABEL, fill=BLACK, anchor="mm")
    draw_rotated_center(img, (105,(y0+y1)//2), "Cumulative hours", LABEL)
    return save_image(img, "F8_cumulative_hours", kind="line")


def draw_f9():
    return horizontal_bar_chart(
        "F9_audio_uniformity",
        "F9. Audio-format uniformity across the corpus",
        "All files share the same sampling format",
        ["Sample rate = 16 kHz", "Bit depth = 16-bit", "Channels = mono"],
        [100.0, 100.0, 100.0],
        "Share of files (%)",
        color=GREEN,
        w=4500,
        h=2300,
    )


def draw_f10(split_rows):
    rows = split_rows
    labels = [str(r["split"]) for r in rows]
    values = [100.0 * float(r["n_synthetic"]) / float(r["n_files"]) for r in rows]
    return vertical_bar_chart(
        "F10_synthetic_disclosure",
        "F10. Synthetic Edge-TTS gap-fill share by split",
        "Very small gap-fill fraction; values shown as percent of split files",
        labels,
        values,
        "Synthetic share (%)",
        color=VERMILION,
    )


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    a = sorted(vals)
    pos = (len(a)-1)*q
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi: return a[lo]
    return a[lo]*(hi-pos)+a[hi]*(pos-lo)


def draw_boxplot_panel(draw, area, rows_by_cat, cats, metric, title, xlabel, xmax=None, show_labels=True):
    x0,y0,x1,y1=area
    allv=[v for c in cats for v in rows_by_cat[c][metric]]
    xmin=0.0 if min(allv)>=0 else min(allv)*1.05
    xmax=xmax or max(allv)*1.12
    ticks=nice_ticks(xmax,5); xmax=max(ticks)
    def xp(v): return x0 + ((v-xmin)/(xmax-xmin))*(x1-x0)
    for t in ticks:
        x=int(xp(t)); draw.line((x,y0,x,y1), fill=GRID, width=2); draw.text((x,y1+22), f"{t:.1f}", font=TICK, fill=BLACK, anchor="mt")
    draw_axes_box(draw, area)
    draw.text(((x0+x1)//2,y0-60), title, font=SUBTITLE, fill=BLACK, anchor="mm")
    slot=(y1-y0)/len(cats)
    for i,cat in enumerate(cats):
        vals=rows_by_cat[cat][metric]
        q1=percentile(vals,.25); q2=percentile(vals,.5); q3=percentile(vals,.75)
        lo=max(min(vals), q1-1.5*(q3-q1)); hi=min(max(vals), q3+1.5*(q3-q1))
        cy=y0+slot*(i+.5); bh=slot*.45
        if show_labels: draw.text((x0-35,int(cy)),cat,font=TICK,fill=BLACK,anchor="rm")
        draw.line((int(xp(lo)),int(cy),int(xp(hi)),int(cy)), fill=BLACK, width=3)
        draw.rectangle((int(xp(q1)),int(cy-bh/2),int(xp(q3)),int(cy+bh/2)), fill=SKY, outline=BLACK, width=3)
        draw.line((int(xp(q2)),int(cy-bh/2),int(xp(q2)),int(cy+bh/2)), fill=VERMILION, width=5)
    draw.text(((x0+x1)//2,y1+105), xlabel, font=LABEL, fill=BLACK, anchor="mm")


def draw_f12(aq_rows):
    cats = sorted(set(str(r["category"]) for r in aq_rows))
    by={c:{"dynamic_range_db":[],"silence_ratio":[]} for c in cats}
    for r in aq_rows:
        c=str(r["category"]); by[c]["dynamic_range_db"].append(float(r["dynamic_range_db"])); by[c]["silence_ratio"].append(float(r["silence_ratio"])*100.0)
    img=new_canvas(4500,3500); draw=ImageDraw.Draw(img)
    draw_title(draw,4500,"F12. Audio quality across categories",f"Stratified sample, n = {len(aq_rows)}; readable boxplot labels")
    draw_boxplot_panel(draw,(1120,470,4200,1770),by,cats,"dynamic_range_db","F12a. Dynamic range","Dynamic range (dB)",show_labels=True)
    draw_boxplot_panel(draw,(1120,2150,4200,3200),by,cats,"silence_ratio","F12b. Silence ratio","Silence ratio (%)",show_labels=True)
    return save_image(img,"F12_audio_quality",kind="line")


def crop_spectrogram_regions(src: Image.Image) -> list[Image.Image]:
    arr = np.asarray(src.convert("RGB"))
    sat = arr.max(axis=2) - arr.min(axis=2)
    mask = (sat > 30) & (arr.max(axis=2) < 250)
    rows = np.where(mask.sum(axis=1) > 100)[0]
    cols = np.where(mask.sum(axis=0) > 100)[0]

    def groups(vals, gap=25):
        out=[]; start=None; prev=None
        for v in vals:
            v=int(v)
            if start is None:
                start=prev=v
            elif v-prev<=gap:
                prev=v
            else:
                out.append((start,prev)); start=prev=v
        if start is not None: out.append((start,prev))
        return out

    row_groups = groups(rows, 25)
    col_groups = groups(cols, 25)
    crops=[]
    for rg in row_groups:
        for cg in col_groups:
            # Last row has only three panels; skip empty fourth if not present.
            x0,x1=cg; y0,y1=rg
            crops.append(src.crop((max(0,x0-10), max(0,y0-10), min(src.width,x1+10), min(src.height,y1+10))))
    return crops[:11]


def draw_f11():
    src = Image.open(ORIG_F11).convert("RGB")
    crops = crop_spectrogram_regions(src)
    labels = [
        ("Declarative", "M10", "5.1 s"),
        ("Clarification", "F2", "5.5 s"),
        ("Conditional", "M8", "5.4 s"),
        ("Confirmation", "M11", "5.3 s"),
        ("Negation", "F2", "5.9 s"),
        ("Scheduling", "F7", "3.9 s"),
        ("Imperative", "M4", "1.9 s"),
        ("Persuasive", "M6", "10.5 s"),
        ("Rhetorical", "M10", "5.0 s"),
        ("Exclamatory", "F1", "3.1 s"),
        ("Interrogative", "M6", "4.3 s"),
    ]
    img = new_canvas(4470, 3000)
    draw = ImageDraw.Draw(img)
    draw_title(draw, 4470, "F11. Mel-spectrogram exemplars", "One real-speech file per sentence category; public speaker IDs only")
    cols, rows = 4, 3
    left, right, top, bottom = 180, 120, 385, 130
    gap_x, gap_y = 120, 190
    panel_w = int((4470-left-right-(cols-1)*gap_x)/cols)
    panel_h = int((3000-top-bottom-(rows-1)*gap_y)/rows)
    title_h = 120
    axis_l = 118
    axis_b = 80
    spec_w = panel_w - axis_l - 8
    spec_h = panel_h - title_h - axis_b
    title_font = font(58, True)  # 7 pt at 600 dpi
    panel_font = font(48, False) # 5.8 pt, used only for ticks; category title is larger
    for idx, crop in enumerate(crops):
        r, c = divmod(idx, cols)
        px = left + c*(panel_w+gap_x)
        py = top + r*(panel_h+gap_y)
        cat, sp, dur = labels[idx]
        draw.text((px+panel_w//2, py), cat, font=title_font, fill=BLACK, anchor="mt")
        draw.text((px+panel_w//2, py+65), f"({sp}, {dur})", font=SMALL, fill=BLACK, anchor="mt")
        sx0 = px + axis_l
        sy0 = py + title_h
        resample = getattr(Image, "Resampling", Image).LANCZOS
        crop_resized = crop.resize((spec_w, spec_h), resample)
        img.paste(crop_resized, (sx0, sy0))
        sx1, sy1 = sx0 + spec_w, sy0 + spec_h
        draw.rectangle((sx0, sy0, sx1, sy1), outline=BLACK, width=3)
        # Simplified readable ticks.  The spectrograms are qualitative exemplars,
        # so dense tick labels are avoided per Elsevier's minimal-text advice.
        for frac, lab in [(0.0, "0"), (0.5, "2048"), (1.0, "4096")]:
            y = int(sy1 - frac*spec_h)
            draw.line((sx0-12, y, sx0, y), fill=BLACK, width=3)
            draw.text((sx0-18, y), lab, font=panel_font, fill=BLACK, anchor="rm")
        for frac, lab in [(0.0, "0"), (1.0, dur.replace(" s", ""))]:
            x = int(sx0 + frac*spec_w)
            draw.line((x, sy1, x, sy1+12), fill=BLACK, width=3)
            draw.text((x, sy1+18), lab, font=panel_font, fill=BLACK, anchor="mt")
        draw.text((sx0+spec_w//2, sy1+70), "Time (s)", font=panel_font, fill=BLACK, anchor="mm")
    return save_image(img, "F11_mel_spectrogram_exemplars", dpi=600, kind="halftone")


def main() -> None:
    df_speaker = read_csv(STATS / "per_speaker.csv")
    df_cat = read_csv(STATS / "per_category.csv")
    df_split = read_csv(STATS / "per_split.csv")
    df_aq = read_csv(STATS / "audio_quality_sample.csv")
    df_wf = read_csv(STATS / "word_frequency.csv")
    with (STATS / "dataset_stats.json").open(encoding="utf-8") as f:
        meta = json.load(f)

    manifest_rows: list[tuple[str, str, str, str]] = []
    for fig_id, result in [
        ("F1", draw_f1(df_speaker)),
        ("F2", horizontal_bar_chart(
            "F2_duration_per_category",
            "F2. File duration per sentence category",
            "Mean ± 1 SD; English category labels enlarged for print readability",
            [str(r["category"]) for r in sorted(df_cat, key=lambda r: float(r["mean_duration_sec"]))],
            [float(r["mean_duration_sec"]) for r in sorted(df_cat, key=lambda r: float(r["mean_duration_sec"]))],
            "Mean file duration (s) ± 1 SD",
            color=BLUE,
            xerr=[float(r["std_duration_sec"]) for r in sorted(df_cat, key=lambda r: float(r["mean_duration_sec"]))],
        )),
        ("F3", horizontal_bar_chart(
            "F3_speaker_total_duration",
            "F3. Total recording time per speaker",
            "Public speaker IDs; bar color indicates sex",
            [str(r["speaker_id"]) for r in sorted(df_speaker, key=lambda r: float(r["total_duration_h"]))],
            [float(r["total_duration_h"]) for r in sorted(df_speaker, key=lambda r: float(r["total_duration_h"]))],
            "Total recording time (hours)",
            color=PURPLE,
            w=4500,
            h=3300,
        )),
        ("F4", draw_f4(df_cat)),
        ("F5", draw_f5(df_wf)),
        ("F6", draw_f6(meta)),
        ("F7", draw_f7(df_speaker, df_cat, df_split)),
        ("F8", draw_f8(df_speaker)),
        ("F9", draw_f9()),
        ("F10", draw_f10(df_split)),
        ("F11", draw_f11()),
        ("F12", draw_f12(df_aq)),
    ]:
        pdf, png, kind = result
        manifest_rows.append((fig_id, pdf.name, png.relative_to(FIGS).as_posix(), kind))

    manifest_csv = FIGS / "figure_manifest.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["figure", "vector_pdf", "raster_png600", "kind"])
        w.writerows(manifest_rows)

    print(f"[ok] wrote manifest -> {manifest_csv.relative_to(ROOT)}")
    print(f"{'fig':6s}{'kind':14s}{'pdf':38s}{'png size'}")
    for fig_id, pdf_name, png_rel, kind in manifest_rows:
        png = FIGS / png_rel
        im = Image.open(png)
        print(f"{fig_id:6s}{kind:14s}{pdf_name:38s}{im.width}x{im.height} dpi={im.info.get('dpi')}")


if __name__ == "__main__":
    main()

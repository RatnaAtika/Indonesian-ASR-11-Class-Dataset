#!/usr/bin/env python3
"""Generate deterministic, public-safe NSS-ID main-text working figures.

The script uses Pillow and parallel SVG primitives rather than Matplotlib so the
artwork remains reproducible in the current environment. Every figure is marked
NOT FOR SUBMISSION; final artwork must be regenerated after all release gates.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from split_schema import canonical_split
DEFAULT_OUTPUT = ROOT / "Draft_Paper" / "04_Revised_Draft" / "figures"
CATEGORY_PATH = ROOT / "Report_paper_9model" / "hf_dataset_information_public" / "per_category_public.csv"
SPLIT_PATH = ROOT / "Report_paper_9model" / "hf_dataset_information_public" / "per_split_public.csv"
SPEAKER_PATH = ROOT / "Report_paper_9model" / "hf_dataset_information_public" / "per_speaker_public.csv"
EVIDENCE_PATH = ROOT / "Draft_Paper" / "02_Evidence" / "evidence_registry.json"
FONT_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

WHITE = "#FFFFFF"
INK = "#172B4D"
MUTED = "#52667A"
GRID = "#D9E2EC"
NAVY = "#28527A"
BLUE = "#3D7EA6"
TEAL = "#2A9D8F"
LIGHT_TEAL = "#DDF3EE"
ORANGE = "#F4A261"
LIGHT_ORANGE = "#FFF0DD"
RED = "#C94C4C"
LIGHT_RED = "#FBE3E3"
LIGHT_BLUE = "#E7F0F8"
GRAY_BG = "#F5F7FA"

CATEGORY_ENGLISH = {
    "Kalimat_Deklaratif": "Declarative",
    "Kalimat_Klarifikasi": "Clarification",
    "Kalimat_Kondisional": "Conditional",
    "Kalimat_Konfirmasi": "Confirmation",
    "Kalimat_Negasi": "Negation",
    "Kalimat_Penjadwalan": "Scheduling",
    "Kalimat_Perintah": "Imperative",
    "Kalimat_Persuasif": "Persuasive",
    "Kalimat_Retoris": "Rhetorical",
    "Kalimat_Seruan": "Exclamatory",
    "Kalimat_Tanya": "Interrogative",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row.get("split"):
            row["split"] = canonical_split(row["split"])
    return rows


class DualCanvas:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), WHITE)
        self.draw = ImageDraw.Draw(self.image)
        self.svg: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>',
        ]
        self._font_cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

    def font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = (size, bold)
        if key not in self._font_cache:
            path = FONT_BOLD if bold else FONT_REGULAR
            self._font_cache[key] = ImageFont.truetype(str(path), size=size)
        return self._font_cache[key]

    def rect(
        self,
        box: tuple[float, float, float, float],
        fill: str,
        outline: str = INK,
        width: int = 4,
        radius: int = 22,
    ) -> None:
        x0, y0, x1, y1 = box
        self.draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
        self.svg.append(
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" '
            f'rx="{radius}" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
        )

    def line(self, points: list[tuple[float, float]], fill: str = INK, width: int = 5) -> None:
        self.draw.line(points, fill=fill, width=width, joint="curve")
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{fill}" stroke-width="{width}"/>')

    def polygon(self, points: list[tuple[float, float]], fill: str) -> None:
        self.draw.polygon(points, fill=fill)
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self.svg.append(f'<polygon points="{coords}" fill="{fill}"/>')

    def circle(self, center: tuple[float, float], radius: float, fill: str, outline: str = INK, width: int = 3) -> None:
        x, y = center
        box = (x - radius, y - radius, x + radius, y + radius)
        self.draw.ellipse(box, fill=fill, outline=outline, width=width)
        self.svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
        )

    def arrow(self, start: tuple[float, float], end: tuple[float, float], fill: str = INK, width: int = 7) -> None:
        self.line([start, end], fill=fill, width=width)
        x0, y0 = start
        x1, y1 = end
        angle = math.atan2(y1 - y0, x1 - x0)
        size = 24
        left = (x1 - size * math.cos(angle - math.pi / 6), y1 - size * math.sin(angle - math.pi / 6))
        right = (x1 - size * math.cos(angle + math.pi / 6), y1 - size * math.sin(angle + math.pi / 6))
        self.polygon([end, left, right], fill=fill)

    def text(
        self,
        position: tuple[float, float],
        value: str,
        size: int,
        fill: str = INK,
        bold: bool = False,
        anchor: str = "lt",
        align: str = "left",
        spacing: int | None = None,
    ) -> None:
        x, y = position
        font = self.font(size, bold)
        spacing = spacing if spacing is not None else max(6, int(size * 0.24))
        pil_anchor = "la" if anchor == "lt" else anchor
        self.draw.multiline_text(
            (x, y),
            value,
            font=font,
            fill=fill,
            anchor=pil_anchor,
            align=align,
            spacing=spacing,
        )
        lines = value.splitlines() or [""]
        line_height = size * 1.25
        total_height = line_height * len(lines)
        if anchor in {"mm", "lm", "rm"}:
            start_y = y - total_height / 2 + size * 0.15
            dominant = "hanging"
        elif anchor.endswith("b"):
            start_y = y - total_height
            dominant = "hanging"
        else:
            start_y = y
            dominant = "hanging"
        if anchor.startswith("m"):
            text_anchor = "middle"
        elif anchor.startswith("r"):
            text_anchor = "end"
        else:
            text_anchor = "start"
        weight = "700" if bold else "400"
        self.svg.append(
            f'<text x="{x:.1f}" y="{start_y:.1f}" fill="{fill}" font-family="DejaVu Sans, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{text_anchor}" dominant-baseline="{dominant}">'
        )
        for index, line in enumerate(lines):
            dy = 0 if index == 0 else line_height
            escaped = html.escape(line)
            self.svg.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{escaped}</tspan>')
        self.svg.append("</text>")

    def panel_title(self, box: tuple[int, int, int, int], title: str) -> None:
        x0, y0, x1, _ = box
        self.text(((x0 + x1) / 2, y0 + 55), title, 44, bold=True, anchor="mm", align="center")

    def save(self, png_path: Path, svg_path: Path) -> None:
        self.image.save(png_path, format="PNG", dpi=(600, 600), optimize=True)
        self.svg.append("</svg>")
        svg_path.write_text("\n".join(self.svg) + "\n", encoding="utf-8")


def add_title(canvas: DualCanvas, title: str, subtitle: str) -> None:
    canvas.text((canvas.width / 2, 95), title, 72, bold=True, anchor="mm", align="center")
    canvas.text((canvas.width / 2, 185), subtitle, 38, fill=MUTED, anchor="mm", align="center")


def add_footer(canvas: DualCanvas, source: str) -> None:
    canvas.line([(120, canvas.height - 105), (canvas.width - 120, canvas.height - 105)], fill=GRID, width=3)
    canvas.text((120, canvas.height - 70), source, 26, fill=MUTED, anchor="lm")
    canvas.text((canvas.width - 120, canvas.height - 70), "INTERNAL WORKING ARTWORK — NOT FOR SUBMISSION", 27, fill=RED, bold=True, anchor="rm")


def node(canvas: DualCanvas, box: tuple[int, int, int, int], value: str, fill: str, outline: str = NAVY, size: int = 40) -> None:
    canvas.rect(box, fill=fill, outline=outline, width=5, radius=26)
    x0, y0, x1, y1 = box
    canvas.text(((x0 + x1) / 2, (y0 + y1) / 2), value, size, bold=True, anchor="mm", align="center")


def build_figure_1(output: Path) -> None:
    canvas = DualCanvas(4200, 3000)
    add_title(canvas, "NSS-ID construction and package flow", "Scope-qualified working schematic; ethical release and final package freeze remain gated")

    node(canvas, (550, 280, 2650, 480), "Recruitment and consent evidence\nMATERIAL GATE — unresolved", LIGHT_RED, RED, 37)
    canvas.arrow((1600, 480), (1600, 585), fill=MUTED)
    node(canvas, (550, 585, 2650, 790), "11-category prompt inventory\nstable original sentence IDs", LIGHT_BLUE, NAVY, 39)
    canvas.arrow((1200, 790), (865, 900), fill=MUTED)
    canvas.arrow((2000, 790), (2335, 900), fill=MUTED)

    node(canvas, (250, 900, 1480, 1150), "Prompted read-speech source tree\n20 retained human labels\nacquisition details partly gated", LIGHT_TEAL, TEAL, 33)
    node(canvas, (1720, 900, 2950, 1150), "Synthetic gap filling\n132 labelled repairs\n2 mismatch rows unresolved", LIGHT_ORANGE, ORANGE, 34)
    canvas.arrow((865, 1150), (1300, 1280), fill=MUTED)
    canvas.arrow((2335, 1150), (1900, 1280), fill=MUTED)

    node(canvas, (550, 1280, 2650, 1485), "Segmentation • transcript assignment • structural QC\npublication-grade protocol attachments incomplete", GRAY_BG, NAVY, 33)
    canvas.arrow((1600, 1485), (1600, 1585), fill=MUTED)
    node(canvas, (550, 1585, 2650, 1805), "Pre-transcript-repair metadata state\n104,500 rows • 1,956 blank transcript fields", LIGHT_BLUE, NAVY, 37)

    canvas.arrow((1200, 1805), (1200, 1950), fill=TEAL)
    canvas.text((1200, 1870), "transcript repair → release target", 25, fill=TEAL, bold=True, anchor="mm", align="center")
    node(canvas, (350, 1950, 2150, 2165), "Current release target\n104,500 files • 134.1762 h\n104,368 human recordings • 132 synthetic", LIGHT_TEAL, TEAL, 34)

    canvas.arrow((2350, 1805), (3100, 1980), fill=ORANGE)
    canvas.text((3200, 1850), "blank-row exclusion → frozen benchmark", 24, fill=ORANGE, bold=True, anchor="mm", align="center")
    node(canvas, (3000, 1950, 4070, 2245), "Frozen benchmark\n102,544 files • 130.6548 h\n15,376 test items\n15,374 human + 2 synthetic\nseen scripts", LIGHT_ORANGE, ORANGE, 29)
    canvas.text((3535, 2310), "Audio shards were unchanged\nby the metadata transcript repair", 27, fill=MUTED, anchor="mm", align="center")

    canvas.arrow((1250, 2165), (1250, 2270), fill=MUTED)
    node(canvas, (350, 2270, 2150, 2445), "Manifests • schema • source values • checksums\nfinal freeze and checksum package pending", LIGHT_BLUE, NAVY, 31)
    canvas.arrow((1250, 2445), (1250, 2545), fill=MUTED)
    node(canvas, (350, 2545, 2150, 2775), "Private staging — release not authorized\nHugging Face repository remains private\nlicence: other • no persistent DOI", LIGHT_RED, RED, 31)

    add_footer(canvas, "Source: evidence_registry.json and pinned private-staging inventory")
    canvas.save(
        output / "Figure_1_construction_package_flow.png",
        output / "Figure_1_construction_package_flow.svg",
    )


def build_figure_2(output: Path, categories: list[dict[str, str]]) -> None:
    rows = [
        {
            "category": CATEGORY_ENGLISH[row["category"]],
            "hours": float(row["duration_hours"]),
            "mean": float(row["mean_duration_sec"]),
            "files": int(row["file_count"]),
        }
        for row in categories
    ]
    rows.sort(key=lambda row: row["hours"], reverse=True)
    canvas = DualCanvas(4200, 3000)
    add_title(canvas, "Release-target duration by category", "104,500 files • 134.1762 h • 11 categories • 9,500 files per category")

    chart_left, chart_right = 1420, 3650
    chart_top, chart_bottom = 410, 2670
    max_hours = 18.0
    for tick in (0, 5, 10, 15):
        x = chart_left + (tick / max_hours) * (chart_right - chart_left)
        canvas.line([(x, chart_top - 20), (x, chart_bottom)], fill=GRID, width=3)
        canvas.text((x, chart_top - 55), f"{tick} h", 30, fill=MUTED, anchor="mm")
    canvas.text((3880, 315), "Mean duration", 31, fill=MUTED, bold=True, anchor="mm")

    row_step = 195
    bar_height = 92
    for index, row in enumerate(rows):
        y = chart_top + index * row_step
        canvas.text((1300, y + bar_height / 2), row["category"], 39, bold=True, anchor="rm")
        bar_end = chart_left + (row["hours"] / max_hours) * (chart_right - chart_left)
        color = TEAL if index % 2 == 0 else BLUE
        canvas.rect((chart_left, y, bar_end, y + bar_height), fill=color, outline=color, width=1, radius=14)
        canvas.text((bar_end + 24, y + bar_height / 2), f"{row['hours']:.4f} h", 34, bold=True, anchor="lm")
        canvas.text((3880, y + bar_height / 2), f"{row['mean']:.4f} s", 34, fill=ORANGE, bold=True, anchor="mm")

    canvas.text((chart_left, 2745), "Total duration (hours); categories sorted descriptively by hours", 31, fill=MUTED, anchor="lt")
    add_footer(canvas, "Source values: per_category_public.csv (release target only)")
    canvas.save(
        output / "Figure_2_release_target_duration_by_category.png",
        output / "Figure_2_release_target_duration_by_category.svg",
    )


def panel_bar(
    canvas: DualCanvas,
    box: tuple[int, int, int, int],
    labels: list[str],
    values: list[float],
    value_labels: list[str],
    max_value: float,
    colors: list[str],
) -> None:
    x0, y0, x1, y1 = box
    left = x0 + 300
    right = x1 - 95
    top = y0 + 145
    step = (y1 - top - 65) / len(labels)
    for index, (label, value, display, color) in enumerate(zip(labels, values, value_labels, colors)):
        y = top + index * step
        canvas.text((left - 35, y + 34), label, 33, bold=True, anchor="rm")
        end = left + (value / max_value) * (right - left)
        canvas.rect((left, y, max(left + 3, end), y + 68), fill=color, outline=color, width=1, radius=12)
        canvas.text((min(end + 18, right - 5), y + 34), display, 29, fill=INK, bold=True, anchor="lm")


def build_figure_3(output: Path, splits: list[dict[str, str]], speakers: list[dict[str, str]]) -> None:
    canvas = DualCanvas(4200, 3000)
    add_title(canvas, "Release-target split and acoustic-source composition", "Human public IDs are split-disjoint; scripts and provider TTS voices are not guaranteed disjoint")

    panels = {
        "files": (120, 330, 2050, 1370),
        "hours": (2150, 330, 4080, 1370),
        "speakers": (120, 1470, 2050, 2570),
        "sources": (2150, 1470, 4080, 2570),
    }
    for box in panels.values():
        canvas.rect(box, fill=WHITE, outline=GRID, width=4, radius=22)
    canvas.panel_title(panels["files"], "A. Files and synthetic repairs")
    canvas.panel_title(panels["hours"], "B. Duration")
    canvas.panel_title(panels["speakers"], "C. Human public speaker labels")
    canvas.panel_title(panels["sources"], "D. Acoustic-source file labels")

    display_split = {"train": "Train", "val": "Validation", "test": "Test"}
    labels = [display_split[row["split"]] for row in splits]
    colors = [TEAL, BLUE, ORANGE]
    panel_bar(
        canvas,
        panels["files"],
        labels,
        [float(row["file_count"]) for row in splits],
        [f"{int(row['file_count']):,}  (synthetic {int(row['synthetic_files']):,})" for row in splits],
        80000,
        colors,
    )
    panel_bar(
        canvas,
        panels["hours"],
        labels,
        [float(row["duration_hours"]) for row in splits],
        [f"{float(row['duration_hours']):.4f} h" for row in splits],
        100,
        colors,
    )

    human = [row for row in speakers if row["speaker_type"].lower() == "human"]
    counts: dict[str, dict[str, int]] = {split: {"Male": 0, "Female": 0} for split in ("train", "val", "test")}
    for row in human:
        counts[row["split"]][row["speaker_gender"]] += 1
    panel_bar(
        canvas,
        panels["speakers"],
        labels,
        [sum(counts[split].values()) for split in ("train", "val", "test")],
        [f"{sum(counts[split].values())}  ({counts[split]['Male']} M / {counts[split]['Female']} F)" for split in ("train", "val", "test")],
        16,
        colors,
    )

    x0, y0, x1, y1 = panels["sources"]
    left, right, top = x0 + 300, x1 - 90, y0 + 150
    step = 260
    max_files = max(int(row["file_count"]) for row in splits)
    for index, row in enumerate(splits):
        y = top + index * step
        male = int(row["male_source_files"])
        female = int(row["female_source_files"])
        total = int(row["file_count"])
        canvas.text((left - 35, y + 38), display_split[row["split"]], 33, bold=True, anchor="rm")
        total_width = (total / max_files) * (right - left)
        male_width = (male / total) * total_width if total else 0
        female_width = total_width - male_width
        if male > 0:
            canvas.rect((left, y, left + male_width, y + 76), fill=NAVY, outline=NAVY, width=1, radius=10)
        if female > 0 and female_width >= 3:
            canvas.rect((left + male_width, y, left + total_width, y + 76), fill=ORANGE, outline=ORANGE, width=1, radius=10)
        elif female > 0:
            canvas.circle((left + total_width, y + 38), 10, fill=ORANGE, outline=ORANGE, width=1)
        canvas.text((left, y + 115), f"Male source {male:,} | Female source {female:,}", 28, fill=MUTED, anchor="lt")
    canvas.text((left, y1 - 105), "Development: 0 female-source files. Test: 2 female-source files, both synthetic and targeting M8.", 25, fill=RED, bold=True, anchor="lt")
    canvas.text((left, y1 - 58), "No natural female human speaker occurs in development or test; no gender-generalization inference.", 25, fill=MUTED, anchor="lt")

    add_footer(canvas, "Source values: per_split_public.csv and per_speaker_public.csv (release target only)")
    canvas.save(
        output / "Figure_3_release_target_split_source_composition.png",
        output / "Figure_3_release_target_split_source_composition.svg",
    )


def build_manifest(output: Path) -> None:
    source_paths = [CATEGORY_PATH, SPLIT_PATH, SPEAKER_PATH, EVIDENCE_PATH]
    outputs = sorted(list(output.glob("*.png")) + list(output.glob("*.svg")), key=lambda path: path.name)
    payload = {
        "status": "internal_not_for_submission",
        "figure_1_scope": "construction_and_scope_bridge",
        "figure_2_scope": "release_target",
        "figure_3_scope": "release_target",
        "figure_4_status": "blocked_pending_sampling_provenance",
        "script": "Draft_Paper/99_Admin/build_release_target_figures.py",
        "script_sha256": sha256_file(Path(__file__)),
        "sources": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(path),
            }
            for path in source_paths
        ],
        "outputs": [
            {
                "path": path.name,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in outputs
        ],
    }
    (output / "figure_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_all(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for stale in output.iterdir():
        if stale.is_file() and stale.name.startswith(("Figure_1_", "Figure_2_", "Figure_3_", "figure_manifest")):
            stale.unlink()
    categories = load_csv(CATEGORY_PATH)
    splits = load_csv(SPLIT_PATH)
    speakers = load_csv(SPEAKER_PATH)
    build_figure_1(output)
    build_figure_2(output, categories)
    build_figure_3(output, splits, speakers)
    build_manifest(output)
    print(f"Wrote 3 PNG/SVG figure pairs and manifest to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_all(args.output_dir.resolve())


if __name__ == "__main__":
    main()

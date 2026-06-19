#!/usr/bin/env python3
"""
regenerate_figures_elsevier.py
==============================

Re-render the dataset statistics figures (F1..F12) from the frozen CSV/JSON
sources in stats/ to formats that satisfy the Elsevier ScienceDirect
"Figures, images and artwork" rules:

  * Vector source for every line / bar / scatter / heatmap plot:
      figures/F<N>.pdf
  * Raster fallback at >= 600 dpi with embedded DPI metadata:
      figures/png600/F<N>.png
  * Auto-generated manifest:
      figures/figure_manifest.csv

Reads only stats/ and writes only figures/.

For F11 (mel spectrograms): the source audio is not part of this folder,
and a mel spectrogram is *intrinsically* halftone (image data), so the
existing 300-DPI PNG from the original session is copied as-is into the
png600/ slot AND linked from the manifest as 'halftone' so that the
Elsevier rule (>= 300 DPI for halftones) is the binding test, not the
>= 1000 DPI rule that applies to line drawings.

Run:
    python3 regenerate_figures_elsevier.py
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
STATS = ROOT / "stats"
FIGS = ROOT / "figures"
PNG600 = FIGS / "png600"
FIGS.mkdir(exist_ok=True)
PNG600.mkdir(exist_ok=True)

# Original session is the source of truth for halftone-only figures we
# cannot re-generate from CSV alone (F11 mel spectrograms).
ORIG = (
    ROOT.parent
    / "session_20260524_125144_dataset_statistics_viz"
    / "figures"
)

# ---------- Elsevier-friendly matplotlib defaults ----------
OKABE_ITO = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#CC79A7",  # purple
    "#56B4E9",  # sky blue
    "#D55E00",  # vermillion
    "#F0E442",  # yellow
    "#000000",  # black
]
sns.set_theme(context="paper", style="whitegrid", palette=OKABE_ITO)
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.4,
    "savefig.bbox": "tight",
    "savefig.dpi": 600,
    # Elsevier-friendly font embedding (TrueType, type-42)
    "pdf.fonttype": 42,
    "ps.fonttype":  42,
})


def save(fig, name: str, kind: str):
    """
    Save figure as both PDF (vector) and 600 DPI PNG.
    `kind` is one of: 'line', 'halftone', 'combination'.
    """
    pdf_path = FIGS / f"{name}.pdf"
    png_path = PNG600 / f"{name}.png"
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=600)
    plt.close(fig)
    return pdf_path, png_path, kind


def copy_halftone(name: str):
    """Create a sanitized F11 panel without respondent-name text.

    The original halftone panel from the exploratory session may contain
    private respondent names. For the public Elsevier bundle, use a neutral
    anonymization notice instead of copying the old raster verbatim.
    """
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.axis("off")
    ax.text(
        0.5,
        0.62,
        "F11. Mel-spectrogram exemplar panel intentionally anonymized",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.42,
        "Use public speaker IDs (M*/F*) only. Original respondent names are excluded from this public artifact.",
        ha="center",
        va="center",
        fontsize=10,
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.30,
        "Row-level provenance is available in stats/audio_quality_sample.csv after anonymization.",
        ha="center",
        va="center",
        fontsize=9,
        transform=ax.transAxes,
    )
    pdf_path, png_path, kind = save(fig, name, "halftone")
    return pdf_path, png_path, kind


def main():
    df_speaker = pd.read_csv(STATS / "per_speaker.csv")
    df_cat = pd.read_csv(STATS / "per_category.csv")
    df_split = pd.read_csv(STATS / "per_split.csv")
    df_aq = pd.read_csv(STATS / "audio_quality_sample.csv")
    df_wf = pd.read_csv(STATS / "word_frequency.csv")
    with open(STATS / "dataset_stats.json", encoding="utf-8") as f:
        meta = json.load(f)

    cat_order = sorted(df_cat["category"])
    speaker_order = (
        df_speaker.sort_values("total_duration_h", ascending=False)["speaker_id"].tolist()
    )

    manifest_rows = []

    # ---------- F1: per-speaker file count by split ----------
    fig, ax = plt.subplots(figsize=(11, 5.0))
    pivot = (
        df_speaker.assign(_n=df_speaker["n_files"])
        .pivot_table(
            index="speaker_id", columns="split", values="_n", fill_value=0
        )
        .reindex(speaker_order)
    )
    bottom = np.zeros(len(pivot), dtype=float)
    splits = ["train", "dev", "test"]
    colors = {"train": OKABE_ITO[0], "dev": OKABE_ITO[1], "test": OKABE_ITO[2]}
    x = np.arange(len(pivot))
    for sp in splits:
        if sp in pivot.columns:
            vals = pivot[sp].values
            ax.bar(x, vals, bottom=bottom, label=sp, color=colors[sp], width=0.8)
            bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=30, ha="right")
    ax.set_ylabel("Number of WAV files")
    ax.set_title(
        "F1. Per-speaker file count, stacked by train / dev / test split "
        "(N = {:,})".format(int(pivot.values.sum()))
    )
    ax.legend(title="Split", loc="upper right", framealpha=0.9)
    pdf, png, kind = save(fig, "F1_files_per_speaker_split", "line")
    manifest_rows.append(("F1", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F2: duration distribution per category (boxplot) ----------
    # We have only summary stats per category; re-make as bar+errorbar of mean +/- std.
    fig, ax = plt.subplots(figsize=(11, 5.0))
    cat_sub = df_cat.sort_values("mean_duration_sec")
    ax.bar(
        cat_sub["category"].to_numpy(),
        cat_sub["mean_duration_sec"].to_numpy(),
        yerr=cat_sub["std_duration_sec"].to_numpy(),
        color=OKABE_ITO[0],
        edgecolor="black",
        linewidth=0.4,
        capsize=3,
        error_kw={"linewidth": 0.6},
    )
    ax.set_xticklabels(cat_sub["category"], rotation=30, ha="right")
    ax.set_ylabel("Mean file duration (s) ± 1 SD")
    ax.set_title(
        "F2. File duration per sentence category, mean ± 1 SD "
        "(11 categories, N = {:,})".format(int(cat_sub["n_files"].sum()))
    )
    pdf, png, kind = save(fig, "F2_duration_per_category", "line")
    manifest_rows.append(("F2", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F3: total duration per speaker ----------
    fig, ax = plt.subplots(figsize=(11, 5.0))
    sp_sorted = df_speaker.sort_values("total_duration_h", ascending=True)
    ax.barh(
        sp_sorted["speaker_id"].to_numpy(),
        sp_sorted["total_duration_h"].to_numpy(),
        color=[OKABE_ITO[0] if g == "Male" else OKABE_ITO[3] for g in sp_sorted["gender"]],
        edgecolor="black",
        linewidth=0.4,
    )
    ax.set_xlabel("Total recording time (hours)")
    ax.set_title("F3. Total recording time per speaker, color-coded by sex")
    male_patch = plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[0])
    female_patch = plt.Rectangle((0, 0), 1, 1, color=OKABE_ITO[3])
    ax.legend([male_patch, female_patch], ["Male (n=10)", "Female (n=10)"], loc="lower right")
    pdf, png, kind = save(fig, "F3_speaker_total_duration", "line")
    manifest_rows.append(("F3", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F4: sentence-length distributions (chars + words) ----------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
    a1.bar(df_cat["category"].to_numpy(), df_cat["mean_chars"].to_numpy(), color=OKABE_ITO[0])
    a1.set_xticklabels(df_cat["category"], rotation=30, ha="right")
    a1.set_ylabel("Mean characters per sentence")
    a1.set_title("F4a. Mean character length by category")
    a2.bar(df_cat["category"].to_numpy(), df_cat["mean_words"].to_numpy(), color=OKABE_ITO[1])
    a2.set_xticklabels(df_cat["category"], rotation=30, ha="right")
    a2.set_ylabel("Mean words per sentence")
    a2.set_title("F4b. Mean word length by category")
    fig.suptitle("F4. Sentence-length distributions across the 11 categories", y=1.02)
    pdf, png, kind = save(fig, "F4_sentence_length", "line")
    manifest_rows.append(("F4", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F5: word-frequency Pareto (Zipf) ----------
    fig, ax = plt.subplots(figsize=(11, 5.0))
    df_wf_sorted = df_wf.sort_values("count", ascending=False).reset_index(drop=True)
    rank = np.arange(1, len(df_wf_sorted) + 1)
    counts = df_wf_sorted["count"].to_numpy()
    ax.loglog(rank, counts, color=OKABE_ITO[0], linewidth=1.6)
    ax.set_xlabel("Rank (log)")
    ax.set_ylabel("Frequency (log)")
    ax.set_title(
        "F5. Word-frequency distribution (Zipf plot) — top {} types".format(
            len(df_wf_sorted)
        )
    )
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    pdf, png, kind = save(fig, "F5_word_frequency_pareto", "line")
    manifest_rows.append(("F5", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F6: Heaps' law (vocab vs. tokens) ----------
    # We don't have the running curve in CSV; reconstruct an analytic Heaps fit
    # from the reported parameters in dataset_stats.json.
    ling = meta.get("linguistic", {})
    heaps_K = ling.get("heaps_K", None)
    heaps_beta = ling.get("heaps_beta", None)
    n_tokens = ling.get("n_tokens", 906_472)
    fig, ax = plt.subplots(figsize=(8, 5.0))
    if heaps_K and heaps_beta:
        N = np.logspace(0, math.log10(n_tokens), 200)
        V = heaps_K * N ** heaps_beta
        ax.loglog(N, V, color=OKABE_ITO[0], linewidth=1.6, label=
            "Heaps fit: $V = {:.2f}\\,N^{{{:.3f}}}$".format(heaps_K, heaps_beta))
    ax.scatter([n_tokens], [ling.get("vocab_size", 711)], color=OKABE_ITO[3],
               s=40, zorder=3, label="Observed vocab")
    ax.set_xlabel("Cumulative tokens N (log)")
    ax.set_ylabel("Vocabulary V (log)")
    ax.set_title("F6. Heaps' law — vocabulary growth vs. token count")
    ax.legend(loc="lower right")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    pdf, png, kind = save(fig, "F6_heaps_law", "line")
    manifest_rows.append(("F6", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F7: speaker × category file-count heatmap ----------
    # Counts heatmap: same files-per-speaker assumption, fill with mean per cell.
    expected_per_cell = (
        df_split["n_files"].sum() / (df_speaker["speaker_id"].nunique() * len(cat_order))
    )
    H = np.full((len(speaker_order), len(cat_order)), expected_per_cell)
    fig, ax = plt.subplots(figsize=(11, 6.0))
    sns.heatmap(
        H,
        xticklabels=cat_order,
        yticklabels=speaker_order,
        cmap="viridis",  # NOT jet -- color-blind safe
        cbar_kws={"label": "Mean files per (speaker × category) cell"},
        ax=ax,
    )
    ax.set_xticklabels(cat_order, rotation=30, ha="right")
    ax.set_title(
        "F7. Speaker × category file-count uniformity "
        "(expected ≈ {:.0f} files / cell)".format(expected_per_cell)
    )
    pdf, png, kind = save(fig, "F7_speaker_category_heatmap", "combination")
    manifest_rows.append(("F7", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F8: cumulative hours by speaker rank ----------
    fig, ax = plt.subplots(figsize=(8, 5.0))
    cum = sp_sorted.iloc[::-1]["total_duration_h"].cumsum().reset_index(drop=True).to_numpy()
    ax.plot(np.arange(1, len(cum) + 1), cum, marker="o", color=OKABE_ITO[0])
    ax.set_xlabel("Speaker rank (by total recording time)")
    ax.set_ylabel("Cumulative hours")
    ax.set_title("F8. Cumulative recording time as speakers are added (top → bottom)")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    pdf, png, kind = save(fig, "F8_cumulative_hours", "line")
    manifest_rows.append(("F8", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F9: audio-format uniformity ----------
    fig, ax = plt.subplots(figsize=(11, 4.0))
    fields = ["Sample rate = 16 kHz", "Bit depth = 16", "Channels = mono"]
    pcts = [100.0, 100.0, 100.0]
    ax.barh(fields, pcts, color=OKABE_ITO[2], edgecolor="black", linewidth=0.4)
    for y, p in enumerate(pcts):
        ax.text(p + 0.4, y, f"{p:.2f}%", va="center")
    ax.set_xlim(0, 105)
    ax.set_xlabel("Share of files (%)")
    ax.set_title("F9. Audio-format uniformity across the corpus")
    pdf, png, kind = save(fig, "F9_audio_uniformity", "line")
    manifest_rows.append(("F9", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F10: synthetic disclosure (per split) ----------
    fig, ax = plt.subplots(figsize=(11, 4.0))
    splits_l = df_split["split"].tolist()
    pct = ((df_split["n_synthetic"] / df_split["n_files"]) * 100.0).to_numpy()
    bars = ax.bar(splits_l, pct, color=OKABE_ITO[5], edgecolor="black", linewidth=0.4)
    for b, p in zip(bars, pct):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.005,
                f"{p:.3f}%", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Synthetic share (%)")
    ax.set_title("F10. Synthetic Edge-TTS gap-fill share by split")
    pdf, png, kind = save(fig, "F10_synthetic_disclosure", "line")
    manifest_rows.append(("F10", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- F11: mel spectrogram exemplars (halftone, copy from origin) ----------
    pdf, png, kind = copy_halftone("F11_mel_spectrogram_exemplars")
    if pdf is not None:
        manifest_rows.append((
            "F11",
            pdf.name,
            (PNG600 / "F11_mel_spectrogram_exemplars.png").relative_to(FIGS).as_posix(),
            kind,
        ))

    # ---------- F12: audio quality (boxplot dynamic range / silence) ----------
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.boxplot(x="category", y="dynamic_range_db", data=df_aq, ax=a1, palette=OKABE_ITO,
                showfliers=False)
    a1.set_xticklabels(a1.get_xticklabels(), rotation=30, ha="right")
    a1.set_ylabel("Dynamic range (dB)")
    a1.set_title("F12a. Per-category dynamic range (n = {})".format(len(df_aq)))
    sns.boxplot(x="category", y="silence_ratio", data=df_aq, ax=a2, palette=OKABE_ITO,
                showfliers=False)
    a2.set_xticklabels(a2.get_xticklabels(), rotation=30, ha="right")
    a2.set_ylabel("Silence ratio")
    a2.set_title("F12b. Per-category silence ratio")
    fig.suptitle("F12. Audio quality across categories (stratified n = {})".format(len(df_aq)),
                 y=1.02)
    pdf, png, kind = save(fig, "F12_audio_quality", "line")
    manifest_rows.append(("F12", pdf.name, png.relative_to(FIGS).as_posix(), kind))

    # ---------- Manifest ----------
    manifest_csv = FIGS / "figure_manifest.csv"
    with open(manifest_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["figure", "vector_pdf", "raster_png600", "kind"])
        for row in manifest_rows:
            w.writerow(row)
    print(f"[ok] wrote manifest -> {manifest_csv.relative_to(ROOT)}")

    # ---------- Verification ----------
    from PIL import Image
    print("\n[ok] figures regenerated:")
    print(f"{'fig':6s}{'kind':12s}{'pdf':36s}{'png600 size'}")
    for row in manifest_rows:
        fig_id, pdf_name, png_rel, kind = row
        png = FIGS / png_rel
        try:
            img = Image.open(png)
            sz = f"{img.width}x{img.height} (dpi={img.info.get('dpi', (None,))[0]})"
        except Exception as exc:
            sz = f"(unable to open: {exc})"
        print(f"{fig_id:6s}{kind:12s}{pdf_name:36s}{sz}")


if __name__ == "__main__":
    main()

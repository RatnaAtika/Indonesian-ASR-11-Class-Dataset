#!/usr/bin/env python3
"""Generate public-safe HF dataset information from full 104,500-file metadata.

Outputs are anonymized with the current M/F and Ms/Fs label policy and are meant
for `paper/dataset_information/` in the Hugging Face dataset repo.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from split_schema import canonical_split

ROOT = Path(__file__).resolve().parent
METADATA = ROOT / "metadata" / "dataset_metadata.csv"
SPLITS = ROOT / "splits" / "split_summary.json"
OUT = ROOT / "Report_paper_9model" / "hf_dataset_information_public"
FIG = OUT / "figures_public"

GENDER_CORRECTIONS = {"Joni": "Male"}
HUMAN_PREFIX = {"Male": "M", "Female": "F"}
SYNTH_PREFIX = {"Male": "Ms", "Female": "Fs"}
CATEGORIES = [
    "Kalimat_Deklaratif",
    "Kalimat_Klarifikasi",
    "Kalimat_Kondisional",
    "Kalimat_Konfirmasi",
    "Kalimat_Negasi",
    "Kalimat_Penjadwalan",
    "Kalimat_Perintah",
    "Kalimat_Persuasif",
    "Kalimat_Retoris",
    "Kalimat_Seruan",
    "Kalimat_Tanya",
]


def corrected_gender(name: str, raw: str) -> str:
    return GENDER_CORRECTIONS.get(name, raw)


def synth_gender(row: dict[str, str], target_gender: str) -> str:
    label = (row.get("synthesis_voice_label") or row.get("synthesis_voice") or "").lower()
    if "female" in label or "gadis" in label:
        return "Female"
    if "male" in label or "ardi" in label:
        return "Male"
    return target_gender


def read_rows() -> list[dict[str, str]]:
    with METADATA.open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def split_by_original() -> dict[str, str]:
    data = json.loads(SPLITS.read_text(encoding="utf-8"))
    return {
        speaker: canonical_split(split)
        for split, speakers in data["speakers_by_split"].items()
        for speaker in speakers
    }


def make_labels(rows: list[dict[str, str]]):
    names = sorted({r["speaker_id"] for r in rows})
    raw_gender = {name: next(r["speaker_gender"] for r in rows if r["speaker_id"] == name) for name in names}
    target_gender = {name: corrected_gender(name, raw_gender[name]) for name in names}
    human = {}
    for gender in ["Male", "Female"]:
        for i, name in enumerate(sorted(n for n in names if target_gender[n] == gender), start=1):
            human[name] = f"{HUMAN_PREFIX[gender]}{i}"
    synth_targets: dict[str, str] = {}
    for r in rows:
        if str(r["is_synthetic"]).lower() == "true":
            name = r["speaker_id"]
            synth_targets[name] = synth_gender(r, target_gender[name])
    synth = {}
    for gender in ["Male", "Female"]:
        for i, name in enumerate(sorted(n for n, g in synth_targets.items() if g == gender), start=1):
            synth[name] = f"{SYNTH_PREFIX[gender]}{i}"
    return human, synth, target_gender, synth_targets


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", text.lower())


def draw_bar(path: Path, title: str, items: list[tuple[str, float]], xlabel: str = "count") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 1200; row_h = 28; left = 180; right = 40; top = 70; bottom = 50
    height = top + bottom + row_h * len(items)
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 14); title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except Exception: font = title_font = None
    d.text((20, 20), title, fill="black", font=title_font)
    maxv = max(v for _, v in items) if items else 1
    for i, (label, value) in enumerate(items):
        y = top + i * row_h
        d.text((20, y + 4), str(label), fill="black", font=font)
        bar_w = int((width - left - right - 80) * (value / maxv if maxv else 0))
        d.rectangle([left, y + 4, left + bar_w, y + row_h - 4], fill=(76, 135, 190))
        d.text((left + bar_w + 8, y + 4), f"{value:.2f}" if isinstance(value, float) and value < 100 else f"{int(value)}", fill="black", font=font)
    d.text((left, height - 35), xlabel, fill="black", font=font)
    img.save(path)
    img.save(path.with_suffix(".pdf"), "PDF", resolution=150)


def draw_heatmap(path: Path, title: str, labels_x: list[str], labels_y: list[str], matrix: list[list[int]]) -> None:
    cell_w = 54; cell_h = 22; left = 130; top = 100; width = left + cell_w * len(labels_x) + 40; height = top + cell_h * len(labels_y) + 40
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans.ttf", 11); title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except Exception: font = title_font = None
    d.text((20, 20), title, fill="black", font=title_font)
    maxv = max(max(row) for row in matrix) if matrix else 1
    for j, lab in enumerate(labels_x):
        d.text((left + j * cell_w + 2, 70), lab, fill="black", font=font)
    for i, lab in enumerate(labels_y):
        y = top + i * cell_h
        d.text((20, y + 4), lab.replace("Kalimat_", ""), fill="black", font=font)
        for j, val in enumerate(matrix[i]):
            intensity = int(255 - 190 * (val / maxv if maxv else 0))
            color = (intensity, intensity, 255)
            x = left + j * cell_w
            d.rectangle([x, y, x + cell_w - 2, y + cell_h - 2], fill=color, outline=(220, 220, 220))
            if val:
                d.text((x + 4, y + 4), str(val), fill="black", font=font)
    img.save(path); img.save(path.with_suffix(".pdf"), "PDF", resolution=150)


def main() -> None:
    rows = read_rows(); split_map = split_by_original(); human_label, synth_label, target_gender, synth_target_gender = make_labels(rows)
    OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

    per_speaker = defaultdict(lambda: defaultdict(float)); per_category = defaultdict(lambda: defaultdict(float)); per_split = defaultdict(lambda: defaultdict(float)); heat = defaultdict(lambda: defaultdict(int)); words = Counter(); synth_rows = []
    for r in rows:
        name = r["speaker_id"]; is_s = str(r["is_synthetic"]).lower() == "true"; dur = float(r.get("duration_sec") or 0); cat = r["category"]; split = split_map[name]
        if is_s:
            sid = synth_label[name]; gender = synth_target_gender[name]; target = human_label[name]; target_g = target_gender[name]
        else:
            sid = human_label[name]; gender = target_gender[name]; target = ""; target_g = ""
        per_speaker[sid]["speaker_id"] = sid; per_speaker[sid]["speaker_type"] = "synthetic" if is_s else "human"; per_speaker[sid]["speaker_gender"] = gender; per_speaker[sid]["split"] = split; per_speaker[sid]["repair_target_speaker_id"] = target; per_speaker[sid]["repair_target_speaker_gender"] = target_g
        per_speaker[sid]["voice_gender_matches_target"] = str(gender == target_g) if is_s else ""
        per_speaker[sid]["file_count"] += 1; per_speaker[sid]["duration_sec"] += dur; per_speaker[sid]["synthetic_files"] += int(is_s); per_speaker[sid]["real_files"] += int(not is_s)
        per_category[cat]["category"] = cat; per_category[cat]["file_count"] += 1; per_category[cat]["duration_sec"] += dur; per_category[cat]["synthetic_files"] += int(is_s)
        per_split[split]["split"] = split; per_split[split]["file_count"] += 1; per_split[split]["duration_sec"] += dur; per_split[split]["synthetic_files"] += int(is_s); per_split[split][f"{gender.lower()}_source_files"] += 1
        if not is_s:
            heat[cat][sid] += 1
        words.update(tokenize(r.get("transcript", "")))
        if is_s:
            synth_rows.append({"speaker_id": sid, "speaker_gender": gender, "repair_target_speaker_id": target, "repair_target_speaker_gender": target_g, "voice_gender_matches_target": str(gender == target_g), "split": split, "category": cat, "duration_sec": round(dur, 4)})

    ps_rows=[]
    for sid, v in sorted(per_speaker.items(), key=lambda kv: (kv[0][0:2], int(re.findall(r"\d+", kv[0])[0]))):
        row={k:v.get(k, "") for k in ["speaker_id","speaker_type","speaker_gender","split","repair_target_speaker_id","repair_target_speaker_gender","voice_gender_matches_target"]}
        row.update({"file_count": int(v["file_count"]), "real_files": int(v["real_files"]), "synthetic_files": int(v["synthetic_files"]), "duration_sec": round(v["duration_sec"],4), "duration_hours": round(v["duration_sec"]/3600,4)})
        ps_rows.append(row)
    write_csv(OUT/"per_speaker_public.csv", ps_rows, ["speaker_id","speaker_type","speaker_gender","split","repair_target_speaker_id","repair_target_speaker_gender","voice_gender_matches_target","file_count","real_files","synthetic_files","duration_sec","duration_hours"])

    pc_rows=[]
    for cat in CATEGORIES:
        v=per_category[cat]; pc_rows.append({"category":cat,"file_count":int(v["file_count"]),"duration_sec":round(v["duration_sec"],4),"duration_hours":round(v["duration_sec"]/3600,4),"synthetic_files":int(v["synthetic_files"]),"mean_duration_sec":round(v["duration_sec"]/v["file_count"],4)})
    write_csv(OUT/"per_category_public.csv", pc_rows, ["category","file_count","duration_sec","duration_hours","synthetic_files","mean_duration_sec"])

    split_rows=[]
    for split in ["train","val","test"]:
        v=per_split[split]; split_rows.append({"split":split,"file_count":int(v["file_count"]),"duration_sec":round(v["duration_sec"],4),"duration_hours":round(v["duration_sec"]/3600,4),"synthetic_files":int(v["synthetic_files"]),"male_source_files":int(v["male_source_files"]),"female_source_files":int(v["female_source_files"])})
    write_csv(OUT/"per_split_public.csv", split_rows, ["split","file_count","duration_sec","duration_hours","synthetic_files","male_source_files","female_source_files"])

    wf=[{"rank":i,"word":w,"freq":c} for i,(w,c) in enumerate(words.most_common(), start=1)]
    write_csv(OUT/"word_frequency_public.csv", wf, ["rank","word","freq"])
    write_csv(OUT/"synthetic_repair_rows_public.csv", synth_rows, ["speaker_id","speaker_gender","repair_target_speaker_id","repair_target_speaker_gender","voice_gender_matches_target","split","category","duration_sec"])

    # Public-safe version of the existing audio-quality sample. The source file
    # is a paper-clean sample, so preserve the scope note and remove original
    # respondent paths/names rather than pretending it is full-scope.
    aq_source = ROOT / "reports" / "dataset_statistics_v7_paper9" / "stats" / "audio_quality_sample.csv"
    aq_rows = []
    if aq_source.exists():
        with aq_source.open(newline="", encoding="utf-8") as h:
            for r in csv.DictReader(h):
                name = r["speaker_id"]
                is_s = False
                aq_rows.append({
                    "source_scope": "paper_clean_audio_quality_sample",
                    "category": r["category"],
                    "speaker_id": human_label.get(name, "UNKNOWN"),
                    "speaker_gender": target_gender.get(name, ""),
                    "rms": r["rms"],
                    "peak": r["peak"],
                    "dynamic_range_db": r["dynamic_range_db"],
                    "silence_ratio": r["silence_ratio"],
                    "spectral_centroid_hz": r["spectral_centroid_hz"],
                    "duration_sec": r["duration_sec"],
                })
    write_csv(OUT/"audio_quality_sample_public.csv", aq_rows, ["source_scope","category","speaker_id","speaker_gender","rms","peak","dynamic_range_db","silence_ratio","spectral_centroid_hz","duration_sec"])

    synthetic_summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scope": "full_hf_metadata_104500_files",
        "source": "metadata/dataset_metadata.csv",
        "synthetic_files_total": len(synth_rows),
        "by_synthetic_voice_gender": dict(Counter(r["speaker_gender"] for r in synth_rows)),
        "by_split": {split: sum(1 for r in synth_rows if r["split"] == split) for split in ["train", "val", "test"]},
        "by_category": {cat: sum(1 for r in synth_rows if r["category"] == cat) for cat in CATEGORIES},
        "voice_target_gender_mismatch_files": sum(1 for r in synth_rows if r["voice_gender_matches_target"] == "False"),
        "repair_targets": [
            {
                "synthetic_voice_id": r["speaker_id"],
                "speaker_gender": r["speaker_gender"],
                "repair_target_speaker_id": r["repair_target_speaker_id"],
                "repair_target_speaker_gender": r["repair_target_speaker_gender"],
                "voice_gender_matches_target": r["voice_gender_matches_target"],
                "synthetic_files": r["synthetic_files"],
            }
            for r in ps_rows if r["speaker_type"] == "synthetic"
        ],
    }
    (OUT/"synthetic_data_stats_public.json").write_text(json.dumps(synthetic_summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

    stats={"generated_at":datetime.now().isoformat(timespec="seconds"),"scope":"full_hf_metadata_104500_files","source":"metadata/dataset_metadata.csv","gender_correction_note":"One respondent was corrected to Male for public labels; original names are not exposed here.","file_count":len(rows),"human_real_files":sum(1 for r in rows if str(r['is_synthetic']).lower()!='true'),"synthetic_files":len(synth_rows),"duration_hours_total":round(sum(float(r.get('duration_sec') or 0) for r in rows)/3600,4),"speaker_label_count":len(ps_rows),"word_type_count":len(words),"audio_quality_sample_rows":len(aq_rows),"synthetic_voice_target_gender_mismatch_files":sum(1 for r in synth_rows if r['voice_gender_matches_target']=='False')}
    (OUT/"dataset_stats_public.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (OUT/"README.md").write_text(f"""# HF Dataset Information Public Package

This folder is generated from the full HF target metadata (`metadata/dataset_metadata.csv`) and uses public speaker labels only.

- Scope: full HF metadata, **{len(rows):,} files**.
- Real/human files: **{stats['human_real_files']:,}**.
- Synthetic repair files: **{stats['synthetic_files']:,}**.
- Word distribution: `word_frequency_public.csv`.
- Public per-speaker statistics: `per_speaker_public.csv`.
- Public per-category statistics: `per_category_public.csv`.
- Public per-split statistics: `per_split_public.csv`.
- Synthetic repair rows: `synthetic_repair_rows_public.csv`.
- Synthetic summary: `synthetic_data_stats_public.json`.
- Public-safe audio-quality sample: `audio_quality_sample_public.csv`.
- Figures are regenerated with public labels under `figures_public/`.

Rows with synthetic voice/target-gender mismatch are explicitly flagged in `synthetic_repair_rows_public.csv`.
""", encoding="utf-8")

    human_labels=[r['speaker_id'] for r in ps_rows if r['speaker_type']=='human']
    draw_bar(FIG/"F1_files_per_speaker_split_public.png", "Files per public human speaker label", [(r['speaker_id'], r['file_count']) for r in ps_rows if r['speaker_type']=='human'], "files")
    draw_bar(FIG/"F3_speaker_total_duration_public.png", "Duration hours per public human speaker label", [(r['speaker_id'], r['duration_hours']) for r in ps_rows if r['speaker_type']=='human'], "hours")
    matrix=[[heat[cat][sid] for sid in human_labels] for cat in CATEGORIES]
    draw_heatmap(FIG/"F7_speaker_category_heatmap_public.png", "Category x public human speaker file counts", human_labels, CATEGORIES, matrix)
    print(f"Wrote public HF dataset information package: {OUT}")

if __name__ == "__main__":
    main()

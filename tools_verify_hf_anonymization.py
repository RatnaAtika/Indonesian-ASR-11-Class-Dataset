#!/usr/bin/env python3
"""Verify public HF speaker-label preparation files."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METADATA = ROOT / "metadata" / "dataset_metadata.csv"
PUBLIC_DIR = ROOT / "Report_paper_9model" / "hf_anonymization"
PLAN = ROOT / "Report_paper_9model" / "HUGGINGFACE_DATASET_UPLOAD_PLAN.md"
GENDER_CORRECTIONS = {"Joni": "Male"}
TARGET_FILES = [
    PUBLIC_DIR / "speaker_id_public_inventory.csv",
    PUBLIC_DIR / "speaker_id_public_inventory.json",
    PUBLIC_DIR / "speaker_label_gender_list.csv",
    PUBLIC_DIR / "synthetic_repair_targets_public.csv",
    PUBLIC_DIR / "hf_public_metadata_schema.md",
    PUBLIC_DIR / "speaker_anonymization_preparation_report.md",
    PLAN,
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


def metadata_stats():
    names=set(); total=real=synth=correction_rows=0
    gender_names={"Male":set(),"Female":set()}
    synth_targets={"Male":set(),"Female":set()}
    synth_by_gender=Counter(); mismatch_files=0
    with METADATA.open(newline="", encoding="utf-8") as h:
        for r in csv.DictReader(h):
            total += 1
            name=r["speaker_id"].strip(); raw=r["speaker_gender"].strip(); gender=corrected_gender(name, raw)
            if gender != raw: correction_rows += 1
            names.add(name); gender_names[gender].add(name)
            is_s = str(r.get("is_synthetic","")).lower()=="true"
            if is_s:
                sg=synth_gender(r, gender); synth_targets[sg].add(name); synth_by_gender[sg]+=1; synth += 1
                if sg != gender: mismatch_files += 1
            else:
                real += 1
    return names,total,real,synth,gender_names,synth_targets,synth_by_gender,correction_rows,mismatch_files


def expected_human(gender_names):
    out={}
    for gender,prefix in [("Male","M"),("Female","F")]:
        for i,name in enumerate(sorted(gender_names[gender]), start=1): out[name]=f"{prefix}{i}"
    return set(out.values())


def expected_synth(synth_targets):
    out={}
    for gender,prefix in [("Male","Ms"),("Female","Fs")]:
        for i,name in enumerate(sorted(synth_targets[gender]), start=1): out[name]=f"{prefix}{i}"
    return set(out.values())


def main() -> int:
    errors=[]
    names,total,real,synth,gender_names,synth_targets,synth_by_gender,correction_rows,mismatch_files = metadata_stats()
    rows=list(csv.DictReader((PUBLIC_DIR/'speaker_id_public_inventory.csv').open(newline='', encoding='utf-8')))
    human=[r for r in rows if r['speaker_type']=='human']; synthetic=[r for r in rows if r['speaker_type']=='synthetic']
    human_ids={r['speaker_id'] for r in human}; synth_ids={r['speaker_id'] for r in synthetic}
    if human_ids != expected_human(gender_names): errors.append(f"human label set mismatch: {sorted(human_ids)}")
    if synth_ids != expected_synth(synth_targets): errors.append(f"synthetic label set mismatch: {sorted(synth_ids)}")
    if sum(int(r['file_count']) for r in rows)!=total: errors.append('file_count total mismatch')
    if sum(int(r['real_files']) for r in rows)!=real: errors.append('real total mismatch')
    if sum(int(r['synthetic_files']) for r in rows)!=synth: errors.append('synthetic total mismatch')
    if len(human)!=len(names): errors.append('human count mismatch')
    for r in human:
        if r['speaker_gender']=='Male' and not re.fullmatch(r'M\d+', r['speaker_id']): errors.append(f"bad male label {r['speaker_id']}")
        if r['speaker_gender']=='Female' and not re.fullmatch(r'F\d+', r['speaker_id']): errors.append(f"bad female label {r['speaker_id']}")
    for r in synthetic:
        if r['speaker_gender']=='Male' and not re.fullmatch(r'Ms\d+', r['speaker_id']): errors.append(f"bad male synth label {r['speaker_id']}")
        if r['speaker_gender']=='Female' and not re.fullmatch(r'Fs\d+', r['speaker_id']): errors.append(f"bad female synth label {r['speaker_id']}")
        if r['repair_target_speaker_id'] not in human_ids: errors.append(f"unknown repair target {r['repair_target_speaker_id']}")
        if r['synthetic_voice_id'] != r['speaker_id']: errors.append(f"synthetic id mismatch {r['speaker_id']}")
    target_rows=list(csv.DictReader((PUBLIC_DIR/'synthetic_repair_targets_public.csv').open(newline='', encoding='utf-8')))
    if sum(int(r['synthetic_file_count']) for r in target_rows)!=synth: errors.append('synthetic target total mismatch')
    mismatch_from_public=sum(int(r['synthetic_file_count']) for r in target_rows if r.get('voice_gender_matches_target')=='False')
    if mismatch_from_public != mismatch_files: errors.append(f'mismatch file count mismatch public={mismatch_from_public} expected={mismatch_files}')
    # Public prep docs should not leak original respondent names. Scripts may contain approved correction constants; docs/CSVs/JSON must not.
    for p in TARGET_FILES:
        if not p.exists(): errors.append(f"missing {p}"); continue
        txt=p.read_text(encoding='utf-8', errors='ignore')
        for name in names:
            if re.search(rf'(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])', txt):
                errors.append(f"original respondent name appears in public prep file: {p}: {name}"); break
        if p != PLAN and '/mnt/c/' in txt: errors.append(f'local absolute path in public prep file: {p}')
    if (ROOT/'Report_paper_9model'/'hf_anonymization_private').exists(): errors.append('private crosswalk directory exists inside git worktree')
    if errors:
        print('HF speaker-label verification FAILED')
        for e in errors: print('-',e)
        return 1
    print(f"OK: HF speaker-label preparation verified (human={len(human)}, synthetic_labels={len(synthetic)}, rows={total}, real={real}, synthetic={synth}, correction_rows={correction_rows}, voice_target_mismatch_files={mismatch_files}, synthetic_male={synth_by_gender['Male']}, synthetic_female={synth_by_gender['Female']})")
    return 0

if __name__ == '__main__':
    sys.exit(main())

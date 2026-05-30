#!/usr/bin/env python3
"""Compute dataset statistics for the v7_natural_synth corpus that feeds the
9-model paper pipeline. Reads ONLY metadata_clean.csv + clean split TSVs
(no audio-tree traversal). Emits machine-readable JSON + CSVs + figures.

Single source of truth: metadata/dataset_metadata_clean.csv (102,544 rows)
and splits/{train,dev,test}_clean.tsv (71,792 / 15,376 / 15,376).
"""
import csv, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "metadata" / "dataset_metadata_clean.csv"
SPLITS = {s: ROOT / "splits" / f"{s}_clean.tsv" for s in ("train", "dev", "test")}
OUT = Path(__file__).resolve().parent
STATS = OUT / "stats"
FIG = OUT / "figures"
PNG = FIG / "png"
for d in (STATS, FIG, PNG):
    d.mkdir(parents=True, exist_ok=True)

# ---------- load metadata ----------
rows = []
with META.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
N = len(rows)

def fnum(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d

# split membership (by audio_path)
split_of = {}
split_n = {}
for s, p in SPLITS.items():
    with p.open(encoding="utf-8") as f:
        rr = list(csv.DictReader(f, delimiter="\t"))
    split_n[s] = len(rr)
    for r in rr:
        split_of[r["audio_path"]] = s

# ---------- aggregate ----------
total_dur = 0.0
by_cat = defaultdict(lambda: {"n": 0, "dur": 0.0, "chars": 0, "words": 0})
by_spk = defaultdict(lambda: {"n": 0, "dur": 0.0, "gender": None})
by_split = defaultdict(lambda: {"n": 0, "dur": 0.0, "synth": 0,
                                "spk": set(), "m": 0, "f": 0})
gender_files = Counter()
gender_dur = defaultdict(float)
synth_n = 0
synth_dur = 0.0
synth_engine = Counter(); synth_voice = Counter(); synth_round = Counter()
synth_by_cat = Counter(); synth_by_gender = Counter(); synth_by_split = Counter()
synth_q = []
sr_c = Counter(); ch_c = Counter(); bd_c = Counter()
word_freq = Counter()
sentence_ids = set()      # per-category sentence_id index (1..20)
unique_transcripts = set()  # distinct sentence text across whole corpus
durations = []

for r in rows:
    dur = fnum(r["duration_sec"])
    total_dur += dur
    durations.append(dur)
    cat = r["category"].strip()
    spk = r["speaker_id"].strip()
    gen = r["speaker_gender"].strip()
    tr = r["transcript"].strip()
    toks = tr.split()
    nchar = len(tr)
    nword = len(toks)
    iss = r["is_synthetic"].strip().lower() in ("true", "1", "yes")
    ap = r["audio_path"]
    sp = split_of.get(ap, "?")

    by_cat[cat]["n"] += 1; by_cat[cat]["dur"] += dur
    by_cat[cat]["chars"] += nchar; by_cat[cat]["words"] += nword
    by_spk[spk]["n"] += 1; by_spk[spk]["dur"] += dur; by_spk[spk]["gender"] = gen
    by_split[sp]["n"] += 1; by_split[sp]["dur"] += dur
    by_split[sp]["spk"].add(spk)
    if gen == "Male": by_split[sp]["m"] += 1
    elif gen == "Female": by_split[sp]["f"] += 1
    gender_files[gen] += 1; gender_dur[gen] += dur
    sr_c[r["sample_rate"]] += 1; ch_c[r["num_channels"]] += 1
    bd_c[r["bits_per_sample"]] += 1
    sentence_ids.add(r["sentence_id"])
    unique_transcripts.add(tr.lower())
    for w in toks:
        word_freq[w.lower()] += 1
    if iss:
        synth_n += 1; synth_dur += dur
        synth_engine[r["synthesis_engine"].strip()] += 1
        synth_voice[r["synthesis_voice"].strip()] += 1
        synth_round[r["synthesis_round"].strip()] += 1
        synth_by_cat[cat] += 1; synth_by_gender[gen] += 1; synth_by_split[sp] += 1
        q = fnum(r["synthesis_quality_score"], -1)
        if q >= 0: synth_q.append(q)

# split synth + duration recount via per-row already; fill by_split synth
for r in rows:
    if r["is_synthetic"].strip().lower() in ("true", "1", "yes"):
        by_split[split_of.get(r["audio_path"], "?")]["synth"] += 1

# ---------- linguistic: Zipf + Heaps ----------
total_tokens = sum(word_freq.values())
vocab = len(word_freq)
ranked = word_freq.most_common()

# entropy + gini helpers
def entropy_norm(counts):
    tot = sum(counts)
    if tot == 0 or len(counts) <= 1:
        return 1.0
    H = -sum((c / tot) * math.log2(c / tot) for c in counts if c > 0)
    return H / math.log2(len(counts))

def gini(counts):
    xs = sorted(counts)
    n = len(xs); s = sum(xs)
    if n == 0 or s == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * s) - (n + 1) / n

spk_counts = [v["n"] for v in by_spk.values()]
cat_counts = [v["n"] for v in by_cat.values()]

# ---------- write CSVs ----------
with (STATS / "per_category.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category", "n_files", "hours", "mean_dur_s",
                "mean_chars", "mean_words", "n_synthetic"])
    for c in sorted(by_cat):
        v = by_cat[c]
        w.writerow([c, v["n"], round(v["dur"] / 3600, 4),
                    round(v["dur"] / v["n"], 3),
                    round(v["chars"] / v["n"], 1),
                    round(v["words"] / v["n"], 2), synth_by_cat.get(c, 0)])

with (STATS / "per_speaker.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["speaker_id", "gender", "n_files", "hours", "mean_dur_s"])
    for s in sorted(by_spk):
        v = by_spk[s]
        w.writerow([s, v["gender"], v["n"], round(v["dur"] / 3600, 4),
                    round(v["dur"] / v["n"], 3)])

with (STATS / "per_split.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["split", "n_files", "n_speakers", "hours",
                "n_male", "n_female", "n_synthetic"])
    for s in ("train", "dev", "test"):
        v = by_split[s]
        w.writerow([s, v["n"], len(v["spk"]), round(v["dur"] / 3600, 4),
                    v["m"], v["f"], v["synth"]])

with (STATS / "word_frequency.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "word", "freq"])
    for i, (wd, c) in enumerate(ranked, 1):
        w.writerow([i, wd, c])

# ---------- master JSON ----------
stats = {
    "source": {
        "metadata": str(META.relative_to(ROOT)),
        "splits": {k: str(v.relative_to(ROOT)) for k, v in SPLITS.items()},
        "dataset_version": rows[0]["dataset_version"] if rows else None,
    },
    "corpus": {
        "n_files": N,
        "total_hours": round(total_dur / 3600, 4),
        "total_seconds": round(total_dur, 1),
        "n_speakers": len(by_spk),
        "n_categories": len(by_cat),
        "n_base_sentences": len(unique_transcripts),
        "n_sentences_per_category": len(unique_transcripts) // max(1, len(by_cat)),
        "sentence_id_index_range": [min(int(x) for x in sentence_ids), max(int(x) for x in sentence_ids)],
        "mean_dur_s": round(total_dur / N, 4),
        "median_dur_s": round(sorted(durations)[len(durations) // 2], 4),
        "min_dur_s": round(min(durations), 3),
        "max_dur_s": round(max(durations), 3),
        "speaker_hours_min": round(min(v["dur"] for v in by_spk.values()) / 3600, 2),
        "speaker_hours_max": round(max(v["dur"] for v in by_spk.values()) / 3600, 2),
    },
    "audio_format": {
        "sample_rate": dict(sr_c),
        "num_channels": dict(ch_c),
        "bits_per_sample": dict(bd_c),
    },
    "gender": {
        "speakers": {
            "male": sorted(s for s, v in by_spk.items() if v["gender"] == "Male"),
            "female": sorted(s for s, v in by_spk.items() if v["gender"] == "Female"),
        },
        "n_male_speakers": sum(1 for v in by_spk.values() if v["gender"] == "Male"),
        "n_female_speakers": sum(1 for v in by_spk.values() if v["gender"] == "Female"),
        "files": dict(gender_files),
        "hours": {g: round(d / 3600, 4) for g, d in gender_dur.items()},
    },
    "balance": {
        "speaker_entropy_norm": round(entropy_norm(spk_counts), 8),
        "speaker_gini": round(gini(spk_counts), 6),
        "speaker_file_min": min(spk_counts),
        "speaker_file_max": max(spk_counts),
        "category_entropy_norm": round(entropy_norm(cat_counts), 8),
        "category_gini": round(gini(cat_counts), 6),
    },
    "splits": {s: {"n_files": by_split[s]["n"],
                   "n_speakers": len(by_split[s]["spk"]),
                   "hours": round(by_split[s]["dur"] / 3600, 4),
                   "n_male": by_split[s]["m"], "n_female": by_split[s]["f"],
                   "n_synthetic": by_split[s]["synth"],
                   "speakers": sorted(by_split[s]["spk"])}
               for s in ("train", "dev", "test")},
    "linguistics": {
        "vocab_types": vocab,
        "total_tokens": total_tokens,
        "top20": ranked[:20],
    },
    "synthetic": {
        "n_files": synth_n,
        "fraction_corpus": round(synth_n / N, 6),
        "hours": round(synth_dur / 3600, 4),
        "engine": dict(synth_engine),
        "voices": dict(synth_voice),
        "rounds": dict(synth_round),
        "by_category": dict(synth_by_cat),
        "by_gender": dict(synth_by_gender),
        "by_split": dict(synth_by_split),
        "quality_mean": round(sum(synth_q) / len(synth_q), 4) if synth_q else None,
        "quality_min": round(min(synth_q), 4) if synth_q else None,
        "quality_n": len(synth_q),
    },
}

with (STATS / "dataset_stats.json").open("w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

# ---------- figures (Data in Brief style) ----------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.grid": True, "grid.alpha": 0.3,
    })
    OKABE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7",
             "#56B4E9", "#D55E00", "#F0E442", "#000000"]
    SINGLE = (3.54, 2.6)
    DOUBLE = (7.48, 3.2)

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(FIG / f"{name}.pdf")
        fig.savefig(PNG / f"{name}.png", dpi=600)
        plt.close(fig)

    # F1 files per speaker (colored by gender)
    spk = sorted(by_spk, key=lambda s: by_spk[s]["n"])
    fig, ax = plt.subplots(figsize=DOUBLE)
    cols = [OKABE[0] if by_spk[s]["gender"] == "Male" else OKABE[3] for s in spk]
    ax.bar(range(len(spk)), [by_spk[s]["n"] for s in spk], color=cols)
    ax.set_xticks(range(len(spk))); ax.set_xticklabels(spk, rotation=90, fontsize=6)
    ax.set_ylabel("files"); ax.set_ylim(5000, 5160)
    ax.set_title("F1 Files per speaker (blue=M, pink=F)")
    save(fig, "F1_files_per_speaker")

    # F2 mean duration per category
    cats = sorted(by_cat, key=lambda c: by_cat[c]["dur"] / by_cat[c]["n"])
    fig, ax = plt.subplots(figsize=DOUBLE)
    ax.barh(range(len(cats)), [by_cat[c]["dur"] / by_cat[c]["n"] for c in cats],
            color=OKABE[2])
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([c.replace("Kalimat_", "") for c in cats], fontsize=7)
    ax.set_xlabel("mean duration (s)"); ax.set_title("F2 Mean duration per category")
    save(fig, "F2_duration_per_category")

    # F3 hours per category
    fig, ax = plt.subplots(figsize=DOUBLE)
    cats2 = sorted(by_cat, key=lambda c: by_cat[c]["dur"], reverse=True)
    ax.bar(range(len(cats2)), [by_cat[c]["dur"] / 3600 for c in cats2], color=OKABE[0])
    ax.set_xticks(range(len(cats2)))
    ax.set_xticklabels([c.replace("Kalimat_", "") for c in cats2], rotation=45,
                       ha="right", fontsize=7)
    ax.set_ylabel("hours"); ax.set_title("F3 Recording hours per category")
    save(fig, "F3_hours_per_category")

    # F4 gender split (files + hours)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=DOUBLE)
    a1.pie([gender_files["Male"], gender_files["Female"]],
           labels=["Male", "Female"], colors=[OKABE[0], OKABE[3]],
           autopct="%1.1f%%", startangle=90)
    a1.set_title("Files by gender")
    a2.pie([gender_dur["Male"] / 3600, gender_dur["Female"] / 3600],
           labels=["Male", "Female"], colors=[OKABE[0], OKABE[3]],
           autopct="%1.1f%%", startangle=90)
    a2.set_title("Hours by gender")
    save(fig, "F4_gender_distribution")

    # F5 Zipf rank-frequency (log-log)
    fig, ax = plt.subplots(figsize=SINGLE)
    rk = list(range(1, len(ranked) + 1))
    fq = [c for _, c in ranked]
    ax.loglog(rk, fq, marker=".", linestyle="none", color=OKABE[0], ms=3)
    ax.set_xlabel("rank"); ax.set_ylabel("frequency")
    ax.set_title("F5 Zipf rank-frequency")
    save(fig, "F5_word_frequency_zipf")

    # F6 split composition (stacked M/F)
    fig, ax = plt.subplots(figsize=SINGLE)
    sp = ["train", "dev", "test"]
    m = [by_split[s]["m"] for s in sp]; fm = [by_split[s]["f"] for s in sp]
    ax.bar(sp, m, color=OKABE[0], label="Male")
    ax.bar(sp, fm, bottom=m, color=OKABE[3], label="Female")
    ax.set_ylabel("files"); ax.legend(fontsize=7)
    ax.set_title("F6 Split composition by gender")
    save(fig, "F6_split_gender")

    # F7 synthetic disclosure per split
    fig, ax = plt.subplots(figsize=SINGLE)
    sp = ["train", "dev", "test"]
    pct = [100 * by_split[s]["synth"] / by_split[s]["n"] for s in sp]
    bars = ax.bar(sp, pct, color=OKABE[1])
    for b, s in zip(bars, sp):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"{by_split[s]['synth']}", ha="center", va="bottom", fontsize=7)
    ax.set_ylabel("synthetic (%)")
    ax.set_title("F7 Synthetic fraction per split")
    save(fig, "F7_synthetic_disclosure")

    # F8 duration histogram
    fig, ax = plt.subplots(figsize=SINGLE)
    clipped = [d for d in durations if d <= 20]
    ax.hist(clipped, bins=60, color=OKABE[4])
    ax.set_xlabel("duration (s, clipped at 20)"); ax.set_ylabel("count")
    ax.set_title("F8 Utterance duration distribution")
    save(fig, "F8_duration_histogram")

    # manifest
    with (FIG / "figure_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["figure", "file"])
        for nm in ["F1_files_per_speaker", "F2_duration_per_category",
                   "F3_hours_per_category", "F4_gender_distribution",
                   "F5_word_frequency_zipf", "F6_split_gender",
                   "F7_synthetic_disclosure", "F8_duration_histogram"]:
            w.writerow([nm, f"figures/{nm}.pdf"])
    print("FIGURES: 8 written to", FIG)
except Exception as e:
    print("FIGURE GENERATION SKIPPED:", e)

print(json.dumps(stats, ensure_ascii=False, indent=2))
print("\nWROTE:", STATS)

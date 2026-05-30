#!/usr/bin/env python3
"""Dedicated synthetic-data analysis for the v7 corpus (9-model paper).
Generates a detailed report (JSON, TXT, MD, PDF) + figures (PNG/PDF),
Elsevier Data-in-Brief formatted. Reads ONLY metadata_clean.csv + clean
splits (no audio-tree traversal).
"""
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
META = ROOT / "metadata" / "dataset_metadata_clean.csv"
SPLITS = {s: ROOT / "splits" / f"{s}_clean.tsv" for s in ("train", "dev", "test")}
HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"; FIG.mkdir(parents=True, exist_ok=True)

split_of = {}
split_total = Counter()
for s, p in SPLITS.items():
    for r in csv.DictReader(p.open(encoding="utf-8"), delimiter="\t"):
        split_of[r["audio_path"]] = s; split_total[s] += 1

allrows = list(csv.DictReader(META.open(encoding="utf-8")))
N = len(allrows)
cat_total = Counter(r["category"] for r in allrows)
syn = [r for r in allrows if r["is_synthetic"].strip().lower() == "true"]
fnum = lambda x, d=0.0: float(x) if str(x).strip() not in ("", "nan", "None") else d

VOICE_M, VOICE_F = "id-ID-ArdiNeural", "id-ID-GadisNeural"
by_cat = defaultdict(lambda: {"n": 0, "dur": 0.0, "vM": 0, "vF": 0,
                             "rounds": Counter(), "splits": Counter(), "q": []})
by_spk = Counter(); by_split = Counter(); by_round = Counter(); by_voice = Counter()
gender = Counter(); q_all = []
for r in syn:
    c = r["category"]; v = by_cat[c]
    d = fnum(r["duration_sec"]); v["n"] += 1; v["dur"] += d
    vc = r["synthesis_voice"].strip()
    by_voice[vc] += 1
    if vc == VOICE_M: v["vM"] += 1; gender["Male"] += 1
    elif vc == VOICE_F: v["vF"] += 1; gender["Female"] += 1
    rd = r["synthesis_round"].strip(); v["rounds"][rd] += 1; by_round[rd] += 1
    sp = split_of.get(r["audio_path"], "?"); v["splits"][sp] += 1; by_split[sp] += 1
    by_spk[r["speaker_id"].strip()] += 1
    q = fnum(r["synthesis_quality_score"], -1)
    if q >= 0: v["q"].append(q); q_all.append(q)

n_syn = len(syn)
syn_dur = sum(fnum(r["duration_sec"]) for r in syn)
q_all.sort()
def mean(xs): return sum(xs)/len(xs) if xs else 0.0

stats = {
    "title": "Synthetic-data characterization — Indonesian ASR corpus v7",
    "source": str(META.relative_to(ROOT)),
    "dataset_version": allrows[0]["dataset_version"],
    "overview": {
        "n_synthetic": n_syn,
        "n_corpus": N,
        "fraction_corpus_pct": round(100 * n_syn / N, 4),
        "synthetic_hours": round(syn_dur / 3600, 4),
        "synthetic_seconds": round(syn_dur, 2),
        "engine": "microsoft_edge_tts_neural",
        "voice_male": VOICE_M, "voice_female": VOICE_F,
        "speaker_cloned": False, "voice_gender_matched": True,
        "n_speakers_with_synth": len(by_spk), "n_speakers_total": 20,
        "speakers_zero_synth": sorted(s for s in ["Baron", "Joni", "Robi"]
                                      if by_spk.get(s, 0) == 0),
    },
    "by_gender_voice": dict(gender),
    "by_voice": dict(by_voice),
    "by_round": dict(by_round),
    "by_split": {s: {"n_synth": by_split.get(s, 0), "split_total": split_total[s],
                     "pct_of_split": round(100 * by_split.get(s, 0) / split_total[s], 4)}
                 for s in ("train", "dev", "test")},
    "by_speaker": dict(sorted(by_spk.items(), key=lambda x: -x[1])),
    "quality": {
        "metric": "Whisper-large-v3 text-similarity to target (0-1)",
        "threshold_accept": 0.70,
        "mean": round(mean(q_all), 4), "min": round(q_all[0], 4),
        "max": round(q_all[-1], 4), "median": round(q_all[len(q_all)//2], 4),
        "n_scored": len(q_all),
        "pass_ge_0.90": sum(1 for x in q_all if x >= 0.90),
        "pass_ge_0.95": sum(1 for x in q_all if x >= 0.95),
        "pass_eq_1.00": sum(1 for x in q_all if x >= 0.9999),
    },
    "by_category": {},
}
for c in sorted(by_cat):
    v = by_cat[c]
    stats["by_category"][c] = {
        "n_synth": v["n"], "category_total": cat_total[c],
        "pct_of_category": round(100 * v["n"] / cat_total[c], 4),
        "pct_of_all_synth": round(100 * v["n"] / n_syn, 2),
        "synthetic_seconds": round(v["dur"], 2),
        "voice_male": v["vM"], "voice_female": v["vF"],
        "rounds": dict(v["rounds"]), "splits": dict(v["splits"]),
        "quality_mean": round(mean(v["q"]), 4) if v["q"] else None,
        "quality_min": round(min(v["q"]), 4) if v["q"] else None,
    }

(HERE / "synthetic_data_stats.json").write_text(
    json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

# ---- per-category CSV ----
with (HERE / "synthetic_per_category.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["category", "n_synth", "category_total", "pct_of_category",
                "pct_of_all_synth", "synth_seconds", "voice_male", "voice_female",
                "n_train", "n_dev", "n_test", "n_v7_initial", "n_v7_residual_fix",
                "quality_mean", "quality_min"])
    for c in sorted(by_cat):
        v = by_cat[c]; d = stats["by_category"][c]
        w.writerow([c, v["n"], cat_total[c], d["pct_of_category"], d["pct_of_all_synth"],
                    round(v["dur"], 2), v["vM"], v["vF"],
                    v["splits"].get("train", 0), v["splits"].get("dev", 0), v["splits"].get("test", 0),
                    v["rounds"].get("v7_initial", 0), v["rounds"].get("v7_residual_fix", 0),
                    d["quality_mean"], d["quality_min"]])

# ============ FIGURES (Data in Brief style) ============
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.size": 9, "pdf.fonttype": 42,
                     "ps.fonttype": 42, "axes.grid": True, "grid.alpha": 0.3})
OK = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
DOUBLE = (7.48, 3.6)
def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / f"{name}.pdf"); fig.savefig(FIG / f"{name}.png", dpi=600)
    plt.close(fig)

cats = sorted(by_cat, key=lambda c: by_cat[c]["n"], reverse=True)
labels = [c.replace("Kalimat_", "") for c in cats]

# S1: stacked synth count per category by voice gender
fig, ax = plt.subplots(figsize=DOUBLE)
m = [by_cat[c]["vM"] for c in cats]; fm = [by_cat[c]["vF"] for c in cats]
ax.bar(labels, m, color=OK[0], label="Ardi (M)")
ax.bar(labels, fm, bottom=m, color=OK[3], label="Gadis (F)")
for i, c in enumerate(cats):
    ax.text(i, by_cat[c]["n"], str(by_cat[c]["n"]), ha="center", va="bottom", fontsize=7)
ax.set_ylabel("synthetic files"); ax.legend(fontsize=8)
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
ax.set_title("S1 Synthetic files per category, by TTS voice gender"); save(fig, "S1_synth_per_category_voice")

# S2: synthetic fraction (%) within each category
fig, ax = plt.subplots(figsize=DOUBLE)
pct = [100 * by_cat[c]["n"] / cat_total[c] for c in cats]
ax.bar(labels, pct, color=OK[1])
for i, p in enumerate(pct):
    ax.text(i, p, f"{p:.2f}%", ha="center", va="bottom", fontsize=6.5)
ax.set_ylabel("synthetic share of category (%)")
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
ax.set_title("S2 Synthetic fraction within each category"); save(fig, "S2_synth_fraction_per_category")

# S3: split distribution of synth per category (stacked)
fig, ax = plt.subplots(figsize=DOUBLE)
tr = [by_cat[c]["splits"].get("train", 0) for c in cats]
dv = [by_cat[c]["splits"].get("dev", 0) for c in cats]
te = [by_cat[c]["splits"].get("test", 0) for c in cats]
ax.bar(labels, tr, color=OK[0], label="train")
ax.bar(labels, dv, bottom=tr, color=OK[1], label="dev")
ax.bar(labels, te, bottom=[a+b for a, b in zip(tr, dv)], color=OK[2], label="test")
ax.set_ylabel("synthetic files"); ax.legend(fontsize=8)
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
ax.set_title("S3 Synthetic-file split distribution per category"); save(fig, "S3_synth_split_per_category")

# S4: quality histogram + per-category mean
fig, (a1, a2) = plt.subplots(1, 2, figsize=DOUBLE)
a1.hist(q_all, bins=20, color=OK[4]); a1.axvline(0.70, color=OK[5], ls="--", lw=1, label="accept ≥0.70")
a1.set_xlabel("Whisper similarity"); a1.set_ylabel("count"); a1.legend(fontsize=7)
a1.set_title(f"(a) quality dist. (μ={mean(q_all):.4f})", fontsize=8)
qmeans = [stats["by_category"][c]["quality_mean"] or 0 for c in cats]
a2.barh(labels[::-1], qmeans[::-1], color=OK[2]); a2.set_xlim(0.95, 1.001)
a2.set_xlabel("mean similarity"); a2.tick_params(labelsize=6.5)
a2.set_title("(b) per-category mean", fontsize=8)
fig.suptitle(f"S4 Synthetic-audio quality (n={len(q_all)}, Whisper-large-v3)", fontsize=10)
save(fig, "S4_synth_quality")

# manifest
with (FIG / "figure_manifest.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["figure", "pdf", "png", "caption"])
    for nm, cap in [("S1_synth_per_category_voice", "Synthetic files per category by TTS voice gender"),
                    ("S2_synth_fraction_per_category", "Synthetic fraction within each category"),
                    ("S3_synth_split_per_category", "Synthetic split distribution per category"),
                    ("S4_synth_quality", "Synthetic-audio Whisper-similarity quality")]:
        w.writerow([nm, f"figures/{nm}.pdf", f"figures/{nm}.png", cap])

# ---- TXT plain report ----
lines = []
ov = stats["overview"]; qd = stats["quality"]
lines.append("SYNTHETIC-DATA REPORT — Indonesian ASR corpus v7 (9-model paper)")
lines.append("=" * 64)
lines.append(f"Source: {stats['source']}  |  dataset_version: {stats['dataset_version']}")
lines.append("")
lines.append("OVERVIEW")
lines.append(f"  Synthetic files       : {ov['n_synthetic']} / {ov['n_corpus']} "
             f"({ov['fraction_corpus_pct']} %)")
lines.append(f"  Synthetic duration    : {ov['synthetic_hours']} h ({ov['synthetic_seconds']} s)")
lines.append(f"  Engine                : {ov['engine']}")
lines.append(f"  Voices (gender-match) : {ov['voice_male']} (M) / {ov['voice_female']} (F)")
lines.append(f"  Speaker-cloned        : {ov['speaker_cloned']}  (TTS only, disclosed)")
lines.append(f"  Speakers with synth   : {ov['n_speakers_with_synth']} / {ov['n_speakers_total']}")
lines.append(f"  Zero-synth speakers   : {', '.join(ov['speakers_zero_synth'])} (clean for test)")
lines.append("")
lines.append("QUALITY (Whisper-large-v3 similarity, accept >= 0.70)")
lines.append(f"  mean {qd['mean']}  median {qd['median']}  min {qd['min']}  max {qd['max']}")
lines.append(f"  pass>=0.90: {qd['pass_ge_0.90']}/{qd['n_scored']}  "
             f"pass>=0.95: {qd['pass_ge_0.95']}/{qd['n_scored']}  "
             f"==1.00: {qd['pass_eq_1.00']}/{qd['n_scored']}")
lines.append("")
lines.append("SYNTHESIS ROUNDS")
for r, n in sorted(by_round.items()): lines.append(f"  {r:18s}: {n}")
lines.append("")
lines.append("PER-SPLIT DISTRIBUTION")
for s in ("train", "dev", "test"):
    d = stats["by_split"][s]
    lines.append(f"  {s:5s}: {d['n_synth']:3d} / {d['split_total']:5d} ({d['pct_of_split']} %)")
lines.append("")
lines.append("PER-CATEGORY DISTRIBUTION")
lines.append(f"  {'category':22s} {'n':>3s} {'%cat':>6s} {'%all':>6s} {'M/F':>7s} "
             f"{'tr/dv/te':>10s} {'qmean':>6s}")
for c in cats:
    d = stats["by_category"][c]; v = by_cat[c]
    mf = f"{v['vM']}/{v['vF']}"
    sp = f"{v['splits'].get('train',0)}/{v['splits'].get('dev',0)}/{v['splits'].get('test',0)}"
    lines.append(f"  {c:22s} {d['n_synth']:3d} {d['pct_of_category']:6.2f} "
                 f"{d['pct_of_all_synth']:6.2f} {mf:>7s} {sp:>10s} "
                 f"{d['quality_mean'] if d['quality_mean'] else 0:6.4f}")
(HERE / "SYNTHETIC_DATA_REPORT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"OK: synth={n_syn} cats={len(by_cat)} figs=4 | wrote JSON/CSV/TXT + figures")
print("\n".join(lines[:12]))

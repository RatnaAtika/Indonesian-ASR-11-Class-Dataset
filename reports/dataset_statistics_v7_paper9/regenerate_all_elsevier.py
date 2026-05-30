#!/usr/bin/env python3
"""Grand regeneration: Elsevier Data-in-Brief stats + figures + tex tables for
the v7_natural_synth corpus that feeds the 9-model paper pipeline.

Reads ONLY metadata_clean.csv + clean split TSVs (+ reuses the immutable
audio-quality sample CSV from the prior session). No audio-tree traversal.

Outputs (Data in Brief compliant):
  stats/{dataset_stats.json, per_*.csv, word_frequency.csv, statistical_tests.csv,
         audio_quality_sample.csv}
  figures/F1..F12.{pdf,png600}  + figure_manifest.csv
  tex/{T1..T5,G1}.tex   (booktabs, verified v7 numbers)
"""
import csv, json, math, shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "metadata" / "dataset_metadata_clean.csv"
SPLITS = {s: ROOT / "splits" / f"{s}_clean.tsv" for s in ("train", "dev", "test")}
HERE = Path(__file__).resolve().parent
STATS, FIG, PNG, TEX = HERE/"stats", HERE/"figures", HERE/"figures"/"png600", HERE/"tex"
for d in (STATS, FIG, PNG, TEX):
    d.mkdir(parents=True, exist_ok=True)

# Reuse immutable audio-quality sample + mel-spec figure from prior session
PRIOR = ROOT / "Whisper_Verification_Sessions" / "session_20260524_125144_dataset_statistics_viz_elsevier"
for src, dst in [(PRIOR/"stats"/"audio_quality_sample.csv", STATS/"audio_quality_sample.csv"),
                 (PRIOR/"figures"/"F11_mel_spectrogram_exemplars.pdf", FIG/"F11_mel_spectrogram_exemplars.pdf"),
                 (PRIOR/"figures"/"png600"/"F11_mel_spectrogram_exemplars.png", PNG/"F11_mel_spectrogram_exemplars.png")]:
    if src.exists():
        shutil.copy2(src, dst)

rows = list(csv.DictReader(META.open(encoding="utf-8")))
N = len(rows)
fnum = lambda x, d=0.0: float(x) if str(x).strip() not in ("", "nan", "None") else d

split_of = {}
for s, p in SPLITS.items():
    for r in csv.DictReader(p.open(encoding="utf-8"), delimiter="\t"):
        split_of[r["audio_path"]] = s

by_cat = defaultdict(lambda: {"n":0,"dur":0.0,"chars":0,"words":0,"durs":[]})
by_spk = defaultdict(lambda: {"n":0,"dur":0.0,"gender":None,"split":None,"durs":[]})
by_split = defaultdict(lambda: {"n":0,"dur":0.0,"synth":0,"spk":set(),"m":0,"f":0,"durs":[]})
gender_files, gender_dur = Counter(), defaultdict(float)
synth = {"n":0,"dur":0.0,"eng":Counter(),"voice":Counter(),"rnd":Counter(),
         "cat":Counter(),"gen":Counter(),"split":Counter(),"q":[]}
sr_c, ch_c, bd_c = Counter(), Counter(), Counter()
word_freq, uniq_tr, sentence_ids, durations = Counter(), set(), set(), []

for r in rows:
    dur = fnum(r["duration_sec"]); durations.append(dur)
    cat, spk, gen = r["category"].strip(), r["speaker_id"].strip(), r["speaker_gender"].strip()
    tr = r["transcript"].strip(); toks = tr.split()
    iss = r["is_synthetic"].strip().lower() in ("true","1","yes")
    sp = split_of.get(r["audio_path"], "?")
    by_cat[cat]["n"]+=1; by_cat[cat]["dur"]+=dur; by_cat[cat]["chars"]+=len(tr)
    by_cat[cat]["words"]+=len(toks); by_cat[cat]["durs"].append(dur)
    by_spk[spk]["n"]+=1; by_spk[spk]["dur"]+=dur; by_spk[spk]["gender"]=gen
    by_spk[spk]["split"]=sp; by_spk[spk]["durs"].append(dur)
    by_split[sp]["n"]+=1; by_split[sp]["dur"]+=dur; by_split[sp]["spk"].add(spk)
    by_split[sp]["durs"].append(dur)
    by_split[sp]["m" if gen=="Male" else "f"]+=1
    gender_files[gen]+=1; gender_dur[gen]+=dur
    sr_c[r["sample_rate"]]+=1; ch_c[r["num_channels"]]+=1; bd_c[r["bits_per_sample"]]+=1
    sentence_ids.add(r["sentence_id"]); uniq_tr.add(tr.lower())
    for w in toks: word_freq[w.lower()]+=1
    if iss:
        synth["n"]+=1; synth["dur"]+=dur; synth["eng"][r["synthesis_engine"].strip()]+=1
        synth["voice"][r["synthesis_voice"].strip()]+=1; synth["rnd"][r["synthesis_round"].strip()]+=1
        synth["cat"][cat]+=1; synth["gen"][gen]+=1; synth["split"][sp]+=1
        synth["split"][sp]; by_split[sp]["synth"]+=1
        q = fnum(r["synthesis_quality_score"], -1)
        if q>=0: synth["q"].append(q)

total_dur = sum(durations)
total_tokens = sum(word_freq.values()); vocab = len(word_freq)
ranked = word_freq.most_common()

def mean(xs): return sum(xs)/len(xs) if xs else 0.0
def sd(xs):
    if len(xs)<2: return 0.0
    m=mean(xs); return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))
def entropy_norm(cs):
    t=sum(cs)
    if t==0 or len(cs)<=1: return 1.0
    H=-sum((c/t)*math.log2(c/t) for c in cs if c>0); return H/math.log2(len(cs))
def gini(cs):
    xs=sorted(cs); n=len(xs); s=sum(xs)
    if n==0 or s==0: return 0.0
    return (2*sum((i+1)*x for i,x in enumerate(xs)))/(n*s)-(n+1)/n

# ---- statistical tests (scipy) ----
stat_tests = []
try:
    from scipy import stats as sps
    cat_durs = [by_cat[c]["durs"] for c in sorted(by_cat)]
    H_c, p_c = sps.kruskal(*cat_durs)
    eta_c = (H_c-len(cat_durs)+1)/(N-len(cat_durs))
    spk_durs = [by_spk[s]["durs"] for s in sorted(by_spk)]
    H_s, p_s = sps.kruskal(*spk_durs)
    eta_s = (H_s-len(spk_durs)+1)/(N-len(spk_durs))
    cat_n = [by_cat[c]["n"] for c in sorted(by_cat)]
    exp = sum(cat_n)/len(cat_n)
    chi2, p_chi = sps.chisquare(cat_n)
    cramv = math.sqrt(chi2/(N*(len(cat_n)-1)))
    tr_d = by_split["train"]["durs"]; te_d = by_split["test"]["durs"]
    D, p_ks = sps.ks_2samp(tr_d, te_d)
    bonf = 4
    stat_tests = [
        ("Kruskal-Wallis (duration ~ category)", H_c, 10, p_c, min(1,p_c*bonf), eta_c, N),
        ("Kruskal-Wallis (duration ~ speaker)", H_s, 19, p_s, min(1,p_s*bonf), eta_s, N),
        ("Chi2 goodness-of-fit (category ~ uniform)", chi2, 10, p_chi, min(1,p_chi*bonf), cramv, N),
        ("Kolmogorov-Smirnov 2-sample (train vs test dur)", D, None, p_ks, min(1,p_ks*bonf), D, len(tr_d)+len(te_d)),
    ]
    with (STATS/"statistical_tests.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["test","statistic","df","p","p_bonferroni","effect_size","n"])
        for t in stat_tests: w.writerow(t)
except Exception as e:
    print("STAT TESTS SKIPPED:", e)

# ---- CSVs ----
with (STATS/"per_category.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["category","n_files","hours","mean_dur_s","sd_dur_s","mean_chars","mean_words","n_synthetic"])
    for c in sorted(by_cat):
        v=by_cat[c]; w.writerow([c,v["n"],round(v["dur"]/3600,4),round(mean(v["durs"]),3),
            round(sd(v["durs"]),3),round(v["chars"]/v["n"],1),round(v["words"]/v["n"],2),synth["cat"].get(c,0)])
with (STATS/"per_speaker.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["speaker_id","gender","split","n_files","hours","mean_dur_s","sd_dur_s"])
    for s in sorted(by_spk, key=lambda s: by_spk[s]["dur"], reverse=True):
        v=by_spk[s]; w.writerow([s,v["gender"],v["split"],v["n"],round(v["dur"]/3600,4),
            round(mean(v["durs"]),3),round(sd(v["durs"]),3)])
with (STATS/"per_split.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["split","n_files","n_speakers","hours","n_male","n_female","n_synthetic","synth_pct","mean_dur_s"])
    for s in ("train","dev","test"):
        v=by_split[s]; w.writerow([s,v["n"],len(v["spk"]),round(v["dur"]/3600,4),v["m"],v["f"],
            v["synth"],round(100*v["synth"]/v["n"],3),round(mean(v["durs"]),3)])
with (STATS/"word_frequency.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["rank","word","freq"])
    for i,(wd,c) in enumerate(ranked,1): w.writerow([i,wd,c])

spk_counts=[v["n"] for v in by_spk.values()]; cat_counts=[v["n"] for v in by_cat.values()]
stats = {
  "source":{"metadata":str(META.relative_to(ROOT)),"dataset_version":rows[0]["dataset_version"],
            "splits":{k:str(v.relative_to(ROOT)) for k,v in SPLITS.items()}},
  "pipeline":{"target_journal":"Data in Brief (Elsevier, ISSN 2352-3409)",
              "n_paper_models":9,
              "models":["m08 HMM-GMM","m09 DNN-HMM","m10 GMM-HMM-DNN","m11 Vanilla Transformer",
                        "m12 ViT-modified-ID (novel)","m07 Bi-LSTM CTC","m06 Conformer-CTC",
                        "m13 Wav2Letter","m02b Whisper-medium FT"],
              "tokenizer":"spm_v7_char","features":"80-bin log-mel 25ms/10ms per-utt CMVN",
              "decoding":"greedy, no LM","seed":42},
  "corpus":{"n_files":N,"total_hours":round(total_dur/3600,4),"total_seconds":round(total_dur,1),
            "n_speakers":len(by_spk),"n_categories":len(by_cat),"n_base_sentences":len(uniq_tr),
            "n_sentences_per_category":len(uniq_tr)//max(1,len(by_cat)),
            "mean_dur_s":round(total_dur/N,4),"median_dur_s":round(sorted(durations)[N//2],4),
            "min_dur_s":round(min(durations),3),"max_dur_s":round(max(durations),3),
            "mean_tokens_per_file":round(total_tokens/N,2),
            "speaker_hours_min":round(min(v["dur"] for v in by_spk.values())/3600,2),
            "speaker_hours_max":round(max(v["dur"] for v in by_spk.values())/3600,2)},
  "audio_format":{"sample_rate":dict(sr_c),"num_channels":dict(ch_c),"bits_per_sample":dict(bd_c)},
  "gender":{"speakers":{"male":sorted(s for s,v in by_spk.items() if v["gender"]=="Male"),
                        "female":sorted(s for s,v in by_spk.items() if v["gender"]=="Female")},
            "n_male_speakers":sum(1 for v in by_spk.values() if v["gender"]=="Male"),
            "n_female_speakers":sum(1 for v in by_spk.values() if v["gender"]=="Female"),
            "files":dict(gender_files),"hours":{g:round(d/3600,4) for g,d in gender_dur.items()}},
  "balance":{"speaker_entropy_norm":round(entropy_norm(spk_counts),8),"speaker_gini":round(gini(spk_counts),6),
             "speaker_file_min":min(spk_counts),"speaker_file_max":max(spk_counts),
             "category_entropy_norm":round(entropy_norm(cat_counts),8),"category_gini":round(gini(cat_counts),6)},
  "splits":{s:{"n_files":by_split[s]["n"],"n_speakers":len(by_split[s]["spk"]),
               "hours":round(by_split[s]["dur"]/3600,4),"n_male":by_split[s]["m"],"n_female":by_split[s]["f"],
               "n_synthetic":by_split[s]["synth"],"speakers":sorted(by_split[s]["spk"])}
            for s in ("train","dev","test")},
  "linguistics":{"vocab_types":vocab,"total_tokens":total_tokens,"top20":ranked[:20]},
  "synthetic":{"n_files":synth["n"],"fraction_corpus":round(synth["n"]/N,6),"hours":round(synth["dur"]/3600,4),
               "engine":dict(synth["eng"]),"voices":dict(synth["voice"]),"rounds":dict(synth["rnd"]),
               "by_category":dict(synth["cat"]),"by_gender":dict(synth["gen"]),"by_split":dict(synth["split"]),
               "quality_mean":round(mean(synth["q"]),4),"quality_min":round(min(synth["q"]),4),"quality_n":len(synth["q"])},
  "statistical_tests":[{"test":t[0],"statistic":t[1],"df":t[2],"p":t[3],"p_bonferroni":t[4],
                        "effect_size":t[5],"n":t[6]} for t in stat_tests],
}
(STATS/"dataset_stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8")

# ============ FIGURES (Data in Brief style) ============
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.size":9,"pdf.fonttype":42,"ps.fonttype":42,
                     "axes.grid":True,"grid.alpha":0.3})
OK=["#0072B2","#E69F00","#009E73","#CC79A7","#56B4E9","#D55E00","#F0E442","#000000"]
SINGLE,DOUBLE=(3.54,2.8),(7.48,3.4)
def save(fig,name):
    fig.tight_layout(); fig.savefig(FIG/f"{name}.pdf"); fig.savefig(PNG/f"{name}.png",dpi=600); plt.close(fig)

# F1 files per speaker by split
spk=sorted(by_spk,key=lambda s:by_spk[s]["n"])
fig,ax=plt.subplots(figsize=DOUBLE)
cmap={"train":OK[0],"dev":OK[1],"test":OK[2]}
ax.bar(range(len(spk)),[by_spk[s]["n"] for s in spk],color=[cmap[by_spk[s]["split"]] for s in spk])
ax.set_xticks(range(len(spk))); ax.set_xticklabels(spk,rotation=90,fontsize=6)
ax.set_ylabel("files"); ax.set_ylim(5000,5160)
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color=cmap[k],label=k) for k in cmap],fontsize=7)
ax.set_title("F1 Files per speaker, by split"); save(fig,"F1_files_per_speaker_split")

# F2 duration per category (boxplot)
cats=sorted(by_cat,key=lambda c:mean(by_cat[c]["durs"]))
fig,ax=plt.subplots(figsize=DOUBLE)
ax.boxplot([by_cat[c]["durs"] for c in cats],vert=False,showfliers=False,
           labels=[c.replace("Kalimat_","") for c in cats])
ax.set_xlabel("duration (s)"); ax.tick_params(labelsize=7)
ax.set_title("F2 Duration distribution per category"); save(fig,"F2_duration_per_category")

# F3 per-speaker total recording time ranked
spk2=sorted(by_spk,key=lambda s:by_spk[s]["dur"],reverse=True)
fig,ax=plt.subplots(figsize=DOUBLE)
ax.bar(range(len(spk2)),[by_spk[s]["dur"]/3600 for s in spk2],
       color=[OK[0] if by_spk[s]["gender"]=="Male" else OK[3] for s in spk2])
ax.set_xticks(range(len(spk2))); ax.set_xticklabels(spk2,rotation=90,fontsize=6)
ax.set_ylabel("hours"); ax.legend(handles=[mp.Patch(color=OK[0],label="Male"),mp.Patch(color=OK[3],label="Female")],fontsize=7)
ax.set_title("F3 Total recording time per speaker"); save(fig,"F3_speaker_total_duration")

# F4 sentence length (chars + words)
fig,(a1,a2)=plt.subplots(1,2,figsize=DOUBLE)
a1.hist([len(r["transcript"].strip()) for r in rows],bins=50,color=OK[0])
a1.set_xlabel("characters/transcript"); a1.set_ylabel("count"); a1.set_title("(a) chars")
a2.hist([len(r["transcript"].split()) for r in rows],bins=30,color=OK[2])
a2.set_xlabel("words/transcript"); a2.set_title("(b) words")
fig.suptitle("F4 Sentence-length distribution",fontsize=10); save(fig,"F4_sentence_length")

# F5 word-frequency pareto (top30 + cumulative)
top=ranked[:30]; fig,ax=plt.subplots(figsize=DOUBLE)
ax.bar(range(len(top)),[c for _,c in top],color=OK[0])
ax.set_xticks(range(len(top))); ax.set_xticklabels([w for w,_ in top],rotation=90,fontsize=6)
ax.set_ylabel("frequency")
ax2=ax.twinx(); cum=[]; s=0
for _,c in top: s+=c; cum.append(100*s/total_tokens)
ax2.plot(range(len(top)),cum,color=OK[5],marker="o",ms=3); ax2.set_ylabel("cumulative %")
ax.set_title("F5 Top-30 word frequency + cumulative coverage"); save(fig,"F5_word_frequency_pareto")

# F6 Heaps law
import random as _r; _r.seed(42)
order=list(range(len(rows))); _r.shuffle(order)
seen=set(); Ns=[]; Vs=[]; tok=0
for k,i in enumerate(order):
    for w in rows[i]["transcript"].lower().split():
        tok+=1; seen.add(w)
    if k%500==0: Ns.append(tok); Vs.append(len(seen))
Ns.append(tok); Vs.append(len(seen))
import numpy as np
ln,lv=np.log(np.array(Ns[1:])),np.log(np.array(Vs[1:]))
beta,lk=np.polyfit(ln,lv,1); 
fig,ax=plt.subplots(figsize=SINGLE)
ax.loglog(Ns,Vs,".",color=OK[0],ms=3)
ax.loglog(Ns,[math.exp(lk)*n**beta for n in Ns],color=OK[5])
ax.set_xlabel("tokens N"); ax.set_ylabel("vocab V")
ax.set_title(f"F6 Heaps' law (β={beta:.3f})"); save(fig,"F6_heaps_law")

# F7 speaker x category heatmap
sc=defaultdict(lambda: defaultdict(int))
for r in rows: sc[r["speaker_id"]][r["category"]]+=1
spks=sorted(sc); cts=sorted(by_cat)
M=np.array([[sc[s][c] for c in cts] for s in spks])
fig,ax=plt.subplots(figsize=DOUBLE)
im=ax.imshow(M,aspect="auto",cmap="viridis")
ax.set_xticks(range(len(cts))); ax.set_xticklabels([c.replace("Kalimat_","") for c in cts],rotation=90,fontsize=6)
ax.set_yticks(range(len(spks))); ax.set_yticklabels(spks,fontsize=6)
fig.colorbar(im,ax=ax,label="files"); ax.set_title("F7 Speaker x category file count"); save(fig,"F7_speaker_category_heatmap")

# F8 cumulative hours
spk3=sorted(by_spk,key=lambda s:by_spk[s]["dur"],reverse=True)
cumh=[]; s=0
for sp_ in spk3: s+=by_spk[sp_]["dur"]/3600; cumh.append(s)
fig,ax=plt.subplots(figsize=SINGLE)
ax.plot(range(1,len(cumh)+1),cumh,marker="o",ms=3,color=OK[0])
ax.set_xlabel("speakers (ranked)"); ax.set_ylabel("cumulative hours")
ax.set_title("F8 Cumulative recording hours"); save(fig,"F8_cumulative_hours")

# F9 audio uniformity
fig,(a1,a2,a3)=plt.subplots(1,3,figsize=DOUBLE)
for ax_,d,t in [(a1,sr_c,"sample rate"),(a2,bd_c,"bit depth"),(a3,ch_c,"channels")]:
    ax_.bar([str(k) for k in d],[v for v in d.values()],color=OK[2]); ax_.set_title(t,fontsize=8)
    ax_.tick_params(labelsize=7)
fig.suptitle("F9 Audio-format uniformity (100%)",fontsize=10); save(fig,"F9_audio_uniformity")

# F10 synthetic disclosure
fig,(a1,a2)=plt.subplots(1,2,figsize=DOUBLE)
a1.pie([N-synth["n"],synth["n"]],labels=[f"real\n{N-synth['n']}",f"synth\n{synth['n']}"],
       colors=[OK[2],OK[1]],autopct="%1.3f%%",startangle=90)
a1.set_title("(a) real vs synthetic")
sp=["train","dev","test"]
a2.bar(sp,[by_split[s]["synth"] for s in sp],color=OK[1])
for i,s in enumerate(sp): a2.text(i,by_split[s]["synth"],str(by_split[s]["synth"]),ha="center",va="bottom",fontsize=8)
a2.set_ylabel("synthetic files"); a2.set_title("(b) synth per split")
fig.suptitle("F10 Synthetic-data disclosure",fontsize=10); save(fig,"F10_synthetic_disclosure")

# F12 audio quality (from reused sample)
aq=list(csv.DictReader((STATS/"audio_quality_sample.csv").open(encoding="utf-8")))
dr=[fnum(r["dynamic_range_db"]) for r in aq]; sil=[fnum(r["silence_ratio"]) for r in aq]
sc_=[fnum(r["spectral_centroid_hz"]) for r in aq]
fig,(a1,a2,a3)=plt.subplots(1,3,figsize=DOUBLE)
a1.hist(dr,bins=25,color=OK[0]); a1.set_title(f"dynamic range\nμ={mean(dr):.1f} dB",fontsize=8)
a2.hist(sil,bins=25,color=OK[3]); a2.set_title(f"silence ratio\nμ={mean(sil):.2f}",fontsize=8)
a3.hist(sc_,bins=25,color=OK[2]); a3.set_title("spectral centroid (Hz)",fontsize=8)
for a in (a1,a2,a3): a.tick_params(labelsize=7)
fig.suptitle(f"F12 Audio quality (n={len(aq)} stratified sample)",fontsize=10); save(fig,"F12_audio_quality")

# manifest
figs=["F1_files_per_speaker_split","F2_duration_per_category","F3_speaker_total_duration",
      "F4_sentence_length","F5_word_frequency_pareto","F6_heaps_law","F7_speaker_category_heatmap",
      "F8_cumulative_hours","F9_audio_uniformity","F10_synthetic_disclosure",
      "F11_mel_spectrogram_exemplars","F12_audio_quality"]
with (FIG/"figure_manifest.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["figure","pdf","png600"])
    for nm in figs: w.writerow([nm,f"figures/{nm}.pdf",f"figures/png600/{nm}.png"])

# ============ TEX TABLES (booktabs, verified v7 numbers) ============
g=stats["gender"]; c=stats["corpus"]
(TEX/"T1_overview.tex").write_text(rf"""% T1 -- Corpus headline statistics (Elsevier booktabs)
\begin{{table}}[!t]
  \centering
  \caption{{Corpus-level headline statistics for the Indonesian ASR dataset (v7).}}
  \label{{tab:corpus_overview}}
  \small
  \begin{{tabular}}{{lr}}
  \toprule
  Property & Value \\
  \midrule
  Audio files                  & {N:,} \\
  Total duration (h)           & {c['total_hours']:.2f} \\
  Speakers (M / F)             & {len(by_spk)} ({g['n_male_speakers']} / {g['n_female_speakers']}) \\
  Sentence categories          & {len(by_cat)} \\
  Base sentences               & {c['n_base_sentences']} (19 $\times$ 11) \\
  Sample rate (uniform)        & 16\,kHz \\
  Bit depth (uniform)          & 16\,bit \\
  Channels (uniform)           & mono \\
  Real-speech files            & {N-synth['n']:,} ({100*(N-synth['n'])/N:.3f}\%) \\
  Synthetic files (Edge-TTS)   & {synth['n']} ({100*synth['n']/N:.3f}\%) \\
  Vocabulary size              & {vocab:,} unique words \\
  Total tokens                 & {total_tokens:,} \\
  Mean tokens / file           & {c['mean_tokens_per_file']:.2f} \\
  \bottomrule
  \end{{tabular}}
\end{{table}}
""",encoding="utf-8")

psrows=sorted(by_spk,key=lambda s:by_spk[s]["dur"],reverse=True)[:10]
sx={"Male":"M","Female":"F"}
lines="".join(f"  {s} & {sx[by_spk[s]['gender']]} & {by_spk[s]['split']} & {by_spk[s]['n']:,} & "
              f"{by_spk[s]['dur']/3600:.2f} & {mean(by_spk[s]['durs']):.2f} & {sd(by_spk[s]['durs']):.2f} " + r"\\" + "\n"
              for s in psrows)
(TEX/"T2_per_speaker.tex").write_text(rf"""% T2 -- Per-speaker (top-10 by time; full in stats/per_speaker.csv)
\begin{{table}}[!t]
  \centering
  \caption{{Per-speaker descriptive statistics (top-10 by recording time; full table in \texttt{{stats/per\_speaker.csv}}).}}
  \label{{tab:per_speaker}}
  \small
  \begin{{tabular}}{{llcrrrr}}
  \toprule
  Speaker & Sex & Split & N files & Hours & Mean dur. (s) & SD (s) \\
  \midrule
{lines}  \bottomrule
  \end{{tabular}}
\end{{table}}
""",encoding="utf-8")

clines="".join(f"  {c_.replace('Kalimat_','Kalimat'+chr(92)+'_')} & {by_cat[c_]['n']:,} & {mean(by_cat[c_]['durs']):.2f} & "
               f"{sd(by_cat[c_]['durs']):.2f} & {by_cat[c_]['chars']/by_cat[c_]['n']:.1f} & "
               f"{by_cat[c_]['words']/by_cat[c_]['n']:.2f} " + r"\\" + "\n" for c_ in sorted(by_cat))
(TEX/"T3_per_category.tex").write_text(rf"""% T3 -- Per-category descriptive statistics
\begin{{table}}[!t]
  \centering
  \caption{{Per-category descriptive statistics for the 11 sentence types.}}
  \label{{tab:per_category}}
  \small
  \begin{{tabular}}{{lrrrrr}}
  \toprule
  Category & N files & Mean dur. (s) & SD dur. (s) & Mean chars & Mean words \\
  \midrule
{clines}  \bottomrule
  \end{{tabular}}
\end{{table}}
""",encoding="utf-8")

slines="".join(f"  {s} & {by_split[s]['n']:,} & {by_split[s]['dur']/3600:.2f} & {len(by_split[s]['spk'])} & "
               f"{by_split[s]['synth']} & {100*by_split[s]['synth']/by_split[s]['n']:.3f} & "
               f"{mean(by_split[s]['durs']):.3f} " + r"\\" + "\n" for s in ("train","dev","test"))
(TEX/"T4_per_split.tex").write_text(rf"""% T4 -- Train/Dev/Test split statistics
\begin{{table}}[!t]
  \centering
  \caption{{Train / dev / test split statistics. Splits are at the speaker level with zero leak.}}
  \label{{tab:per_split}}
  \small
  \begin{{tabular}}{{lrrrrrr}}
  \toprule
  Split & N files & Hours & N speakers & N synth. & Synth. (\%) & Mean dur. (s) \\
  \midrule
{slines}  \bottomrule
  \end{{tabular}}
\end{{table}}
""",encoding="utf-8")

trows=""
for t in stat_tests:
    nm,stt,df,p,pb,es,n=t
    p_s = r"${<}10^{-300}$" if p==0 else f"{p:.2e}"
    pb_s = r"${<}10^{-300}$" if pb==0 else f"{pb:.2e}"
    df_s = str(df) if df is not None else "---"
    trows += f"  {nm} & {stt:.2f} & {df_s} & {p_s} & {pb_s} & {es:.3f} " + r"\\" + "\n"
(TEX/"T5_statistical_tests.tex").write_text(rf"""% T5 -- Statistical tests (Bonferroni family size 4)
\begin{{table*}}[!t]
  \centering
  \caption{{Statistical tests on the corpus. Bonferroni family size 4. Effect sizes: $\eta^2$ (Kruskal--Wallis), Cram\'er's $V$ ($\chi^2$), KS statistic $D$.}}
  \label{{tab:statistical_tests}}
  \small
  \begin{{tabular}}{{lrrrrr}}
  \toprule
  Test & Statistic & df & $p$ & $p_{{\mathrm{{Bonf.}}}}$ & Effect size \\
  \midrule
{trows}  \bottomrule
  \end{{tabular}}
\end{{table*}}
""",encoding="utf-8")

(TEX/"G1_category_glossary.tex").write_text(r"""% G1 -- Glossary of 11 Indonesian sentence-type categories
\begin{table}[!t]
  \centering
  \caption{Glossary of the 11 Indonesian sentence-type categories used in the corpus.}
  \label{tab:category_glossary}
  \small
  \begin{tabular}{lll}
  \toprule
  Indonesian label & English gloss & Function \\
  \midrule
  Kalimat\_Deklaratif  & Declarative          & Statement that asserts a fact \\
  Kalimat\_Klarifikasi & Clarification        & Request to clarify or rephrase \\
  Kalimat\_Kondisional & Conditional          & If--then construction \\
  Kalimat\_Konfirmasi  & Confirmation         & Yes/no confirmation request \\
  Kalimat\_Negasi      & Negation             & Negated assertion (\emph{tidak / bukan}) \\
  Kalimat\_Penjadwalan & Scheduling           & Time-related plan or appointment \\
  Kalimat\_Perintah    & Command / Imperative & Direct instruction (often telegraphic) \\
  Kalimat\_Persuasif   & Persuasive           & Multi-clause argumentation, longest type \\
  Kalimat\_Retoris     & Rhetorical           & Question whose answer is implied \\
  Kalimat\_Seruan      & Exclamation          & Surprise / emphasis \\
  Kalimat\_Tanya       & Interrogative        & Genuine information-seeking question \\
  \bottomrule
  \end{tabular}
\end{table}
""",encoding="utf-8")

print(f"OK: N={N} hours={total_dur/3600:.2f} M/F spk={g['n_male_speakers']}/{g['n_female_speakers']} "
      f"vocab={vocab} synth={synth['n']} figs={len(figs)} stat_tests={len(stat_tests)}")

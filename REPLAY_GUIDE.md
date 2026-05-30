# REPLAY_GUIDE — Re-plot Training History Without Retraining

> Setiap model menyimpan **history + log + meta lengkap** sehingga grafik dapat
> di-replot kapanpun, dalam format jurnal apapun, **tanpa retrain**. Cocok ketika
> jurnal target meminta gaya plotting tertentu (IEEE, ACM, Springer LNCS,
> Elsevier) atau saat menulis thesis.

## Yang disimpan setiap model setelah training

Setiap `runs/run_<smoke|full>_<YYYYMMDD>/` berisi:

```
runs/run_full_20260601/
├── config.json              ← CLI args lengkap
├── meta.json                ← snapshot environment (Python, torch, CUDA, libs)
├── history.json             ← per-epoch metrics (LOSS, ACC, WER, CER, LR, GPU, throughput, time)
├── log.txt                  ← rich human-readable training log
├── predictions/             ← sample PRED/LABEL per epoch
│   ├── sample_preds_e001.txt
│   ├── sample_preds_e002.txt
│   └── ...
├── plots/                   ← plot default style (saat training)
│   ├── loss.png
│   ├── wer_cer.png
│   ├── lr.png
│   └── gpu_mb.png
├── checkpoints/             ← per-epoch model state
└── report.md                ← auto-generated summary
```

**Yang penting untuk re-plot adalah hanya `history.json`.** Semua field metrik
ada di sana per epoch — tidak perlu data training, model, atau checkpoint untuk
replot.

## history.json schema

Setiap entri (1 per epoch) berisi:

```json
{
  "epoch": 187,
  "timestamp": "2026-05-24T13:17:31",
  "train_loss": 1.601781,
  "val_loss": 0.831560,
  "train_acc": 0.807958,
  "val_acc": 0.866993,
  "wer": 0.236174,
  "cer": 0.133007,
  "mer": 0.230456,
  "wil": 0.398122,
  "time_sec": 387.0,
  "time_str": "00:06:27",
  "total_elapsed_sec": 89674.0,
  "total_elapsed_str": "24:54:34",
  "gpu_mb": 309.0,
  "lr": 0.0000007813,
  "throughput_samples_per_sec": 213.25
}
```

Berlaku untuk **14 model FT** (modern + conventional). Zero-shot baselines hanya
1 epoch entry karena tidak ada training.

## meta.json — reproducibility snapshot

```json
{
  "model_id": "openai/whisper-small",
  "family": "Whisper",
  "era": "2022",
  "config": {"epochs": 3, "batch_size": 4, "lr": 1e-5, ...},
  "dataset_info": {"splits_dir": "...", "audio_root": "..."},
  "environment": {
    "python": "3.10.18",
    "torch_version": "2.10.0+cu128",
    "transformers_version": "4.57.6",
    "cuda_device": "NVIDIA GeForce RTX 4060 Laptop GPU",
    "cuda_version": "12.8",
    "timestamp": "2026-05-24T15:06:01"
  },
  "replay": {
    "history_path": "runs/run_full_20260601/history.json",
    "log_path": "runs/run_full_20260601/log.txt",
    "available_styles": ["ieee", "acm", "springer", "elsevier", "thesis", "plain"],
    "available_formats": ["png", "pdf", "svg", "eps"],
    "replot_command": "python3 -m common.journal_plotting --run-dir <this_dir> --style ieee --formats png pdf"
  }
}
```

## 6 journal-style preset built-in

| Style | Konteks | Figsize (1-col) | Font | Default DPI |
|-------|---------|-----------------|------|-------------|
| `ieee` | IEEE / IEEE TASLP / ICASSP | 3.487″ × 2.6″ | sans-serif, BW-friendly | 600 |
| `acm` | ACM SIGCHI / SIGGRAPH / TOG | 3.33″ × 2.5″ | serif, color-friendly | 600 |
| `springer` | Springer LNCS / Interspeech | 4.6″ × 3.0″ | serif | 600 |
| `elsevier` | Elsevier (Speech Communication, Comput. Speech & Lang.) | 3.5″ × 2.7″ | sans-serif | 600 |
| `thesis` | Thesis / dissertation full-page | 6.5″ × 4.0″ | serif | 300 |
| `plain` | Default matplotlib | 8.0″ × 5.0″ | DejaVu Sans | 300 |

Lihat dengan: `python3 training/common/journal_plotting.py --list-styles`

## 4 cara melakukan re-plot

### Cara 1 — Re-plot satu model (paling simpel)

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu
cd "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA"

python3 training/common/journal_plotting.py \
  --run-dir training/m02_whisper_small/runs/run_full_20260601 \
  --style ieee \
  --formats png pdf svg
```

Output: `runs/run_full_20260601/plots_ieee/` berisi:
- `loss.{png,pdf,svg}`
- `acc.{png,pdf,svg}`
- `wer_cer.{png,pdf,svg}`
- `lr.{png,pdf,svg}`
- `gpu_mb.{png,pdf,svg}`
- `throughput.{png,pdf,svg}`
- `combined_4panel.{png,pdf,svg}` (paper Figure 1: 4-panel summary)
- `_replay_meta.json` (apa yang di-replot)

### Cara 2 — Re-plot semua 14 model dengan satu perintah

```bash
# Re-plot semua run_full_* dalam style IEEE, output ke per-run folder
python3 replot_all.py --style ieee --pattern "run_full*"

# Atau aggregate ke satu folder paper
python3 replot_all.py --style ieee --pattern "run_full*" \
  --out-root reports/paper_figures_ieee
```

Output `reports/paper_figures_ieee/`:
```
reports/paper_figures_ieee/
├── _replot_manifest.json
├── m01_whisper_tiny/
│   └── run_full_20260601/
│       ├── loss.{png,pdf}
│       ├── wer_cer.{png,pdf}
│       └── ... (7 plots × 2 formats)
├── m02_whisper_small/
│   └── run_full_20260601/...
... (semua 14 model)
```

### Cara 3 — Multi-model overlay (paper Figure 2)

```bash
# Bandingkan 4 model di 4 metric (loss, acc, wer, cer)
python3 replot_compare.py \
  --runs training/m02_whisper_small/runs/run_full_20260601 \
         training_conventional/m11_vanilla_transformer/runs/run_full_20260601 \
         training_conventional/m12_vit_modified/runs/run_full_20260601 \
         training_conventional/m13_wav2letter_cnn/runs/run_full_20260601 \
  --labels "Whisper-small ★" "Vanilla TF" "ViT-modified-ID ★" "Wav2Letter" \
  --metrics wer cer train_loss val_loss \
  --style ieee --formats png pdf \
  --out reports/paper_figures_ieee/figure2_compare.png \
  --title "Training-curve comparison on Indonesian v7"

# Atau auto-discover semua run_full_*
python3 replot_compare.py --auto-discover --pattern "run_full*" \
  --metrics wer cer --style thesis \
  --out reports/all14_compare_thesis.pdf
```

### Cara 4 — Semua 6 style sekaligus (1 perintah, batch loop)

```bash
for STYLE in ieee acm springer elsevier thesis plain; do
  python3 replot_all.py --style $STYLE --pattern "run_full*" \
    --out-root reports/paper_figures_$STYLE
done
```

Hasil: 6 sub-folder `reports/paper_figures_{ieee,acm,springer,elsevier,thesis,plain}/`
masing-masing berisi 14 model × 7 plot × 2 format. Total ~84 file per style,
~500 file total.

## Verifikasi yang sudah berjalan (smoke runs)

| Style | File output (1 model) | Total size |
|-------|---------------------:|-----------:|
| `ieee` | 15 files | 872 KB |
| `acm` | 15 files | 944 KB |
| `springer` | 15 files | 992 KB |
| `elsevier` | 15 files | 952 KB |
| `thesis` | 15 files | 664 KB |
| `plain` | 15 files | 644 KB |

Replot full 6 style untuk 1 model: ~17 detik. Untuk 14 model × 6 style: ~25 menit.

## Tips untuk paper submission

1. **Vector format (PDF / SVG)** untuk paper — scale tanpa pixelation. PNG hanya
   untuk preview / draft.
2. **`combined_4panel.{pdf}`** adalah kandidat **Figure 1** yang ringkas (4
   sub-plot: loss, acc, WER+CER, LR).
3. **`replot_compare.py` overlay** adalah kandidat **Figure 2** (training-curve
   per arsitektur).
4. **Aggregate report** (`reports/all_models_full/`) sudah punya:
   - `wer_bar_all17.png` (paper Figure 3 candidate)
   - `wer_vs_params.png` (paper Figure 4 candidate)
   - `era_timeline.png` (paper Figure 5 candidate)
   - `family_summary.png`
   - `paper_table.tex` (Table 1)
5. **Per-style consistency**: gunakan style yang sama untuk semua figure di
   paper. Tidak campur IEEE + Elsevier dalam satu manuscript.

## Custom style (advanced)

Jika jurnal target tidak ada di preset, edit `STYLES` dict di
`training/common/journal_plotting.py`. Contoh add `nature`:

```python
STYLES["nature"] = {
    "name": "Nature single-col",
    "rc": {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial"],
        "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7,
        "lines.linewidth": 1.0, "savefig.dpi": 600,
    },
    "figsize": (2.95, 2.2),  # Nature 1-column = 89mm
    "figsize_double": (6.0, 2.5),
    "linestyles": ["-", "--", "-.", ":"],
    "colors": ["#000000", "#444444", "#888888"],
}
```

Lalu sync ke `training_conventional/common/journal_plotting.py` (atau import
dari satu lokasi). Setelah itu `--style nature` langsung tersedia.

## Restore / migrate

Jika folder run dipindahkan ke disk lain:
1. Pastikan `history.json`, `meta.json`, `log.txt`, `config.json`,
   `predictions/` ikut terbawa
2. Re-plot tetap berjalan tanpa training data atau checkpoint:
   ```bash
   python3 training/common/journal_plotting.py \
     --run-dir /new/path/to/run_full_20260601 \
     --style ieee
   ```

## Apa yang TIDAK perlu untuk re-plot

- ❌ Audio dataset (.wav files, .pkl features)
- ❌ Model checkpoints (.pt / safetensors)
- ❌ GPU
- ❌ Internet (HF model downloads)
- ❌ Original training code / config

Yang dibutuhkan **hanya**: `history.json` (≤ 200 KB per model bahkan untuk full run).
Aman untuk di-archive ke Git LFS, Google Drive, atau cloud storage.

## Workflow lengkap untuk paper

```bash
# 0. Training selesai di terminal terpisah (lihat RUN_GUIDE.md)
#    Setiap model menghasilkan runs/run_full_20260601/{history,meta,log,plots,...}

# 1. Aggregate semua results untuk Tabel 1
python3 aggregate_all_models.py
# → reports/all_models_full/{paper_table.tex, comparison.md, plots, summary.json}

# 2. Re-plot per-model figures dalam style jurnal target (pilih satu)
python3 replot_all.py --style ieee --pattern "run_full*" \
  --out-root reports/paper_figures_ieee --formats pdf png

# 3. Multi-model overlay untuk Figure 2 (training curves comparison)
python3 replot_compare.py --auto-discover \
  --metrics wer cer --style ieee --formats pdf \
  --out reports/paper_figures_ieee/figure2_overlay_wer_cer.pdf

# 4. (opsional) Re-plot dalam style alternatif (untuk co-author preference)
for S in acm springer thesis; do
  python3 replot_all.py --style $S --pattern "run_full*" \
    --out-root reports/paper_figures_$S --formats pdf
done

# 5. Submit ke jurnal pakai folder reports/paper_figures_<style>/
```

Selesai. Setiap kali pembimbing minta gaya beda, cukup jalankan ulang langkah
2 — tidak perlu retrain.

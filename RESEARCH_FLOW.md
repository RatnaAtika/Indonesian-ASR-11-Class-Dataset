# RESEARCH FLOW — Paper_Datatset_SOTA

Dokumen ini adalah peta jalan riset khusus untuk sub-proyek **`Paper_Datatset_SOTA`** dengan target publikasi paper ilmiah (jurnal SINTA / IEEE / NeurIPS Datasets & Benchmarks Track).

> Lingkup: hanya folder `Paper_Datatset_SOTA/`. Aset di luar folder ini (mis. `baselines/`, `Clean_Training/`, `bilstm_asr/`, `kaldi_tdnn_hmm_global/`) **tidak** termasuk dan boleh dirujuk hanya sebagai *related work* internal.

---

## 0. Snapshot status (yang sudah ada)

| Aset | Lokasi | Status |
|------|--------|--------|
| Audio sumber 11 kategori × 20 speaker × ~25 take × 20 utt | `Dataset_Ori/` | mentah, 110 000 WAV |
| Build pipeline (audit + filter ID + balanced 19) | `process_paper_dataset_sota.py` | ✅ tervalidasi struktur |
| Dataset balanced final | `Processed_Balanced19_v3/Dataset_Balanced19/` | ✅ 11 kat × 20 spk × 25 take × 19 utt = 104 500 WAV |
| Transkrip kanonik 11 kategori | `Transkrip_ASR_Jurnal_Dataset/*.txt` | ✅ format `ID|kalimat`, satu ID di-drop per kategori |
| Verifikasi konten via Whisper-large-v3 | `verify_paper_dataset_sota_whisper.py` | ✅ run terbaik = `Whisper_Verification/run_20260403_221557` |
| Hasil verifikasi terakhir | `whisper_match_details.csv` (45 MB) | 99.78 % best-id-match, 99.32 % pass threshold (0.75), 465 likely_mismatch (0.44 %) |
| Analisis mismatch | `analyze_whisper_likely_mismatches.py`, `Analyze Whisper Mismatch.md` | ✅ pola ID-shift / boundary terdokumentasi |
| Draft naratif positioning | `Publikasi Dataset Audio ASR Terbatas_… .pdf/.docx` | ✅ outline (metadata, etika, SOTA survey, desain eksperimen) |

**Yang belum ada (gap menuju paper SOTA):**

1. **Metadata pusat** (CSV/JSON) sesuai *Datasheets for Datasets* (Gebru et al., 2018).
2. **Datasheet** lengkap (motivation, composition, collection, recommended uses, distribution, maintenance).
3. **Split resmi** train/val/test yang **speaker-disjoint** (mencegah kebocoran identitas).
4. **Baseline benchmark** terstandar (Whisper {tiny, base, small, medium, large-v3}, MMS, wav2vec2-XLS-R, Indonesian-wav2vec2; zero-shot vs fine-tuned).
5. **Ablation** (efek 11 kategori, efek per-speaker, efek panjang ujaran).
6. **Lisensi & informed-consent artefak** (LICENSE, CONSENT_FORM, Mintarsih et al. style).
7. **Reproducibility package** (Hugging Face Datasets loader script, environment lock, seed).
8. **Manuscript LaTeX** (Overleaf-ready, kelas IEEE / NeurIPS Datasets).

---

## 1. Karakter dataset (one-pager)

| Atribut | Nilai |
|---------|-------|
| Bahasa | Bahasa Indonesia |
| Domain | Sentence-type — *terbatas* (limited-vocabulary, tetapi *sentence-level*, bukan *word-level* seperti Speech Commands) |
| Kategori | 11 (Deklaratif, Klarifikasi, Kondisional, Konfirmasi, Negasi, Penjadwalan, Perintah, Persuasif, Retoris, Seruan, Tanya) |
| Speaker | 20 (Afgan, Ammar, Amri, Anggi, Atika, Baron, Bey, Elisa, Erlin, Fajar, Fito, Harry, Indah, Joni, Muhaimin, Nanda, Pram, Risky, Robi, Uly) |
| Take per speaker × kategori | 25 |
| Utterance per take | 19 (setelah 1 ID dibuang per kategori karena duplikat) |
| Total WAV | 104 500 |
| Format | WAV (perlu audit konsisten 16 kHz, mono, 16-bit) |
| Format nama | `{respondent}/{respondent}_{kategori}_take{N}/{ID:02d}.wav` |
| Nominal SOTA verifikasi | Whisper-large-v3 ID4 indo, similarity normalised SequenceMatcher |

Diferensiasi terhadap dataset publik:

- **LibriSpeech** = English read speech, 1 000 h, lisensi CC-BY-4.0.
- **Mozilla Common Voice** = multilingual *crowdsourced*, lisensi CC-0; data Indonesia kecil & noisy.
- **Speech Commands** = English, *word-level*, 35 kelas.
- **Dataset ini** = Indonesian, *sentence-level*, **type-of-sentence taxonomy** (pragmatic-functional) yang belum pernah dirilis untuk Bahasa Indonesia.

Klaim kebaruan paper:

> "First publicly-released Indonesian sentence-level limited-vocabulary speech corpus stratified by 11 pragmatic sentence types, with reproducible balanced split, content-level Whisper-large-v3 verification, and zero-shot + fine-tuned SOTA baselines."

---

## 2. Skill stack yang sudah terpasang

`scripts/bootstrap.sh --profile academic` sudah dijalankan → 12 skill terpasang di `.agents/skills/`:

```
academic-research-suite       ← pipeline riset → tulis → review → revisi → finalize
research-paper-writing        ← panduan section-by-section ML/NLP paper (Peng Sida)
autoresearch-suite            ← loop autonomous modify→verify→keep/discard
superpowers-suite             ← brainstorm / writing-plans / TDD / verification-before-completion
notebook-authoring            ← .ipynb terstruktur untuk eksperimen reproducible
pdf-toolkit                   ← ekstraksi/redaksi/sign untuk PDF rujukan & manuscript
media-pipeline                ← TTS/STT multi-provider (cross-check Whisper vs MMS vs AssemblyAI)
github-delivery               ← commit, push, PR, CI workflow
agent-harness-compatibility   ← bridging multi-harness
model-provider-config         ← capability flags untuk routing model
skill-authoring               ← scaffold skill khusus jika muncul kebutuhan baru
portable-project-adapter      ← jaga semua skill agar adaptif ke konteks repo ini
```

Konfigurasi pra-flight: `Paper_Datatset_SOTA/.skills-config.yaml` (`mode: harness-managed`).
Decision report: `.agents/skills/.install-report.yaml` & `.conflicts-report.yaml`.

---

## 3. Research flow — 7 fase menuju paper

Setiap fase punya: (a) **input**, (b) **skill yang dipanggil**, (c) **output artefak konkret**, (d) **gate kelar**.

### Fase 1 — Konsolidasi dataset & metadata (1–2 hari)

| | |
|---|---|
| Input | `Processed_Balanced19_v3/Dataset_Balanced19/` + transkrip + Whisper run terbaru |
| Skill | `superpowers-suite` (writing-plans, verification-before-completion), `notebook-authoring` |
| Output | `metadata/dataset_metadata.csv` (kolom: `audio_path, speaker_id, gender, age_group, category, sentence_id, transcript, take_number, duration_sec, sample_rate, num_channels, bit_depth, snr_db, whisper_pass`) · `metadata/datasheet.md` (Datasheets-for-Datasets template) · `metadata/audio_audit.json` |
| Gate | 100 % WAV punya baris CSV; semua kolom numerik valid; SHA-256 checksum tiap WAV tersimpan |

> Catatan implementasi: tambah skrip `build_metadata_csv.py` yang membaca seluruh `Dataset_Balanced19`, hitung durasi via `soundfile`, SNR via `librosa.feature.rms`, verifikasi 16 kHz mono 16-bit.

### Fase 2 — Splitting speaker-disjoint + sanity audit (0.5 hari)

| | |
|---|---|
| Input | metadata CSV |
| Skill | `superpowers-suite` (test-driven-development), `autoresearch-suite` (sanity loop) |
| Output | `splits/train.tsv` · `splits/val.tsv` · `splits/test.tsv` (rasio 14 / 3 / 3 speaker; **TIDAK BOLEH** ada speaker yang muncul di >1 split) · `splits/split_report.md` |
| Gate | `pytest tests/test_splits.py` lulus: (i) speaker-disjoint, (ii) tiap split punya semua 11 kategori, (iii) leakage check via filename hash |

### Fase 3 — Baseline benchmark zero-shot (1 hari, GPU-bound)

Kandidat model (HF Transformers, evaluasi `transcribe` + `lang=id`):

- `openai/whisper-tiny`, `…-base`, `…-small`, `…-medium`, `…-large-v3`
- `openai/whisper-large-v3-turbo`
- `facebook/mms-1b-all` (lang code `ind`)
- `facebook/wav2vec2-xls-r-300m` (CTC; perlu LM-decoder Indonesia)
- `cahya/wav2vec2-large-xlsr-indonesian` (community fine-tuned)

| | |
|---|---|
| Input | `splits/test.tsv` |
| Skill | `autoresearch-suite` (loop modify→verify), `notebook-authoring` |
| Output | `benchmarks/zeroshot/{model}/predictions.tsv` · `benchmarks/zeroshot/results.csv` (kolom: `model, wer, cer, mer, wil, rtfx, vram_peak`) · `benchmarks/zeroshot/per_category_wer.csv` · `benchmarks/zeroshot/per_speaker_wer.csv` |
| Gate | Hasil reproducible: `seed=42`, ffmpeg/torchaudio versi pinned; CI script `make bench-zeroshot` selesai tanpa error |

> Praktis: `verify_paper_dataset_sota_whisper.py` sudah jadi prototip — generalisasi menjadi `bench/run_benchmark.py --model <id>` dan ukur **WER/CER** pakai `evaluate.load("wer")`, bukan SequenceMatcher similarity.

### Fase 4 — Fine-tune SOTA + ablasi (3–5 hari, GPU-bound)

| | |
|---|---|
| Input | `splits/train.tsv` + `val.tsv` |
| Skill | `autoresearch-suite` (kalau metric WER turun → keep, kalau naik → discard), `superpowers-suite` (TDD test pipeline) |
| Output | Checkpoint Hugging Face (`models/whisper-small-id-finetuned/`, `models/wav2vec2-xls-r-300m-id-finetuned/`) · `benchmarks/finetuned/results.csv` · `ablations/{kategori_drop,length_bin,speaker_dropout}.csv` · grafik WER vs jumlah jam pelatihan |
| Gate | Fine-tuned ≥ 10 % relative WER reduction vs zero-shot pada val split, dan tidak overfit (val/test ratio ≤ 1.05) |

> Knob ablation: (i) train tanpa kategori X (uji generalisasi pragmatik), (ii) train hanya 10/14 speaker, (iii) train dengan augment pitch/noise/RIR.

### Fase 5 — Etika, lisensi, anonymisasi (0.5 hari)

| | |
|---|---|
| Input | nama speaker (saat ini = nama panggilan, perlu di-pseudonymize) |
| Skill | `pdf-toolkit` (redaksi PDF consent form), `superpowers-suite` (verification-before-completion) |
| Output | `LICENSE` (CC-BY 4.0 default; opsional CC-BY-NC-SA 4.0 jika consent membatasi) · `CONSENT_FORM.md` (template, ditandatangani peserta) · `metadata/anonymization_map.csv` (real → `SPK01..SPK20`, **disimpan terenkripsi, tidak dirilis**) · `ETHICS.md` (datasheet bagian *Composition* + *Collection* + *Distribution*) |
| Gate | Tidak ada nama asli muncul di rilisan publik; informed consent tercatat per speaker; opsi withdraw tersedia (kontak email) |

### Fase 6 — Distribusi & reproducibility (1 hari)

| | |
|---|---|
| Input | dataset final + metadata + benchmark |
| Skill | `notebook-authoring`, `github-delivery`, `media-pipeline` (cross-check transkrip akhir) |
| Output | Hugging Face Datasets loader script `datasets/paper_dataset_sota.py` (mengikuti template `audiofolder` atau `LegacyMetadataConfig`) · `README_HF.md` (dataset card resmi) · `Dockerfile` + `environment.yml` (conda `torch-gpu`) · GitHub Actions CI: lint + bench-smoke (≤ 50 file) |
| Gate | `datasets.load_dataset("RatnaAtika/paper_dataset_sota", "balanced19_test")` sukses; CI hijau |

### Fase 7 — Manuscript & submission (5–10 hari)

Outline mengikuti `research-paper-writing` skill (Peng Sida):

1. **Abstract** (4 kalimat: motivation · gap · contribution · headline result)
2. **Introduction** (kondisi ASR Indonesia, gap dataset *sentence-type*, kontribusi: dataset + benchmark + analysis)
3. **Related Work** (LibriSpeech, Common Voice, Speech Commands, MMS, Whisper-Indo, dataset Bahasa Indonesia eksisting: TITML-IDN, INDOspeech, Magic Data)
4. **Dataset** (collection protocol, taxonomy 11 kategori, statistik, datasheet)
5. **Verification** (Whisper-large-v3 audit pipeline → 99.32 % pass; analisis 465 likely-mismatch)
6. **Benchmarks** (zero-shot tabel + fine-tuned tabel + per-category heatmap + RTFx vs VRAM scatter)
7. **Ablation & Analysis** (kategori-drop, speaker-disjoint vs random, augment)
8. **Limitations** (20 speaker = small; tidak balanced gender umum; domain Palembang)
9. **Ethical Considerations** (consent, license, withdrawal)
10. **Conclusion**

| | |
|---|---|
| Skill | `academic-research-suite` (research → write → review), `research-paper-writing` (per-section), `autoresearch-suite` (claim-evidence checker), `pdf-toolkit` (compile/redact) |
| Output | `manuscript/main.tex` + `manuscript/references.bib` + figures + Overleaf project · cover-letter · supplementary `appendix.pdf` |
| Gate | Internal peer-review (gunakan `academic-paper-reviewer`) → semua *major* feedback ditutup → submit ke venue |

---

## 4. Kandidat venue (urut prioritas)

| Tier | Venue | Track | Deadline tipikal | Cocok karena |
|------|-------|-------|------------------|--------------|
| A | **NeurIPS Datasets & Benchmarks** | Datasets paper | Mei (abstract) / Juni (paper) | Format & ekspektasi sangat dekat dengan dataset paper kamu |
| A | **LREC-COLING** | Resource paper | Oktober | Pure resource paper, low-resource Indonesian welcome |
| B | **INTERSPEECH** | Special session “Low-resource ASR” | Maret | Audio-centric, speech community fit |
| B | **ICASSP** | Speech – ASR | September | Engineering-heavy benchmark fit |
| B | **IEEE Access** (jurnal) | Open-access ASR / dataset | Rolling | Cepat publish, OA, IF ~3.4 |
| C | **JOIV / IJEECS / IJACSA** (jurnal nasional Indonesia, SINTA-1/2 atau Q3-Q4 Scopus) | Dataset paper | Rolling | Backup cepat untuk syarat lulus |

Rekomendasi: kunci dulu di **IEEE Access** (revision cycle pendek) atau **LREC-COLING 2026** (deadline Oktober — paling realistis dengan timeline 7 fase di atas).

---

## 5. Repo layout target

```
Paper_Datatset_SOTA/
├── .agents/skills/                ← 12 skill terpasang (sudah ✅)
├── .skills-config.yaml            ← config harness/router (sudah ✅)
├── RESEARCH_FLOW.md               ← dokumen ini
├── README.md                      ← dataset + benchmark overview
├── LICENSE
├── CONSENT_FORM.md
├── ETHICS.md
├── Dataset_Ori/                   ← raw, JANGAN dirilis (sumber kebenaran)
├── Processed_Balanced19_v3/       ← release-ready audio (sudah ✅)
│   └── Dataset_Balanced19/...
├── Transkrip_ASR_Jurnal_Dataset/  ← canonical text (sudah ✅)
├── metadata/                      ← BARU
│   ├── dataset_metadata.csv
│   ├── datasheet.md
│   ├── audio_audit.json
│   └── anonymization_map.csv      ← terenkripsi, .gitignored
├── splits/                        ← BARU
│   ├── train.tsv  val.tsv  test.tsv
│   └── split_report.md
├── benchmarks/                    ← BARU
│   ├── zeroshot/{model_id}/...
│   ├── finetuned/{model_id}/...
│   └── results.csv
├── ablations/                     ← BARU
├── models/                        ← BARU (HF checkpoint)
├── notebooks/                     ← BARU (.ipynb reproducible)
├── bench/                         ← BARU (run_benchmark.py, etc.)
├── scripts/                       ← migrate process_paper_dataset_sota.py + verify_*.py + analyze_*.py
├── manuscript/                    ← BARU (LaTeX, figures)
├── Whisper_Verification/          ← log historis audit (sudah ✅)
└── tests/                         ← BARU (pytest split-leakage, audio-format, metadata schema)
```

---

## 6. Aksi langsung (next 24 jam)

Eksekusi berurutan, tiap langkah punya verifikasi sendiri (`superpowers-suite/verification-before-completion`):

1. **Build metadata CSV** — tulis `bench/build_metadata_csv.py`, jalankan, hasil `metadata/dataset_metadata.csv` (104 500 baris).
2. **Audit format audio** — pastikan semua 16 kHz mono 16-bit; tulis WARN ke `metadata/audio_audit.json`.
3. **Buat split speaker-disjoint** — `bench/build_splits.py --train 14 --val 3 --test 3 --seed 42`. Komit `splits/`.
4. **Tulis test pytest** — `tests/test_splits.py` (no leakage), `tests/test_metadata.py` (schema valid). `pytest -q` lulus.
5. **Smoke benchmark** — `python bench/run_benchmark.py --model openai/whisper-small --split test --max-files 200`. Pastikan `wer < 0.30`.
6. **Bumping skrip lama** — refactor `verify_paper_dataset_sota_whisper.py` agar memakai metric `evaluate.load("wer")` selain `SequenceMatcher`, jangan dihapus skrip lamanya (ada `superpowers-suite/finishing-a-development-branch` saat siap merge).
7. **Datasheet draft** — pakai skill `academic-research-suite` → `metadata/datasheet.md`.

> Setelah 7 langkah di atas selesai, kita masuk Fase 3 (full benchmark) dan paper sudah punya bahan tabel + figur.

---

## 7. Konvensi & guardrail

- **Reproducibility**: semua skrip eksperimen WAJIB punya `--seed`, log `git rev-parse HEAD`, log nama env conda.
- **Storage**: jangan commit WAV ke git; gunakan `git lfs` untuk metadata besar atau Hugging Face Hub sebagai *source of truth* untuk audio.
- **Privacy**: `metadata/anonymization_map.csv` masuk `.gitignore`. Public release hanya pakai ID `SPK01..SPK20`.
- **Lisensi**: default CC-BY 4.0 untuk audio + transkrip; kode penelitian MIT.
- **Verifikasi sebelum commit**: jalankan `pytest -q` + `python bench/run_benchmark.py --max-files 20` (smoke) sebelum push (skill `secure-commit-guard` opsional bisa diaktifkan via `bootstrap.sh --profile secure-delivery` tambahan).
- **Backup**: tiap perubahan struktur Processed_Balanced19_v3 → buat snapshot `_backup_<ts>/` dulu (pola sudah dipakai di root proyek besar).

---

## 8. Skill quick-call cheat-sheet

| Mau lakukan | Buka skill |
|-------------|-----------|
| Brainstorm fitur dataset baru | `superpowers-suite/brainstorming` |
| Buat plan multi-step | `superpowers-suite/writing-plans` |
| Implementasi loop modify→eval (mis. tuning hyperparameter) | `autoresearch-suite` |
| Debug kenapa WER tiba-tiba naik | `superpowers-suite/systematic-debugging` |
| Buat unit test sebelum implementasi | `superpowers-suite/test-driven-development` |
| Cek pekerjaan sebelum commit | `superpowers-suite/verification-before-completion` |
| Tulis section paper (Intro, Method, Exp) | `research-paper-writing` |
| Pipeline penuh penelitian → review → finalize | `academic-research-suite` |
| Convert hasil eksperimen ke notebook | `notebook-authoring` |
| Cross-check ASR dengan provider lain (AssemblyAI/Deepgram) | `media-pipeline` |
| Review PDF rujukan / redact identitas | `pdf-toolkit` |
| Push & buka PR ke GitHub | `github-delivery` |

---

*Dokumen ini hidup. Setiap fase yang selesai → tandai di plan-tracker dan update bagian §0 (snapshot status). Setiap perubahan skill stack → re-run `scripts/bootstrap.sh --profile academic --force` dari `my-grand-project-skills/` lalu update bagian §2.*

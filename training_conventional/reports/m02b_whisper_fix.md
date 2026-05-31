# Fix m02b Whisper FT — backward-through-graph error + OOM → switch to whisper-small

**Tanggal:** 2026-05-31 | **Tag:** `[FIX-WHISPER 2026-05-31]`
**Model:** m02b (paper #9, pretrained fine-tune). Command P-9 RUN_GUIDE.

---

## Gejala (dari log user)
1. Command tercetak punya **argumen ganda** (`--epochs 5 ... --epochs 5 ...`).
2. Crash: `RuntimeError: Trying to backward through the graph a second time ...` di `trainer.train()` (whisper-medium, batch 2, grad-accum 16, gradient-checkpointing).

## Diagnosis (2 bug + 1 batasan hardware)

### Bug A \u2014 backward through the graph twice (akar crash)
Gradient checkpointing **di-enable ganda**: `model.gradient_checkpointing_enable()` dipanggil manual DAN HF `Seq2SeqTrainer` mengaktifkannya lagi dari `training_args.gradient_checkpointing=True`. Dengan torch 2.10 + jalur autograd **reentrant** (default), graf di-backward dua kali \u2192 RuntimeError.

**Fix:** hapus `model.gradient_checkpointing_enable()` manual; biarkan Trainer yang enable, dengan `gradient_checkpointing_kwargs={"use_reentrant": False}` + `model.config.use_cache=False`. (`training/common/whisper_trainer.py`)

### Bug B \u2014 argumen ganda (kosmetik)
Wrapper `m02b/train.py` hardcode `--epochs/--batch-size/...` LALU `+ sys.argv[1:]` \u2192 flag user terduplikasi. **Fix:** wrapper hanya inject `--model-id` + `--run-dir`, sisanya forward dari user.

### Batasan C \u2014 whisper-medium OOM di GPU 8GB (terverifikasi)
Setelah Bug A diperbaiki, whisper-medium (764M) tetap **CUDA out of memory** di RTX 4060 Laptop 8.6GB walau batch 2 + grad-ckpt (OOM saat fase eval/generate). Sesuai instruksi user: **ganti ke whisper-small (244M)**.

## Perubahan
- Model m02b: `openai/whisper-medium` \u2192 **`openai/whisper-small`** (wrapper, test fallback, label test writer, slot aggregator `m02b-whisper-small-ft`, RUN_GUIDE P1/P-9/\u00a74.2).
- Folder tetap `m02b_whisper_medium_ft/` (hindari churn path); hanya model+label yang berubah.
- Batch direkomendasikan naik (small lebih ringan): contoh `--batch-size 8 --grad-accum 4`.

## Bukti (smoke nyata di torch-gpu)
| Konfigurasi | Hasil |
|---|---|
| medium, b2, grad-ckpt (setelah Bug A fix) | **CUDA OOM** (fase generate) |
| small, b4, grad-ckpt, via WRAPPER | **OK** \u2014 GPU 3996MB, training complete, no backward error, no duplikasi arg |
| small smoke 1-ep/12-sample | WER 0.2424 / CER 0.0433 (pretrained adaptasi cepat) |

Command tercetak bersih: `--model-id openai/whisper-small --run-dir ... --epochs 1 ...` (tanpa argumen ganda).

## Status untuk paper
- m02b kini **whisper-small FT**, valid sebagai baseline pretrained-FT (Radford 2022), muat di hardware 8GB.
- Run paper: `python3 training/m02b_whisper_medium_ft/train.py --epochs 5 --batch-size 8 --grad-accum 4 --lr 1e-5 --warmup-steps 500 --gradient-checkpointing --seed 42` di terminal terpisah.
- Jika ada akses A100/GPU besar dan ingin medium, ganti `--model-id openai/whisper-medium` di wrapper \u2014 tapi default kini small demi reproduksibilitas di laptop.

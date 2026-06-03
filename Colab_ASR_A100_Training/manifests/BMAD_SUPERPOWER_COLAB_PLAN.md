# BMAD + Superpowers Plan — Colab A100 Whisper Training

## Discovery

- Bottleneck lokal: Whisper training lama di RTX 4060/Windows/WSL/NTFS.
- Target: Colab A100 40 GB untuk m02b Whisper-small paper model, optional Whisper-medium secondary.
- Constraint: jangan menggandakan dataset permanen; upload dataset existing ke Google Drive satu kali.

## Architecture

- Code snapshot kecil: `Colab_ASR_A100_Training/repo_code/`.
- Dataset permanen: `MyDrive/ASR_Colab_A100/Data/...`.
- Runtime workdir cepat: `/content/asr_work/Paper_Datatset_SOTA`.
- Optional runtime dataset copy: `/content/asr_data/...` untuk mengurangi bottleneck Drive FUSE.
- Results: `MyDrive/ASR_Colab_A100/Results/...`.

## Delivery

1. Upload/sync Colab folder.
2. Upload dataset existing directly to Drive.
3. Run notebook bootstrap.
4. Train small A100 fast or paper-exact.
5. Test and sync results to Drive.
6. Download/sync results back to Linux/Windows later.

## Guardrails

- Do not upload `runs/`, `checkpoints/`, or raw dataset inside `repo_code`.
- Keep effective batch = 32 for comparability.
- Mark Colab runs with `_colab_a100`.

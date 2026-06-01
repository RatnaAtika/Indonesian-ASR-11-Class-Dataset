# Skills Transfer - Konfigurasi Codex/Pi/Skills dari Windows/WSL ke Ubuntu Native

Tujuan: saat laptop direstart ke Ubuntu native, agent/Codex/Pi bisa langsung memakai skill set dan konfigurasi yang sama tanpa perlu clone/download ulang dari internet jika partisi Windows/WSL bisa dibaca.

Dokumen ini fokus pada **best practice aman**:

1. Pakai **project skills** yang sudah ikut repo (`.agents/skills/`) sebagai sumber utama.
2. Copy/sync **user skills** dari environment sekarang (`~/.codex/skills`, `~/.pi/agent/git/...`) ke Ubuntu jika tersedia.
3. Hindari commit/copy sembarang secret ke repo.
4. Simpan bundle lokal di folder yang di-ignore git: `_linux_transfer/` atau `skills_transfer_bundle/`.

> Penting: file ini boleh dicommit. Tetapi bundle hasil transfer **jangan dicommit** karena bisa berisi `auth.json`, token, session, atau credential.

---

## 1. Ringkasan sumber skills/config yang terdeteksi di environment sekarang

Dari audit environment saat dokumen dibuat:

```text
Project skills repo:
  .agents/skills/
  AGENTS.md

Codex user config/skills:
  ~/.codex/config.toml
  ~/.codex/auth.json                  # secret, jangan commit
  ~/.codex/skills/
  ~/.codex/rules/
  ~/.codex/memories/

Pi agent config/skills:
  ~/.pi/agent/settings.json
  ~/.pi/agent/models.json
  ~/.pi/agent/auth.json                # secret, jangan commit
  ~/.pi/agent/git/github.com/...       # skill repos, termasuk pi-superpowers
  ~/.pi/agent/bin/rg
  ~/.pi/agent/bin/fd
```

Project ini sudah membawa portable skills di:

```text
.agents/skills/academic-research-suite
.agents/skills/agent-harness-compatibility
.agents/skills/autoresearch-suite
.agents/skills/github-delivery
.agents/skills/media-pipeline
.agents/skills/model-provider-config
.agents/skills/notebook-authoring
.agents/skills/pdf-toolkit
.agents/skills/portable-project-adapter
.agents/skills/research-paper-writing
.agents/skills/skill-authoring
.agents/skills/superpowers-suite
```

Jadi jika tidak ingin transfer seluruh user config, **minimum yang wajib** hanya repo ini + `.agents/skills/`.

---

## 2. Best practice pilihan transfer

### Opsi A - recommended: copy bundle dari environment sekarang ke folder repo, lalu Ubuntu membaca/copy dari sana

Cocok jika:

- Ubuntu native bisa membaca partisi Windows/WSL path tempat repo ini berada.
- Ingin minim download/clone.
- Ingin menyimpan satu bundle lokal sementara.

Alur:

1. Dari environment sekarang, buat `_linux_transfer/` berisi skills/config yang diperlukan.
2. Boot ke Ubuntu.
3. Mount/buka partisi Windows.
4. Copy `_linux_transfer/` ke home Ubuntu.
5. Install/symlink ke `~/.codex` dan `~/.pi`.

### Opsi B - paling bersih: Ubuntu pakai project skills dari repo saja

Cocok jika:

- Tidak butuh history/memory/token lama.
- Mau login ulang Codex/Pi dari Ubuntu.
- Ingin menghindari transfer secret.

Alur:

1. Ubuntu buka repo ini dari Windows atau copy ke ext4.
2. Agent membaca `.agents/skills/` dan `AGENTS.md`.
3. Login ulang provider/API dari Ubuntu.

### Opsi C - symlink langsung ke skill folders di partisi Windows/WSL

Tidak direkomendasikan untuk long term, tetapi bisa untuk darurat.

Kelemahan:

- Symlink ke NTFS/WSL path bisa lambat/rapuh.
- Jika Windows hibernate/Fast Startup, path bisa read-only/bermasalah.
- Better: copy sekali ke ext4 Ubuntu.

---

## 3. Buat bundle transfer dari environment sekarang

Jalankan dari environment yang saat ini sudah punya skills (WSL/Windows-side Linux). Path repo:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
mkdir -p _linux_transfer/codex _linux_transfer/pi-agent _linux_transfer/project
```

### 3.1 Copy project skills dari repo

```bash
rsync -aH --delete .agents/ _linux_transfer/project/.agents/
cp -f AGENTS.md _linux_transfer/project/AGENTS.md
cp -f skills_transfer.md _linux_transfer/project/skills_transfer.md
cp -f note_prompt_linux.md _linux_transfer/project/note_prompt_linux.md 2>/dev/null || true
cp -f GPU_Cloud.md _linux_transfer/project/GPU_Cloud.md 2>/dev/null || true
```

### 3.2 Copy Codex skills/config non-destructive

```bash
# Skills and rules are safe-ish, but still inspect before sharing.
rsync -aH --delete ~/.codex/skills/ _linux_transfer/codex/skills/ 2>/dev/null || true
rsync -aH --delete ~/.codex/rules/ _linux_transfer/codex/rules/ 2>/dev/null || true
rsync -aH --delete ~/.codex/memories/ _linux_transfer/codex/memories/ 2>/dev/null || true
cp -f ~/.codex/config.toml _linux_transfer/codex/config.toml 2>/dev/null || true
cp -f ~/.codex/models_cache.json _linux_transfer/codex/models_cache.json 2>/dev/null || true
```

### 3.3 Secret handling untuk Codex auth

`~/.codex/auth.json` bisa berisi token. Pilih salah satu:

**Pilihan recommended:** jangan copy, login ulang di Ubuntu.

```bash
rm -f _linux_transfer/codex/auth.json
```

**Pilihan offline/cepat (berisiko):** copy hanya jika laptop pribadi dan disk aman.

```bash
cp -f ~/.codex/auth.json _linux_transfer/codex/auth.json
chmod 600 _linux_transfer/codex/auth.json
```

Jika memilih copy auth, jangan pernah commit `_linux_transfer/`.

### 3.4 Copy Pi agent config/skills

```bash
rsync -aH --delete ~/.pi/agent/git/ _linux_transfer/pi-agent/git/ 2>/dev/null || true
rsync -aH --delete ~/.pi/agent/bin/ _linux_transfer/pi-agent/bin/ 2>/dev/null || true
cp -f ~/.pi/agent/settings.json _linux_transfer/pi-agent/settings.json 2>/dev/null || true
cp -f ~/.pi/agent/models.json _linux_transfer/pi-agent/models.json 2>/dev/null || true
cp -f ~/.pi/agent/locks.json _linux_transfer/pi-agent/locks.json 2>/dev/null || true
```

Secret Pi auth:

```bash
# Recommended: jangan copy auth; login ulang Pi/agent di Ubuntu.
rm -f _linux_transfer/pi-agent/auth.json

# Jika benar-benar perlu offline transfer auth (berisiko):
# cp -f ~/.pi/agent/auth.json _linux_transfer/pi-agent/auth.json
# chmod 600 _linux_transfer/pi-agent/auth.json
```

### 3.5 Buat manifest bundle

```bash
cat > _linux_transfer/MANIFEST.txt <<EOF
Created: $(date -Is)
Source repo: $(pwd)
Git commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)
Contains:
- project/.agents skills
- codex skills/rules/config (auth optional, usually omitted)
- pi-agent git/bin/settings/models (auth optional, usually omitted)
WARNING: do not commit this folder; it may contain local credentials if auth copied.
EOF

find _linux_transfer -maxdepth 3 -type f | sed 's#^#- #' > _linux_transfer/FILES.txt
```

### 3.6 Verifikasi bundle tidak masuk git

`.gitignore` sudah menambahkan:

```text
_linux_transfer/
skills_transfer_bundle/
```

Cek:

```bash
git status --short --ignored | grep -E '_linux_transfer|skills_transfer_bundle' || true
```

---

## 4. Boot ke Ubuntu native dan temukan repo/bundle di partisi Windows

Setelah masuk Ubuntu:

```bash
lsblk -f
ls /media/$USER
```

Cari repo:

```bash
find /media/$USER /mnt -maxdepth 8 -type d -name 'Paper_Datatset_SOTA' 2>/dev/null | head -20
```

Set variabel sesuai hasil:

```bash
export WIN_REPO="/media/$USER/Windows/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
ls "$WIN_REPO/_linux_transfer"
```

Jika path Windows berbeda, ganti `WIN_REPO`.

---

## 5. Install/copy bundle ke Ubuntu home

### 5.1 Copy bundle ke ext4 Ubuntu

```bash
mkdir -p "$HOME/asr_transfer"
rsync -aH --info=progress2 "$WIN_REPO/_linux_transfer/" "$HOME/asr_transfer/_linux_transfer/"
```

Gunakan copy ke ext4, bukan symlink ke Windows, agar agent lebih cepat dan tidak tergantung mount Windows.

### 5.2 Install project skills ke repo Ubuntu

Jika repo Ubuntu sudah ada di `$HOME/asr/Paper_Datatset_SOTA`:

```bash
export UBUNTU_REPO="$HOME/asr/Paper_Datatset_SOTA"
mkdir -p "$UBUNTU_REPO"
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/project/.agents/" "$UBUNTU_REPO/.agents/"
cp -f "$HOME/asr_transfer/_linux_transfer/project/AGENTS.md" "$UBUNTU_REPO/AGENTS.md" 2>/dev/null || true
```

Jika belum punya repo dan ingin menghindari clone, copy dari Windows repo ke ext4 Ubuntu:

```bash
mkdir -p "$HOME/asr/Paper_Datatset_SOTA"
rsync -aH --info=progress2 \
  --exclude '.git/' \
  --exclude '*/runs/' \
  --exclude '_linux_transfer/' \
  "$WIN_REPO/" "$HOME/asr/Paper_Datatset_SOTA/"
```

Catatan: jika ingin git history utuh, lebih baik `git clone` saat internet ada. Jika tidak ada internet, copy tanpa `.git` tetap bisa untuk training, tetapi bukan working tree git penuh.

### 5.3 Install Codex skills/config

```bash
mkdir -p "$HOME/.codex"
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/codex/skills/" "$HOME/.codex/skills/" 2>/dev/null || true
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/codex/rules/" "$HOME/.codex/rules/" 2>/dev/null || true
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/codex/memories/" "$HOME/.codex/memories/" 2>/dev/null || true
cp -n "$HOME/asr_transfer/_linux_transfer/codex/config.toml" "$HOME/.codex/config.toml" 2>/dev/null || true
cp -n "$HOME/asr_transfer/_linux_transfer/codex/models_cache.json" "$HOME/.codex/models_cache.json" 2>/dev/null || true
chmod -R go-rwx "$HOME/.codex" 2>/dev/null || true
```

Jika `auth.json` ikut dibundle dan memang ingin dipakai:

```bash
cp -n "$HOME/asr_transfer/_linux_transfer/codex/auth.json" "$HOME/.codex/auth.json" 2>/dev/null || true
chmod 600 "$HOME/.codex/auth.json" 2>/dev/null || true
```

Jika tidak ada `auth.json`, login ulang Codex di Ubuntu.

### 5.4 Install Pi agent skills/config

```bash
mkdir -p "$HOME/.pi/agent"
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/pi-agent/git/" "$HOME/.pi/agent/git/" 2>/dev/null || true
rsync -aH --delete "$HOME/asr_transfer/_linux_transfer/pi-agent/bin/" "$HOME/.pi/agent/bin/" 2>/dev/null || true
cp -n "$HOME/asr_transfer/_linux_transfer/pi-agent/settings.json" "$HOME/.pi/agent/settings.json" 2>/dev/null || true
cp -n "$HOME/asr_transfer/_linux_transfer/pi-agent/models.json" "$HOME/.pi/agent/models.json" 2>/dev/null || true
cp -n "$HOME/asr_transfer/_linux_transfer/pi-agent/locks.json" "$HOME/.pi/agent/locks.json" 2>/dev/null || true
chmod -R go-rwx "$HOME/.pi" 2>/dev/null || true
```

Jika Pi `auth.json` ikut dibundle:

```bash
cp -n "$HOME/asr_transfer/_linux_transfer/pi-agent/auth.json" "$HOME/.pi/agent/auth.json" 2>/dev/null || true
chmod 600 "$HOME/.pi/agent/auth.json" 2>/dev/null || true
```

Jika tidak ada, login ulang Pi/agent di Ubuntu.

---

## 6. Opsi tanpa copy: symlink ke project skills dari repo Windows

Gunakan hanya jika copy tidak memungkinkan.

```bash
mkdir -p "$HOME/.codex/skills"
ln -sfn "$WIN_REPO/.agents/skills/superpowers-suite" "$HOME/.codex/skills/superpowers-suite"
ln -sfn "$WIN_REPO/.agents/skills/github-delivery" "$HOME/.codex/skills/github-delivery"
ln -sfn "$WIN_REPO/.agents/skills/model-provider-config" "$HOME/.codex/skills/model-provider-config"
ln -sfn "$WIN_REPO/.agents/skills/research-paper-writing" "$HOME/.codex/skills/research-paper-writing"
```

Kritik:

- Symlink ke NTFS bisa lambat/fragile.
- Kalau partisi Windows tidak termount, skills hilang.
- Untuk training panjang, lebih baik copy ke ext4.

---

## 7. Validasi skills di Ubuntu

### 7.1 Validasi file skills ada

```bash
find "$HOME/.codex/skills" -maxdepth 2 -name SKILL.md | sort | sed -n '1,80p'
find "$HOME/.pi/agent/git" -maxdepth 6 -name SKILL.md | sort | sed -n '1,80p'
find "$HOME/asr/Paper_Datatset_SOTA/.agents/skills" -maxdepth 2 -name SKILL.md | sort
```

### 7.2 Validasi command line tools

```bash
which rg || echo 'rg missing; install ripgrep'
which fd || echo 'fd missing; install fd-find'
python3 --version
node --version 2>/dev/null || true
```

Install tools jika perlu:

```bash
sudo apt update
sudo apt install -y ripgrep fd-find jq git rsync tmux
mkdir -p "$HOME/.local/bin"
ln -sfn /usr/bin/fdfind "$HOME/.local/bin/fd" 2>/dev/null || true
```

### 7.3 Validasi agent membaca project context

Dari repo Ubuntu:

```bash
cd "$HOME/asr/Paper_Datatset_SOTA"
ls AGENTS.md .agents/skills
```

Jika memakai Codex CLI, buka session dari folder repo ini agar context project dan `.agents/skills` terbaca.

---

## 8. Model/provider config untuk GPT-5.5 style workflow

Jika nanti memakai model GPT-5.5 / Codex terbaru, pastikan skills yang relevan tersedia:

- `model-provider-config`: mapping provider/model/API behavior.
- `agent-harness-compatibility`: kompatibilitas skill antar harness.
- `superpowers-suite`: planning/debugging/verification workflow.
- `academic-research-suite` dan `research-paper-writing`: paper/report.
- `github-delivery`: commit/push.

Validasi:

```bash
find "$HOME/asr/Paper_Datatset_SOTA/.agents/skills" -maxdepth 2 -name SKILL.md | grep -E 'model-provider-config|agent-harness|superpowers|research|github'
```

Jika user-level Codex skills dibutuhkan juga:

```bash
find "$HOME/.codex/skills" -maxdepth 2 -name SKILL.md | grep -E 'bmad|superpowers|github|model-provider|research' || true
```

Catatan best practice: jangan edit manual credential provider di Markdown. Gunakan login resmi CLI atau environment variables lokal.

---

## 9. Security checklist

Sebelum dan sesudah transfer:

```bash
# Cari auth yang tidak sengaja berada di repo kerja
cd "$HOME/asr/Paper_Datatset_SOTA" 2>/dev/null || cd "$WIN_REPO"
find . -maxdepth 4 -type f \( -iname '*auth*' -o -iname '*token*' -o -iname '*secret*' -o -iname '*.sqlite' \) | sed -n '1,120p'

git status --short --ignored | grep -E '_linux_transfer|skills_transfer_bundle|auth|token|secret' || true
```

Jangan commit:

- `_linux_transfer/`
- `skills_transfer_bundle/`
- `auth.json`
- `.sqlite` history/session DB
- cloud/API token
- checkpoint/model/data besar

Jika auth terlanjur dicopy ke folder repo, hapus atau pindahkan:

```bash
rm -f _linux_transfer/codex/auth.json _linux_transfer/pi-agent/auth.json
```

---

## 10. Skenario paling cepat saat boot Ubuntu

Jika ingin langsung jalan tanpa clone/download repo:

```bash
# 1) Temukan repo Windows
find /media/$USER /mnt -maxdepth 8 -type d -name 'Paper_Datatset_SOTA' 2>/dev/null | head
export WIN_REPO="/media/$USER/Windows/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"

# 2) Copy repo minus runs ke ext4 Ubuntu
mkdir -p "$HOME/asr/Paper_Datatset_SOTA"
rsync -aH --info=progress2 \
  --exclude '.git/' \
  --exclude '*/runs/' \
  --exclude '_linux_transfer/' \
  "$WIN_REPO/" "$HOME/asr/Paper_Datatset_SOTA/"

# 3) Copy dataset ke ext4 jika ruang cukup (recommended)
cd "$HOME/asr/Paper_Datatset_SOTA"
rsync -aH --info=progress2 \
  "$WIN_REPO/Processed_Balanced19_v7_natural_synth/" \
  "Processed_Balanced19_v7_natural_synth/"
rsync -aH --info=progress2 "$WIN_REPO/training/data_final/" "training/data_final/"

# 4) Copy skills/config bundle jika ada
if [ -d "$WIN_REPO/_linux_transfer" ]; then
  mkdir -p "$HOME/asr_transfer"
  rsync -aH --info=progress2 "$WIN_REPO/_linux_transfer/" "$HOME/asr_transfer/_linux_transfer/"
  mkdir -p "$HOME/.codex" "$HOME/.pi/agent"
  rsync -aH "$HOME/asr_transfer/_linux_transfer/codex/skills/" "$HOME/.codex/skills/" 2>/dev/null || true
  rsync -aH "$HOME/asr_transfer/_linux_transfer/pi-agent/git/" "$HOME/.pi/agent/git/" 2>/dev/null || true
fi

# 5) Validate project skills
find "$HOME/asr/Paper_Datatset_SOTA/.agents/skills" -maxdepth 2 -name SKILL.md | sort | sed -n '1,80p'
```

Lanjutkan training memakai `note_prompt_linux.md`.

---

## 11. Skenario minimal tanpa bundle

Jika tidak sempat membuat `_linux_transfer/`, Ubuntu tetap bisa jalan dengan project skills saja:

```bash
export WIN_REPO="/media/$USER/Windows/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
mkdir -p "$HOME/asr/Paper_Datatset_SOTA"
rsync -aH --info=progress2 --exclude '*/runs/' "$WIN_REPO/" "$HOME/asr/Paper_Datatset_SOTA/"
cd "$HOME/asr/Paper_Datatset_SOTA"
ls .agents/skills AGENTS.md
```

Kemudian login ulang Codex/Pi di Ubuntu. Ini paling aman karena tidak memindahkan token.

---

## 12. Restore/update kembali ke Windows/WSL setelah Ubuntu selesai

Jika Ubuntu menghasilkan update docs kecil:

```bash
export UBUNTU_REPO="$HOME/asr/Paper_Datatset_SOTA"
export WIN_REPO="/media/$USER/Windows/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"

rsync -aH --info=progress2 \
  --include '*/' \
  --include '*.md' \
  --include '*.py' \
  --include '*.json' \
  --exclude '*/runs/***' \
  --exclude '_linux_transfer/***' \
  --exclude '*' \
  "$UBUNTU_REPO/" "$WIN_REPO/"
```

Jika ingin copy hasil training run, pakai instruksi di `note_prompt_linux.md`, bukan rsync docs-only di atas.

---

## 13. Final recommendation

Best practice untuk kasus laptop dual OS ini:

1. **Jangan clone/download ulang jika tidak perlu**: baca repo Windows, lalu `rsync` ke ext4 Ubuntu.
2. **Jangan jalankan training berat langsung dari NTFS** kecuali fallback.
3. **Gunakan project skills `.agents/skills/` sebagai baseline** karena sudah ikut repo dan aman.
4. **Transfer user skills ke `~/.codex/skills` dan `~/.pi/agent/git` hanya jika perlu**.
5. **Jangan transfer auth/token kecuali benar-benar perlu dan mesin pribadi aman**; login ulang lebih aman.
6. **Simpan semua bundle lokal di `_linux_transfer/` atau `skills_transfer_bundle/`**, sudah di-ignore git.
7. Setelah skills siap, lanjutkan eksekusi training dari `note_prompt_linux.md`.

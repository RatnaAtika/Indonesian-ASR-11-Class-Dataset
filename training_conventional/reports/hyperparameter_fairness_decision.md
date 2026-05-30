# Keputusan Metodologis: Apakah Hyperparameter Harus Sama Antar-Model?

**Konteks:** Publikasi *dataset* (Data in Brief, Elsevier), bukan publikasi *metode*.
**Pertanyaan inti:** Wajibkah hyperparameter (terutama jumlah epoch) identik untuk semua model? Bolehkah HMM-GMM yang lemah dilatih 100 epoch sementara ViT-Novel hanya 30 epoch? Mengapa Whisper hanya 5 epoch?
**Skill yang dipakai:** BMAD (analyst → keputusan terdokumentasi), Superpowers (brainstorming: jelajahi alternatif + rekomendasi), riset mendalam (4 paper benchmark/fairness 2023–2026).

---

## TL;DR (rekomendasi)

**Tidak wajib identik. Yang wajib adalah *protokol* yang sama, bukan *angka* yang sama.** Untuk paper dataset, jawaban yang defensible di mata reviewer adalah:

1. **Samakan yang menentukan keadilan data:** split train/dev/test (frozen), fitur, tokenizer, decoding (greedy, no-LM), metrik, dan **kriteria penghentian** (mis. early-stopping patience yang sama).
2. **Boleh berbeda yang merupakan sifat alami arsitektur:** jumlah epoch, learning rate, batch size, scheduler — selama dipilih agar **tiap model mencapai konvergensi-nya sendiri** dan dijustifikasi.
3. **Whisper 5 epoch BUKAN ketidakadilan** — itu konvensi fine-tuning model pretrained besar (30 epoch = overfit pasti). Reviewer menerima ini bila dijelaskan.
4. **HMM-GMM 100 "epoch" boleh**, tapi hati-hati: untuk HMM itu *EM iteration*, bukan gradient epoch, dan ia konvergen ~10–25 iter. Menaikkan ke 100 hampir tidak mengubah hasil (lihat §4). Yang lebih penting bukan "lebih banyak epoch untuk yang lemah", melainkan **"cukup epoch sampai konvergen untuk semua"**.

> **Prinsip pengikat (dari riset):** keuntungan/kekalahan sebuah model harus dapat diatribusikan ke **arsitekturnya**, bukan ke artefak training yang tidak setara. Selama itu terpenuhi, heterogenitas hyperparameter justru *lebih adil* daripada memaksakan satu angka.

---

## 1. Mengapa "satu angka epoch untuk semua" JUSTRU tidak adil

Riset benchmark/fairness lintas-bidang konsisten menolak "identik kaku":

- **Pretrained vs from-scratch berbeda fundamental.** Whisper-medium sudah dilatih 680k jam audio; fine-tuning 30 epoch pada korpus ~92 jam = catastrophic forgetting + overfit. Konvensi paper FT (Radford 2022, Pratap 2023): 3–5 epoch. (Sudah benar di protokol repo.)
- **EM iteration ≠ gradient epoch.** HMM-GMM (Baum-Welch) konvergen dalam ~10–25 iter; "100 epoch" untuknya menyesatkan secara terminologi dan praktis sia-sia.
- **Sensitivitas optimizer terhadap arsitektur sangat tinggi.** Dahl et al. (AlgoPerf, 2023) menunjukkan perubahan arsitektur kecil membalik ranking optimizer; memaksa LR/epoch sama dapat membuat satu arsitektur tak terlatih (untrainable) sementara yang lain baik-baik saja. Jadi "identik" malah bisa menghasilkan perbandingan yang *salah*.
- **Wang et al. (2023, "Why is pruning so confusing")** menegaskan prinsip fairness: jangan kunci semua hyperparameter ke satu nilai; kunci **base/data/protokol**, lalu beri tiap metode kesempatan konvergen. Mereka tunjukkan baseline lemah (L1-pruning) bisa "dihidupkan" hanya dengan LR/epoch retraining yang layak — bukti bahwa **angka training yang tidak setara mendistorsi kesimpulan**.

**Contoh dari benchmark nyata yang heterogen tapi tetap dipublikasi top-tier:**
- **STEP (Spiking Transformer, 2025):** di CIFAR semua model 400 epoch (seragam, karena ukuran setara), tapi di ImageNet QKFormer 200 ep × batch 32 vs Spikformer 300 ep × batch 24 — eksplisit disebut *"intentional, resource-aware decision rather than an oversight"*, dengan semua hyperparameter lain diseragamkan via satu skrip.
- **CheXGenBench (2025):** 11 model T2I, **20 epoch seragam** untuk semua, TAPI model <1B full-FT dan >1B pakai LoRA — yaitu *jenis adaptasi berbeda per kapasitas*, dan LR berbeda per model (Tabel 11). Mereka justru mengkritik literatur sebelumnya yang "inconsistent training budgets".

Kesimpulan riset: **dua pola sama-sama sah** — (a) epoch seragam ketika model setara skalanya, atau (b) epoch per-keluarga yang dijustifikasi ketika skalanya berbeda. Yang tidak sah adalah epoch tak setara **tanpa justifikasi** atau yang membuat sebagian model tak konvergen.

---

## 2. Tiga pendekatan (brainstorming + rekomendasi)

### Pendekatan A — Epoch seragam mutlak (mis. semua 30)
- **Plus:** paling mudah dijelaskan satu kalimat; tampak "adil" secara naif.
- **Minus:** menghukum pretrained (Whisper overfit), memboroskan compute pada HMM (sudah konvergen), dan bisa membuat arsitektur tertentu tak terlatih. Bertentangan dengan praktik FT pretrained.
- **Cocok bila:** semua model from-scratch dengan skala parameter mirip. **Tidak cocok** untuk lineup Anda (campur HMM klasik + from-scratch + pretrained Whisper).

### Pendekatan B — Fixed compute budget (samakan total FLOPs/wall-time) ⭐ paling ketat
- **Plus:** paling defensible secara ilmiah (setiap model dapat "anggaran komputasi" sama); standar SX-B di literatur pruning.
- **Minus:** sangat sulit dikalibrasi; HMM CPU-only vs ViT GPU tidak punya FLOP yang comparable; menambah kompleksitas pelaporan besar.
- **Cocok bila:** klaim utama adalah efisiensi. **Overkill** untuk paper *dataset* yang fokusnya merilis data, bukan mengklaim metode tercepat.

### Pendekatan C — Protokol seragam + epoch per-keluarga yang dijustifikasi + early-stopping universal ⭐ **REKOMENDASI**
- **Plus:** persis yang sudah ada di `FAIR_COMPARISON_PROTOCOL.md` repo Anda; sejalan dengan STEP & CheXGenBench; mudah dipertahankan saat reviewer bertanya; tidak memboroskan compute; tiap model adil mencapai potensinya.
- **Minus:** butuh satu paragraf justifikasi di §4.2 (sudah ditulis di protokol repo).
- **Aturan:** kunci data/fitur/tokenizer/decoding/metrik/seed + **patience early-stopping sama (mis. 10)**; epoch *maksimum* per keluarga (from-scratch 30, pretrained FT 5, HMM EM 30 iter); LR per-keluarga sesuai konvensi.

**Untuk paper *dataset*, Pendekatan C adalah titik manis** antara kekakuan dan keadilan, dan sudah Anda miliki.

---

## 3. Spesifik untuk pertanyaan "HMM-GMM 100 epoch, ViT 30 epoch"

Boleh secara prinsip, **tetapi bukan strategi yang tepat** untuk kasus ini, karena alasan berikut:

1. **HMM-GMM tidak punya "epoch" gradient.** Yang ada adalah EM iteration. Menyebut "100 epoch" di paper untuk HMM akan membingungkan reviewer. Pakai istilah benar: *"30 Baum-Welch EM iterations (converged)"*.
2. **Menambah iterasi HMM tidak menyembuhkan kelemahannya.** Dari diagnosis m08: WER>1 disebabkan **kapasitas model rendah** (5 state, 3 mix untuk kalimat penuh), bukan kurang iterasi. EM sudah konvergen jauh sebelum iter ke-30; 100 iter → WER praktis sama. (Analog kuat: CheXGenBench Appendix E menunjukkan menaikkan Sana dari 20→50 epoch hanya memberi perbaikan FID "modest" — extended training tidak mengubah cerita.)
3. **Asimetri "lemah dapat lebih banyak, kuat dapat lebih sedikit" justru memicu pertanyaan reviewer.** Itu terlihat seperti "menganakemaskan" baseline lemah agar tidak terlalu memalukan, atau "menahan" model kuat. Keduanya melemahkan klaim. Yang benar: **biarkan tiap model konvergen pada anggaran wajar keluarganya** dan laporkan apa adanya — kelemahan HMM justru menjadi *narasi motivasi* (lihat report m08 yang sudah dibuat).
4. **Jika ingin menunjukkan potensi penuh ViT-Novel**, jalurnya bukan "kurangi epoch model lain", melainkan lampirkan **extended-training run** ViT (mis. 200 epoch) di **Appendix B** sebagai "extended/SOTA", terpisah dari Table 1 yang fair-30-epoch. (Sudah direncanakan di protokol repo.)

---

## 4. Yang harus dilaporkan di paper agar lolos review

Reviewer dataset/benchmark (lihat checklist NeurIPS di paper-paper riset) menuntut **transparansi**, bukan keseragaman:

- **Tabel hyperparameter per-model** (epoch, optimizer, LR, batch, scheduler, early-stop) — wajib, di §4.2 atau Appendix. Ini yang membuat heterogenitas *dapat diterima*.
- **Justifikasi eksplisit setiap deviasi:** "Whisper 5 epoch (Radford 2022, hindari catastrophic forgetting)"; "HMM 30 EM iter (Baum-Welch converged)"; "from-scratch 30 epoch + early-stop patience 10".
- **Kriteria penghentian & pemilihan checkpoint:** best-on-val (bukan last-epoch), patience sama → ini "kesetaraan kesempatan" yang menggantikan "kesetaraan epoch".
- **Compute resources** (GPU, jam) per model — standar checklist.
- **Pernyataan fairness 1 paragraf** (sudah ada di protokol repo §3) yang menyebut: data/fitur/tokenizer/decoding/metrik seragam; epoch budget per-family dijustifikasi.

Kalimat kunci yang bisa langsung dipakai di §4.2 (adaptasi dari riset):

> "Karena lineup mencakup model generatif klasik (HMM-GMM), hybrid neural-HMM, encoder-decoder from-scratch, dan model pretrained yang di-fine-tune, kami tidak menyeragamkan jumlah langkah pelatihan—praktik yang justru akan membuat sebagian arsitektur tidak konvergen atau model pretrained overfit. Sebagai gantinya kami menyeragamkan split data, fitur, tokenizer, dekoding greedy tanpa LM, metrik, dan kriteria early-stopping (patience 10), serta menetapkan anggaran pelatihan maksimum per keluarga arsitektur dengan justifikasi konvensional (pretrained FT: 5 epoch; from-scratch: 30 epoch; HMM: 30 iterasi EM). Pemilihan checkpoint selalu best-on-validation. Dengan demikian setiap sistem dievaluasi pada potensi konvergennya, dan perbedaan kinerja dapat diatribusikan ke arsitektur, bukan ke anggaran pelatihan yang tidak setara."

---

## 5. Keputusan akhir & langkah konkret

| Aspek | Keputusan |
|---|---|
| Wajib identik? | **Tidak.** Protokol identik; angka per-keluarga. |
| Epoch HMM-GMM | Tetap **30 EM iter** (sudah konvergen); jangan 100. Istilah: "EM iterations", bukan "epoch". |
| Epoch ViT-Novel | **30** (fair, di Table 1) + **200** di Appendix B sebagai extended/SOTA. |
| Whisper | **5 epoch** — pertahankan, justifikasi Radford 2022. Bukan ketidakadilan. |
| Penyetara keadilan | data/fitur/tokenizer/decoding/metrik/seed + **early-stopping patience 10** untuk semua trainer neural. |
| Wajib di paper | tabel hyperparameter per-model + justifikasi per deviasi + compute + best-on-val. |
| Status repo | Protokol ini **sudah ada** di `reports/hyperparameter_reference/FAIR_COMPARISON_PROTOCOL.md` — keputusan ini mengonfirmasinya, hanya menambah landasan riset + koreksi terminologi epoch HMM. |

**Langkah konkret:**
1. Jangan ubah epoch HMM ke 100; pertahankan 30 EM iter, perbaiki terminologi di laporan/§4.2.
2. Pastikan §4.2 paper memuat tabel hyperparameter per-model + paragraf fairness di atas.
3. Jalankan extended ViT (200 ep) hanya untuk Appendix B, di terminal terpisah.
4. (Opsional, memperkuat) tambahkan 1 baris "early-stopping patience" ke tiap entry tabel agar reviewer melihat "equal opportunity to converge".

> Catatan kepercayaan: rekomendasi ini bersandar pada empat paper benchmark/fairness 2023–2026 (AlgoPerf, "pruning confusing", STEP, CheXGenBench) yang sudah saya baca; semuanya mendukung "protokol seragam + hyperparameter per-arsitektur yang dijustifikasi". Yang belum diverifikasi: apakah reviewer spesifik Data in Brief Anda punya kebijakan tambahan — itu di luar jangkauan data yang saya akses.

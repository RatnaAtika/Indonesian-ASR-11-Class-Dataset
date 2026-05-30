# Usulan Bahasan Bi-LSTM dan RCNN untuk Paper_Datatset_SOTA

## Tujuan Dokumen

Dokumen ini merangkum informasi dan usulan bahasan algoritma **Bi-LSTM** dan **RCNN/T-RCNN** yang relevan dengan proyek `Paper_Datatset_SOTA`.

Dokumen ini dibuat untuk:

- menjadi bahan lanjutan penulisan paper/dataset SOTA
- menyatukan konteks lama yang ditemukan di workspace
- membandingkan posisi Bi-LSTM dan RCNN/T-RCNN sebagai baseline atau usulan model
- memberi arahan eksperimen lanjutan yang sesuai dengan dataset hasil rebuild `Processed_Balanced19_v3`

## Workspace dan Sumber Konteks yang Ditemukan

Workspace utama proyek paper dataset:

- `c:\Users\ratnaatika\AI\Dataset ASR\Paper_Datatset_SOTA`

Catatan penting:

- Nama folder aktual adalah `Paper_Datatset_SOTA`, terdapat typo `Datatset`.
- Semua pekerjaan dataset paper sebelumnya sudah dijaga terisolasi di folder ini.
- Runtime yang digunakan selama proyek: `WSL2`, conda env `torch-gpu`, GPU `RTX 4060 8GB`.

Sumber konteks algoritma yang ditemukan di workspace:

- `baselines/bilstm_asr/README.md`
- `baselines/bilstm_asr/ANALYSIS.md`
- `baselines/bilstm_asr/config.py`
- `baselines/bilstm_asr/model.py`
- `baselines/bilstm_asr/runs/train_3/metrics/summary.json`
- `baselines/bilstm_asr/runs/train_3/eval_greedy/summary.json`
- `baselines/trcnn_asr/README.md`
- `baselines/trcnn_asr/ANALYSIS.md`
- `baselines/trcnn_asr/config.py`
- `baselines/trcnn_asr/models/trcnn.py`
- `baselines/trcnn_asr/runs/train_6/metrics/summary.json`
- `baselines/trcnn_asr/runs/train_6/eval_greedy/summary.json`

Catatan audit konteks:

- Tidak ditemukan file prompt mentah khusus berisi percakapan lama tentang Bi-LSTM/RCNN di dalam `Paper_Datatset_SOTA`.
- Namun ditemukan implementasi, dokumentasi, konfigurasi, dan hasil run untuk baseline `Bi-LSTM ASR` dan `T-RCNN ASR` pada folder `baselines/` di root workspace.
- Resume ini disusun dari artefak tersebut dan disesuaikan dengan konteks final proyek `Paper_Datatset_SOTA`.

## Konteks Dataset Paper_Datatset_SOTA

Dataset final yang sudah dibangun dan diverifikasi berada di:

- `Paper_Datatset_SOTA/Processed_Balanced19_v3/Dataset_Balanced19`

Status final dataset:

- Kategori: `11`
- Total take: `5500`
- Total WAV output: `104500`
- WAV per take: `19`
- Bad source takes: `0`
- Build problem takes: `0`
- Bad output takes: `0`
- Naming output: zero-padded, contoh `01.wav`, `02.wav`, dst.

Hasil verifikasi Whisper penuh:

- Run: `Whisper_Verification/run_20260403_221557`
- Model: `openai/whisper-large-v3`
- Total files: `104500`
- OK files: `104500`
- Error files: `0`
- Likely mismatch count: `465`

Implikasi untuk training model:

- Dataset build sudah valid secara struktur.
- Namun ada `465 likely_mismatch` yang perlu dipertimbangkan sebelum training final.
- Jika model dilatih langsung memakai semua data, mismatch tersebut berpotensi menjadi noise label kecil tetapi terlokalisasi.
- Untuk eksperimen paper, disarankan membuat skenario:
  - training dengan seluruh data final
  - training dengan data mismatch diberi flag/exclude
  - analisis dampak mismatch terhadap WER/CER

## Posisi Bi-LSTM dalam Proyek

### Ringkasan Konsep Bi-LSTM

**Bi-LSTM** atau **Bidirectional Long Short-Term Memory** adalah model sekuensial yang membaca fitur audio dari dua arah:

- arah maju: dari awal ke akhir sinyal
- arah mundur: dari akhir ke awal sinyal

Dalam ASR, Bi-LSTM berguna karena ucapan memiliki konteks temporal yang kuat. Bunyi saat ini sering bergantung pada bunyi sebelum dan sesudahnya.

Pada proyek ini, Bi-LSTM diposisikan sebagai:

- baseline klasik pra-Transformer
- pembanding kuat terhadap Transformer Vanilla, ViT-based ASR, dan TDNN-HMM
- model yang relatif stabil dan mudah direproduksi
- pendekatan sequence modeling berbasis CTC

### Implementasi yang Sudah Ada

Folder implementasi:

- `baselines/bilstm_asr/`

File utama:

- `config.py`
- `model.py`
- `dataset.py`
- `train.py`
- `evaluate.py`
- `generate_report.py`
- `preflight.py`
- `README.md`
- `ANALYSIS.md`

### Arsitektur Bi-LSTM yang Ditemukan

Arsitektur dari dokumentasi dan kode:

```text
Input: (B, T, 80) log-mel features
  -> Conv1D Subsampling, 2 layer stride 2, total 4x time reduction
  -> Bi-LSTM Encoder, 4 layers, hidden=512 per direction
  -> LayerNorm + Dropout
  -> Linear Projection, 1024 -> 512
  -> CTC Head, 512 -> vocab_size
  -> CTC Loss / Greedy CTC Decode
```

Parameter utama:

- Input feature: `80` dim log-mel
- Conv channels: `256`
- Conv kernel: `3`
- LSTM layers: `4`
- Hidden size: `512` per direction
- Bidirectional output: `1024`
- Dropout: `0.3`
- Projection: aktif, `1024 -> 512`
- Loss: `CTC`
- Blank ID: `0`, sama dengan PAD
- Optimizer: `AdamW`
- Learning rate default: `3e-4`
- Batch size default: `16`
- Epoch default: `80`
- AMP: aktif
- SpecAugment: aktif

Jumlah parameter aktual dari run yang ditemukan:

- `23,043,984` trainable parameters

### Kompatibilitas Fitur

Baseline Bi-LSTM yang ditemukan memakai fitur:

- `features_retake2026_global/train.pkl`
- `features_retake2026_global/valid.pkl`
- `features_retake2026_global/test.pkl`

Format fitur:

```text
X: List[np.ndarray] dengan bentuk (T, 80)
y: List[List[int]] token ID
fnames: List[str]
text: List[str]
lengths: List[int]
```

Parameter preprocessing fitur:

- Sample rate: `16 kHz`
- `n_fft`: `512`
- `hop_length`: `256`
- `n_mels`: `80`
- Pre-emphasis: `0.97`
- Trim silence: aktif
- Max length: `8.0 sec`
- Normalization: per-utterance mean/variance pada log-mel
- Tokenizer: `spm/spm_char_fixed.model`

Catatan penting untuk `Paper_Datatset_SOTA`:

- Implementasi Bi-LSTM yang ditemukan belum otomatis menunjuk ke `Processed_Balanced19_v3/Dataset_Balanced19`.
- Jika ingin memakai dataset paper final, perlu membuat fitur `.pkl` baru dari dataset final atau membuat konfigurasi terisolasi yang menunjuk ke fitur hasil preprocessing dataset final.
- Jangan mengubah script stable root secara destruktif; lebih aman membuat pipeline/konfigurasi baru yang versioned.

### Hasil Eksperimen Bi-LSTM yang Ditemukan

Run yang ditemukan:

- `baselines/bilstm_asr/runs/train_3`

Ringkasan training:

- Total epoch trained: `30`
- Best validation loss: `0.14228612805906846`
- Total training time: `4h 24m 4s`
- Model params: `23,043,984`

Ringkasan evaluasi greedy:

- Split: `valid`
- Num utterances: `16300`
- Checkpoint: `best.pth`
- Checkpoint epoch: `15`
- WER: `0.020904729266620972`
- CER: `0.01293459234239787`
- Decode time: `76.01129651069641 sec`
- Throughput: `214.4418099447395 utt/sec`

Interpretasi hasil:

- Bi-LSTM menunjukkan hasil sangat kuat pada valid split yang tersedia.
- WER sekitar `2.09%` dan CER sekitar `1.29%` menunjukkan baseline ini sangat layak dijadikan pembanding utama.
- Karena hasilnya sangat baik, perlu dipastikan apakah split evaluasi benar-benar speaker-independent dan tidak mengalami leakage pola kalimat yang sama antar split.
- Untuk paper, Bi-LSTM bisa diposisikan sebagai baseline kuat yang menunjukkan bahwa dataset dapat dipelajari dengan baik oleh model sekuensial klasik.

### Kelebihan Bi-LSTM

- Stabil dan matang untuk data sekuensial audio.
- Cocok dengan fitur `(T, 80)` tanpa reshaping rumit.
- CTC membuat training lebih sederhana dibanding seq2seq autoregressive.
- Dapat dilatih di RTX 4060 8GB dengan aman.
- Hasil eksperimen yang ditemukan sudah sangat baik.
- Cocok sebagai baseline pembanding yang fair terhadap model lain.

### Keterbatasan Bi-LSTM

- Tidak memiliki explicit attention decoder.
- CTC mengasumsikan independensi output bersyarat yang dapat membatasi pemodelan dependensi bahasa.
- Tidak memberikan lokalisasi token eksplisit seperti pendekatan RCNN/T-RCNN.
- Lebih cocok sebagai baseline kuat daripada kontribusi arsitektur baru.

## Posisi RCNN/T-RCNN dalam Proyek

### Catatan Istilah

Dalam workspace, model yang ditemukan bukan RCNN generic biasa, tetapi **T-RCNN ASR**:

- T-RCNN = Temporal Region-based Convolutional Neural Network
- Konsepnya mengadaptasi ide Region-based CNN/Faster R-CNN dari object detection ke domain temporal audio
- Token ucapan diperlakukan sebagai objek temporal yang memiliki boundary start/end

Jadi, untuk paper, istilah yang paling akurat adalah:

- **Temporal RCNN for ASR**
- **T-RCNN ASR**
- **Region-based temporal token detection for ASR**

### Ringkasan Konsep RCNN/T-RCNN

RCNN pada computer vision biasanya bekerja dengan ide:

- mencari kandidat region
- mengambil fitur region
- mengklasifikasikan isi region
- memperbaiki boundary region

Pada ASR, konsep ini diubah menjadi domain waktu:

- region bukan kotak gambar, tetapi segmen waktu audio
- objek bukan benda visual, tetapi token/karakter/subword
- proposal bukan bounding box 2D, tetapi interval temporal `[start, end]`

T-RCNN untuk ASR mencoba menjawab pertanyaan:

> Selain mengetahui apa transkripnya, apakah model juga bisa mengetahui di bagian waktu mana token tersebut muncul?

### Implementasi yang Sudah Ada

Folder implementasi:

- `baselines/trcnn_asr/`

File utama:

- `models/trcnn.py`
- `config.py`
- `datasets.py`
- `train.py`
- `evaluate.py`
- `generate_report.py`
- `preflight.py`
- `utils/alignment.py`
- `utils/decoding.py`
- `utils/metrics.py`
- `utils/profiling.py`
- `README.md`
- `ANALYSIS.md`

### Arsitektur T-RCNN yang Ditemukan

Arsitektur dari dokumentasi dan kode:

```text
Input: (B, T, 80) log-mel features
  -> Temporal Backbone, Conv1D stack, LayerNorm/BatchNorm
  -> CTC Auxiliary Head
  -> Temporal RPN, anchor-based region proposals
  -> ROIAlign1D
  -> Detection Head
      -> token classification
      -> temporal boundary refinement
```

Komponen utama:

- **Temporal Backbone**
  - Conv1D stack untuk ekstraksi fitur temporal
  - Channel default: `[128, 256, 256, 512]`
  - Kernel: `5`
  - Stride awal: `2`

- **CTC Auxiliary Head**
  - Memberikan sinyal training stabil
  - Menjamin model tetap bisa melakukan transkripsi walaupun detection branch belum matang

- **Temporal RPN**
  - Anchor durations default: `[2, 4, 8, 16, 32]`
  - Menghasilkan objectness score dan bbox/interval regression

- **ROIAlign1D**
  - Mengambil fitur fixed-size dari setiap proposal temporal
  - ROI pool size default: `8`

- **Detection Head**
  - Klasifikasi token per proposal
  - Refinement boundary start/end

- **Hybrid Loss**
  - CTC loss weight: `1.0`
  - RPN loss weight: `0.5`
  - Classification loss weight: `1.0`
  - BBox loss weight: `0.5`

### Hyperparameter T-RCNN yang Ditemukan

Dari `config.py`:

- Input dim: `80`
- Backbone channels: `[128, 256, 256, 512]`
- Backbone kernel: `5`
- Backbone stride: `2`
- Anchor durations: `[2, 4, 8, 16, 32]`
- RPN hidden: `256`
- RPN pre-NMS top K: `2000`
- RPN post-NMS top K: `300`
- RPN NMS threshold: `0.7`
- ROI pool size: `8`
- Detection hidden: `512`
- Detection dropout: `0.3`
- Batch size: `8`
- Grad accumulation: `2`
- Effective batch: `16`
- Learning rate: `1e-4`
- Warmup epochs: `5`
- Epoch default: `80`
- AMP: aktif
- SpecAugment: aktif
- Decode mode default: `ctc`

### Hasil Eksperimen T-RCNN yang Ditemukan

Run yang ditemukan:

- `baselines/trcnn_asr/runs/train_6`

Ringkasan training:

- Total epoch trained: `187`
- Best validation loss: `0.8289185865417532`
- Best validation WER selama training: `0.23506330051084623`
- Total training time: `24h 54m 35s`
- Model params: `4,369,329`

Ringkasan evaluasi greedy:

- Split: `valid`
- Num utterances: `16300`
- Checkpoint: `best.pth`
- Checkpoint epoch: `172`
- WER: `0.312145305003427`
- CER: `0.16290525381524124`
- Decode time: `25.08959674835205 sec`
- Throughput: `649.671661266163 utt/sec`

Interpretasi hasil:

- T-RCNN sudah memiliki implementasi dan hasil run yang dapat dirujuk.
- Dari sisi akurasi, hasil valid WER sekitar `31.21%` masih jauh di bawah Bi-LSTM pada run yang ditemukan.
- Dari sisi kecepatan decode, throughput T-RCNN lebih tinggi daripada Bi-LSTM pada evaluasi yang tersedia.
- Nilai riset utama T-RCNN bukan pada performa saat ini, melainkan pada novelty: eksplisit memodelkan region temporal token.
- Untuk paper, T-RCNN lebih cocok dijadikan usulan arsitektur eksperimental/novel, bukan baseline terbaik final jika belum diperbaiki.

### Kelebihan T-RCNN

- Memberikan sudut pandang baru untuk ASR: token sebagai objek temporal.
- Memiliki explicit token localization.
- Kompleksitas temporal cenderung linear terhadap panjang input, tidak kuadratik seperti self-attention penuh.
- CTC auxiliary head menjaga training tetap stabil.
- Dapat menghasilkan artefak tambahan seperti proposal quality, RPN loss, dan boundary prediction.
- Menarik sebagai kontribusi novelty dalam paper.

### Keterbatasan T-RCNN

- Membutuhkan alignment target yang baik agar detection branch efektif.
- Saat ini memakai pseudo-alignment, sehingga target boundary masih kasar.
- Hasil WER valid run yang ditemukan masih lebih buruk daripada Bi-LSTM.
- Training lebih kompleks karena multi-loss: CTC, RPN, classification, bbox.
- Proposal-based decoding belum tentu matang dibanding CTC/attention decoding.
- Butuh tuning lebih lanjut sebelum dapat diklaim sebagai model unggulan.

## Perbandingan Bi-LSTM vs T-RCNN

| Aspek | Bi-LSTM CTC | T-RCNN ASR |
|---|---:|---:|
| Tujuan utama | Baseline klasik kuat | Arsitektur novel berbasis detection |
| Input | `(T, 80)` log-mel | `(T, 80)` log-mel |
| Decoder utama | CTC greedy/beam | CTC default, proposal/hybrid opsional |
| Temporal localization | Implisit | Eksplisit melalui proposal region |
| Loss | CTC | CTC + RPN + classification + bbox |
| Parameter aktual run | `23,043,984` | `4,369,329` |
| Run yang ditemukan | `bilstm_asr/runs/train_3` | `trcnn_asr/runs/train_6` |
| Valid WER | `0.0209` | `0.3121` |
| Valid CER | `0.0129` | `0.1629` |
| Throughput eval | `214.44 utt/sec` | `649.67 utt/sec` |
| Kematangan | Tinggi | Eksperimental |
| Posisi paper | Baseline pembanding kuat | Usulan/novel contribution atau future work |

## Rekomendasi Narasi untuk Paper

### Narasi 1: Bi-LSTM sebagai Baseline Kuat

Bi-LSTM dapat dipakai sebagai baseline utama karena:

- arsitektur sudah mapan untuk ASR
- pipeline training/evaluasi sudah tersedia
- hasil validasi yang ditemukan sangat baik
- cocok sebagai pembanding terhadap Transformer/ViT/Kaldi

Contoh narasi:

> Bi-LSTM with CTC is included as a strong recurrent baseline to evaluate whether the proposed balanced Indonesian speech dataset can be modeled effectively using a classical sequence architecture. The model uses the same log-mel features and tokenizer as other neural baselines, enabling a controlled comparison.

### Narasi 2: T-RCNN sebagai Usulan Novel

T-RCNN dapat dibahas sebagai arsitektur eksploratif karena:

- mengadaptasi region proposal/object detection ke domain ASR
- memberikan explicit token temporal localization
- punya nilai kebaruan dibanding CTC/attention standar
- cocok sebagai arah penelitian lanjutan

Contoh narasi:

> We also investigate a Temporal Region-based CNN architecture that treats speech tokens as temporal objects. The model combines a Conv1D acoustic backbone, temporal region proposal network, ROIAlign1D, detection head, and an auxiliary CTC objective. This design allows transcription learning while simultaneously exploring token-level temporal localization.

### Narasi 3: Dataset Quality dan Mismatch Whisper

Karena `Paper_Datatset_SOTA` sudah memiliki hasil verifikasi Whisper, bagian ini dapat dikaitkan dengan pemilihan algoritma:

- Bi-LSTM dapat digunakan untuk mengukur baseline performa setelah dataset dibersihkan.
- T-RCNN berpotensi membantu mendeteksi segmentasi/token yang bermasalah jika alignment diperbaiki.
- Mismatch sistematis dari Whisper dapat menjadi motivasi untuk model yang memahami lokasi temporal token.

Contoh narasi:

> The Whisper-based verification identified a small subset of likely sentence-order mismatches. While the final dataset is structurally valid, this motivates future modeling approaches that can reason not only about transcription accuracy but also about temporal token alignment and sentence-level consistency.

## Rekomendasi Eksperimen untuk Paper_Datatset_SOTA

### Tahap 1: Siapkan Fitur dari Dataset Final

Karena baseline yang ditemukan saat ini menunjuk ke `features_retake2026_global`, perlu dibuat fitur khusus untuk dataset final jika ingin benar-benar memakai `Paper_Datatset_SOTA`.

Input dataset final:

- `Processed_Balanced19_v3/Dataset_Balanced19`

Output yang direkomendasikan:

- manifest train/valid/test
- fitur `.pkl` train/valid/test
- tokenizer SentencePiece yang konsisten
- report preprocessing

Rekomendasi split:

- gunakan speaker-independent split jika memungkinkan
- hindari leakage respondent antara train dan test
- simpan split dalam manifest agar reproducible

### Tahap 2: Jalankan Bi-LSTM sebagai Baseline Utama

Tujuan:

- memperoleh baseline kuat pada dataset final paper
- mengukur WER/CER dengan setup sederhana dan reproducible

Hal yang perlu dilaporkan:

- total parameter
- train time
- best epoch
- valid/test WER
- valid/test CER
- throughput decode
- GPU memory
- loss curve
- WER/CER curve

### Tahap 3: Jalankan T-RCNN sebagai Eksperimen Novel

Tujuan:

- mengevaluasi apakah pendekatan region proposal temporal dapat bekerja pada dataset final
- mengukur gap performa terhadap Bi-LSTM
- mengevaluasi stabilitas CTC auxiliary dan detection loss

Hal yang perlu dilaporkan:

- WER/CER CTC decode
- RPN loss
- classification loss
- bbox loss
- proposal quality jika tersedia
- throughput decode
- contoh prediksi benar/salah

### Tahap 4: Perbaikan T-RCNN yang Direkomendasikan

Jika T-RCNN ingin dijadikan kontribusi utama, perbaikan yang disarankan:

- gunakan CTC-guided Viterbi alignment setelah warmup CTC
- latih detection branch setelah CTC head cukup stabil
- lakukan ablation loss weight:
  - CTC-only
  - CTC + RPN
  - CTC + RPN + classification
  - full CTC + RPN + classification + bbox
- coba anchor durations berbeda untuk token char/subword
- bandingkan decode mode:
  - CTC
  - proposal
  - hybrid
- gunakan speaker-independent test set untuk klaim final

## Rekomendasi Posisi Akhir

### Jika target paper adalah performa terbaik

Gunakan:

- **Bi-LSTM CTC** sebagai baseline kuat
- bandingkan dengan ViT/Transformer/Kaldi jika tersedia
- T-RCNN hanya sebagai eksperimen tambahan/future work

Alasan:

- Bi-LSTM run yang ditemukan jauh lebih baik dari T-RCNN dalam WER/CER.
- Hasil Bi-LSTM lebih siap dijadikan pembanding performa.

### Jika target paper adalah kontribusi arsitektur baru

Gunakan:

- **T-RCNN ASR** sebagai usulan novel
- Bi-LSTM sebagai baseline pembanding
- tekankan novelty temporal region proposal dan token localization

Syarat:

- T-RCNN perlu ditingkatkan agar gap WER tidak terlalu besar
- perlu eksperimen alignment dan ablation
- perlu visualisasi proposal/token localization agar kontribusinya jelas

### Jika target paper adalah dataset paper SOTA

Gunakan:

- Bi-LSTM untuk menunjukkan dataset dapat menghasilkan performa ASR kuat
- T-RCNN sebagai arah eksplorasi tambahan
- Whisper verification sebagai validasi kualitas dataset
- laporan mismatch sebagai bagian quality assurance dataset

## Usulan Struktur Subbab Paper

### Opsi struktur untuk bagian metode

```text
3. Methodology
   3.1 Dataset Preparation and Balancing
   3.2 Whisper-based Dataset Verification
   3.3 Acoustic Feature Extraction
   3.4 Bi-LSTM CTC Baseline
   3.5 Temporal RCNN ASR Model
   3.6 Evaluation Metrics
```

### Opsi struktur untuk bagian eksperimen

```text
4. Experiments
   4.1 Experimental Setup
   4.2 Dataset Split Strategy
   4.3 Baseline Models
   4.4 Bi-LSTM Results
   4.5 Temporal RCNN Results
   4.6 Error Analysis
   4.7 Discussion of Whisper Mismatch Findings
```

### Opsi struktur untuk bagian diskusi

```text
5. Discussion
   5.1 Impact of Balanced Sentence Categories
   5.2 Recurrent vs Detection-based Modeling
   5.3 Dataset Noise and Label Consistency
   5.4 Limitations and Future Work
```

## Draft Ringkas Deskripsi Algoritma

### Draft Bi-LSTM

Bi-LSTM is a recurrent neural network architecture designed to model sequential dependencies in both forward and backward temporal directions. In this ASR setup, log-mel acoustic features are first reduced using a Conv1D subsampling frontend, then passed through stacked bidirectional LSTM layers. The final encoder representation is projected and optimized using Connectionist Temporal Classification. This allows the model to learn speech-to-token alignment without requiring frame-level annotations.

### Draft T-RCNN

T-RCNN adapts region-based object detection principles to speech recognition by treating output tokens as temporal objects. A Conv1D temporal backbone extracts acoustic representations, while a temporal region proposal network generates candidate token intervals. ROIAlign1D pools fixed-size features from each temporal proposal, and a detection head classifies tokens and refines their boundaries. An auxiliary CTC head is used to stabilize transcription learning in the absence of exact token-level alignment.

## Risiko yang Perlu Dicatat

- Hasil Bi-LSTM yang sangat baik perlu divalidasi pada split test yang benar-benar independen.
- T-RCNN masih eksperimental dan performanya belum setara Bi-LSTM.
- Baseline saat ini memakai `features_retake2026_global`, sehingga perlu adaptasi jika targetnya benar-benar dataset `Processed_Balanced19_v3`.
- `465 likely_mismatch` dari verifikasi Whisper harus diperlakukan sebagai potensi noise label kecil.
- Jika mismatch tidak difilter, metrik model bisa sedikit terpengaruh.
- Jika mismatch difilter, jumlah data berkurang kecil tetapi kualitas label meningkat.

## Kesimpulan

Berdasarkan artefak yang ditemukan:

- **Bi-LSTM CTC** adalah baseline paling siap dan paling kuat untuk dilaporkan.
- **T-RCNN/Temporal RCNN** adalah arsitektur yang lebih novel, tetapi masih perlu tuning dan alignment improvement.
- Untuk proyek `Paper_Datatset_SOTA`, pendekatan terbaik adalah menggunakan Bi-LSTM sebagai baseline utama dan T-RCNN sebagai eksperimen tambahan atau kontribusi eksploratif.
- Dataset final `Processed_Balanced19_v3` sudah layak menjadi dasar eksperimen, dengan catatan mismatch hasil Whisper perlu dipertimbangkan dalam skenario training/evaluasi.

## File Rujukan Penting

Untuk membaca detail lebih lanjut, gunakan urutan berikut:

- `Paper_Datatset_SOTA/transfer_prompt_paper_dataset.md`
- `Paper_Datatset_SOTA/Processed_Balanced19_v3/FINAL_RESUME.md`
- `Paper_Datatset_SOTA/Whisper_Verification/run_20260403_221557/whisper_report.md`
- `Paper_Datatset_SOTA/Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_report.md`
- `baselines/bilstm_asr/README.md`
- `baselines/bilstm_asr/ANALYSIS.md`
- `baselines/bilstm_asr/model.py`
- `baselines/bilstm_asr/runs/train_3/eval_greedy/summary.json`
- `baselines/trcnn_asr/README.md`
- `baselines/trcnn_asr/ANALYSIS.md`
- `baselines/trcnn_asr/models/trcnn.py`
- `baselines/trcnn_asr/runs/train_6/eval_greedy/summary.json`

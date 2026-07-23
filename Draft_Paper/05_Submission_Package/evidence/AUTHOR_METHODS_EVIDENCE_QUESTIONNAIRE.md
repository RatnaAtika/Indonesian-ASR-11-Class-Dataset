# NSS-ID Author Methods and Release-Evidence Questionnaire

**Status:** **NOT FOR SUBMISSION OR PUBLIC RELEASE**  
**Purpose:** obtain primary evidence and author/institution decisions needed to convert the internal evidence-led draft into a reproducible, ethically releasable data article.  
**Response languages:** English, Bahasa Indonesia, or both.  
**Evidence rule:** classify each answer as **OBSERVED, INFERRED, CONFLICTED, or MISSING**. A source-manuscript statement is an observed author assertion only; an **author-draft assertion is not proof that the event occurred**.

## Secure-response instructions

1. Do not place the private respondent crosswalk, participant names, signatures, phone numbers, personal email addresses, consent scans, identity documents, or other direct identifiers in Git, Hugging Face, the manuscript folder, or this form.
2. **Do not place the private respondent crosswalk** in any response artifact. It must remain separately governed and access-controlled.
3. For sensitive evidence, provide only a public-safe evidence record here: artifact type, date, responsible custodian, redacted identifier, SHA-256, verification outcome, and approved wording. Transfer the primary record only through the institutionally approved secure channel.
4. Do not guess. Use `MISSING` when the evidence does not exist, `CONFLICTED` when records disagree, and `INFERRED` only when the inference and its limitations are explicit.
5. A proposed sentence is not approved until the responsible author/institutional owner signs off and all affected metadata, tables, figures, manifests, checksums, DOCX/XLSX files, and audits are regenerated.

## Response template for every item

```text
Question ID:
Classification: OBSERVED / INFERRED / CONFLICTED / MISSING
English response:
Jawaban Bahasa Indonesia:
Primary artifact:
Artifact date:
Evidence custodian/owner:
Redacted record or reference number:
SHA-256:
Verification performed by/date:
Approved wording:
Approved by/date:
Privacy or access restriction:
Downstream artifacts that must be regenerated:
```

## Conflicts that must not be silently harmonized

- **Room dimensions:** the source text reports **1 × 1 × 2.5 m**, while embedded diagrams show **approximately 1.5037 m × 2.5027 m** and a height near 2.5027 m.
- **Participant age:** the source draft gives both **25–38** and **22–38** years.
- **Sex/gender-label counts:** a later metadata correction yields 12 male/8 female labels, while stale artifacts report 11/9; label definition and provenance are absent.
- **Repetition design:** the older balanced tree supports 19 retained IDs × 25 takes, but the repaired release target has 213 category-ID pairs with partial replacements; universal completion and controlled variation are not established.
- **Dataset scope:** the release target is 104,500 files; the frozen benchmark is 102,544 files. They are different states.

# A. Authors and title-page authority

## Q001 — Corresponding author

**Gap token:** `[MATERIAL GAP: corresponding author name and current email]`

- **English:** Who is authorized to serve as corresponding author? Provide the institutionally approved name, current professional email, postal contact, and ORCID if approved. Do not place private contact data in a public artifact until publication use is authorized.
- **Bahasa Indonesia:** Siapa yang berwenang menjadi penulis korespondensi? Berikan nama yang disetujui institusi, surel profesional aktif, alamat korespondensi, dan ORCID jika disetujui. Jangan memasukkan data kontak privat ke artefak publik sebelum penggunaannya disahkan.

## Q002 — Final author order and affiliations

**Gap token:** `[MATERIAL GAP: final author order and affiliations]`

- **English:** Confirm final author order, exact affiliation names/addresses, and whether every listed person satisfies authorship criteria.
- **Bahasa Indonesia:** Konfirmasikan urutan penulis final, nama/alamat afiliasi yang tepat, dan apakah setiap nama memenuhi kriteria kepengarangan.

# B. Participants, recruitment, and human-subject governance

## Q003 — Recruitment and eligibility

**Gap token:** `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`

- **English:** How were the 20 participants approached and selected? State source population, recruitment route, inclusion/exclusion criteria, language proficiency criterion, whether one label represents one distinct person, compensation, and observed exclusions. Supply the approved protocol or a dated author attestation grounded in contemporaneous records.
- **Bahasa Indonesia:** Bagaimana 20 partisipan dihubungi dan dipilih? Jelaskan populasi sumber, jalur rekrutmen, kriteria inklusi/eksklusi, kriteria kemahiran bahasa, apakah satu label mewakili satu orang yang berbeda, kompensasi, dan eksklusi yang terjadi. Lampirkan protokol yang disetujui atau pernyataan penulis bertanggal berdasarkan catatan sezaman.

## Q004 — Age or omission

**Gap token:** `[MATERIAL GAP: participant age or approved omission]`

- **English:** Resolve the 25–38 versus 22–38 conflict using a primary record. Was age collected as exact age, range, or not at all? Is publication necessary, consented, and privacy-safe? If not, approve omission.
- **Bahasa Indonesia:** Selesaikan konflik rentang 25–38 dan 22–38 menggunakan catatan primer. Apakah usia dicatat sebagai usia tepat, rentang, atau tidak dicatat? Apakah publikasinya diperlukan, dicakup persetujuan, dan aman bagi privasi? Jika tidak, setujui penghapusan informasi usia.

## Q005 — Sex/gender label definition and provenance

**Gap token:** `[MATERIAL GAP: sex/gender label definition and provenance]`

- **English:** Define the field: sex, gender, voice-source label, or another construct. Was it self-described, administratively recorded, or inferred? Who corrected one label, when, from what primary record, and with what authority? Confirm whether the field should be retained publicly.
- **Bahasa Indonesia:** Definisikan bidang tersebut: jenis kelamin biologis, gender, label sumber suara, atau konstruk lain. Apakah dilaporkan sendiri, dicatat secara administratif, atau diinferensikan? Siapa yang mengoreksi satu label, kapan, berdasarkan catatan primer apa, dan dengan kewenangan apa? Konfirmasikan apakah bidang ini perlu dipertahankan secara publik.

## Q006 — Ethics determination

**Gap token:** `[MATERIAL GAP: ethics committee/determination, reference number, and date]`

- **English:** Identify the competent committee/institution and provide the approval, exemption, waiver, or other determination type, reference number, date, protocol title/version, and scope. Do not write that approval was unnecessary without a competent documented determination.
- **Bahasa Indonesia:** Identifikasikan komite/institusi yang berwenang dan berikan jenis persetujuan, pengecualian, pembebasan, atau keputusan lain, nomor referensi, tanggal, judul/versi protokol, dan cakupannya. Jangan menyatakan bahwa persetujuan tidak diperlukan tanpa keputusan terdokumentasi dari pihak berwenang.

## Q007 — Informed consent and public voice reuse

**Gap token:** `[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`

- **English:** Describe when/how consent was obtained and retained. Quote or securely verify the clauses covering recording, publication, repository access, redistribution, commercial/non-commercial use, model training, derivatives, synthetic/voice-cloning uses, future research, and withdrawal limits. State whether re-consent is required.
- **Bahasa Indonesia:** Jelaskan kapan/bagaimana persetujuan diperoleh dan disimpan. Kutip atau verifikasi secara aman klausul yang mencakup perekaman, publikasi, akses repositori, redistribusi, penggunaan komersial/nonkomersial, pelatihan model, karya turunan, penggunaan sintetis/kloning suara, penelitian mendatang, dan batas penarikan. Nyatakan apakah persetujuan ulang diperlukan.

## Q008 — Demographic minimization and public schema

**Gap token:** `[MATERIAL GAP: demographic minimization and public-schema decision]`

- **English:** Which participant attributes are scientifically necessary, consented, accurate, and safe to release? Approve retention, aggregation, suppression, or deletion for age, locality, region, accent/dialect, and sex/gender labels. Do not infer dialect from locality.
- **Bahasa Indonesia:** Atribut partisipan mana yang diperlukan secara ilmiah, tercakup persetujuan, akurat, dan aman untuk dirilis? Setujui penyimpanan, agregasi, penyamaran, atau penghapusan usia, lokasi, wilayah, aksen/dialek, dan label jenis kelamin/gender. Jangan menyimpulkan dialek hanya dari lokasi.

## Q009 — Voice-data lifecycle governance

**Gap token:** `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`

- **English:** Name the institutional data controller and public contact. Define crosswalk custodian/access, retention/destruction, withdrawal and takedown workflow, breach response, release-version corrections, repository maintenance, and who can authorize changes. State residual recognition/linkage risk for pseudonymous, voice-identifiable data.
- **Bahasa Indonesia:** Sebutkan pengendali data institusional dan kontak publik. Definisikan pengelola/akses crosswalk, retensi/pemusnahan, alur penarikan dan penghapusan, respons insiden, koreksi versi rilis, pemeliharaan repositori, dan pihak yang berwenang menyetujui perubahan. Nyatakan risiko pengenalan/keterhubungan yang tersisa pada data suara berpseudonim dan tetap dapat diidentifikasi melalui suara.

# C. Recording environment and session protocol

## Q010 — Recording dates and sessions

**Gap token:** `[MATERIAL GAP: recording dates and session protocol]`

- **English:** Provide date range, number of sessions per participant, session duration, breaks, operator role, recording order, fatigue controls, interruptions, and whether all sessions used the same room/equipment/procedure. Supply collection logs where available.
- **Bahasa Indonesia:** Berikan rentang tanggal, jumlah sesi per partisipan, durasi sesi, jeda, peran operator, urutan perekaman, pengendalian kelelahan, gangguan, serta apakah semua sesi memakai ruangan/peralatan/prosedur yang sama. Lampirkan log pengumpulan jika tersedia.

## Q011 — Room dimensions and treatment

**Gap token:** `[MATERIAL GAP: verified room dimensions and treatment]`

- **English:** Resolve the text/diagram conflict using a dated measurement, floor plan, facilities record, or authorized attestation. Identify wall/ceiling/floor treatment and whether acoustic attenuation, reverberation, or background noise was actually measured. If not measured, approve bounded descriptive wording only.
- **Bahasa Indonesia:** Selesaikan konflik teks/diagram dengan pengukuran bertanggal, denah, catatan fasilitas, atau pernyataan resmi. Identifikasikan perlakuan dinding/plafon/lantai dan apakah peredaman, reverberasi, atau kebisingan latar benar-benar diukur. Jika tidak diukur, setujui hanya deskripsi yang terbatas.

## Q012 — Equipment and software chain

**Gap token:** `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]`

- **English:** Verify microphone manufacturer/model/serial or asset record, polar pattern, interface/adapter/recorder, computer, operating system, recording application/version, driver, and native acquisition format. Were any files later converted or resampled?
- **Bahasa Indonesia:** Verifikasi produsen/model mikrofon/nomor seri atau catatan aset, pola arah, antarmuka/adaptor/perekam, komputer, sistem operasi, aplikasi/versi perekaman, driver, dan format akuisisi asli. Apakah file kemudian dikonversi atau di-resample?

## Q013 — Microphone geometry and level control

**Gap token:** `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]`

- **English:** Confirm microphone-to-mouth distance and how it was maintained; orientation; stand/pop filter; input gain; automatic gain control; calibration/reference level if any; clipping/level monitoring; and room-noise check. Also describe prompt display medium, operator cues, and prompt order.
- **Bahasa Indonesia:** Konfirmasikan jarak mikrofon-ke-mulut dan cara mempertahankannya; orientasi; penyangga/pop filter; gain input; penguatan otomatis; kalibrasi/level referensi jika ada; pemantauan clipping/level; serta pemeriksaan kebisingan ruangan. Jelaskan juga media tampilan prompt, aba-aba operator, dan urutan prompt.

## Q014 — Repetitions, replacements, retakes, and rejection

**Gap token:** `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]`

- **English:** Define what a “take” means. State intended repetitions per prompt, whether order was fixed/randomized, instructions for rate/intonation/volume, retake triggers, maximum attempts, acceptance authority, observed re-record counts, removed prompt IDs, balancing/replacement decisions, and why four ID-20 partial replacement groups occur.
- **Bahasa Indonesia:** Definisikan arti “take”. Nyatakan jumlah pengulangan yang direncanakan per prompt, apakah urutan tetap/acak, instruksi terkait tempo/intonasi/volume, pemicu rekam ulang, jumlah percobaan maksimum, pihak yang menyetujui, jumlah rekam ulang yang terjadi, ID prompt yang dihapus, keputusan penyeimbangan/penggantian, dan alasan munculnya empat kelompok penggantian parsial ID-20.

# D. Prompts, segmentation, transcripts, and metadata

## Q015 — Prompt source, rights, categories, and presentation

**Related gap tokens:** `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`; `[MATERIAL GAP: transcript source and normalization specification]`

- **English:** Who authored each prompt, from what source/version, under what rights? How were the 11 categories defined and reviewed? Were they organizational labels or linguistically validated annotations? Provide the exact prompt inventory used at collection and the presentation/order procedure.
- **Bahasa Indonesia:** Siapa yang menulis setiap prompt, dari sumber/versi apa, dan dengan hak apa? Bagaimana 11 kategori didefinisikan dan ditinjau? Apakah hanya label organisasi atau anotasi yang divalidasi secara linguistik? Berikan inventaris prompt tepat yang digunakan saat pengumpulan dan prosedur penyajian/urutannya.

## Q016 — Segmentation, filenames, and transcript specification

**Gap token:** `[MATERIAL GAP: transcript source and normalization specification]`

- **English:** Explain whether recording was utterance-by-utterance or continuous; segmentation boundaries and silence padding; tool/version; filename grammar; speaker/category/take/sentence mapping; transcript source; Unicode normalization; casing; punctuation; numerals; abbreviations; whitespace; disfluencies; noise/non-speech tags; and alignment checks.
- **Bahasa Indonesia:** Jelaskan apakah perekaman dilakukan per ujaran atau kontinu; batas segmentasi dan padding hening; alat/versi; tata nama file; pemetaan pembicara/kategori/take/kalimat; sumber transkrip; normalisasi Unicode; kapitalisasi; tanda baca; angka; singkatan; spasi; disfluensi; tag kebisingan/nonucapan; dan pemeriksaan keselarasan.

## Q017 — Transcript repair evidence

**Gap token:** `[MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result]`

- **English:** Provide the executable algorithm that filled 1,956 blank fields: exact input revisions/hashes, source precedence, join keys, ambiguity handling, normalizer, repaired-row manifest, before/after hashes, assertions, reviewer, and audio–text listening-audit design/results. Confirm that audio shards were unchanged.
- **Bahasa Indonesia:** Berikan algoritme yang dapat dijalankan untuk mengisi 1.956 bidang kosong: revisi/hash input tepat, prioritas sumber, kunci join, penanganan ambiguitas, normalizer, manifes baris yang diperbaiki, hash sebelum/sesudah, assertion, peninjau, serta desain/hasil audit dengar audio–teks. Konfirmasikan bahwa shard audio tidak berubah.

## Q018 — Metadata generation and validation

**Closure parent:** `[MATERIAL GAP: transcript source and normalization specification]`, sub-gate `SG-METADATA-BUILD`

- **English:** Identify the script and software versions that generated duration, sample rate, channel, bit depth, sample count, file size, source type, split, and public IDs. Supply schema, allowed values, nullability, units, validation rules, input hashes, and observed failures/corrections. Remove absolute paths and private labels from public metadata.
- **Bahasa Indonesia:** Identifikasikan skrip dan versi perangkat lunak yang menghasilkan durasi, sample rate, kanal, bit depth, jumlah sampel, ukuran file, tipe sumber, split, dan ID publik. Berikan skema, nilai yang diizinkan, nullability, satuan, aturan validasi, hash input, serta kegagalan/koreksi yang terjadi. Hapus path absolut dan label privat dari metadata publik.

# E. Quality control and acoustic diagnostics

## Q019 — Collection and file-level QC

**Closure parents:** `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]` and `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`, sub-gate `SG-AUDIO-QC`

- **English:** List automated and human checks performed during and after collection: file readability, expected counts, headers, duration, clipping, silence, background noise, duplicates, prompt match, pronunciation, transcript alignment, rejection/retake criteria, assessor training, disagreement handling, and item-level outcomes. Distinguish a full-corpus check from a sample.
- **Bahasa Indonesia:** Daftarkan pemeriksaan otomatis dan manusia saat serta setelah pengumpulan: keterbacaan file, jumlah yang diharapkan, header, durasi, clipping, keheningan, kebisingan latar, duplikasi, kecocokan prompt, pelafalan, keselarasan transkrip, kriteria penolakan/rekam ulang, pelatihan penilai, penanganan perbedaan, dan hasil per item. Bedakan pemeriksaan seluruh korpus dari pemeriksaan sampel.

## Q020 — Provenance of the 297-file diagnostic sample

**Gap token:** `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]`

- **English:** Provide the complete eligible frame, source dataset revision, allocation by category/speaker/source/split, deterministic ordering, random algorithm/library/version, seed, inclusion/exclusion rules, selected relative paths/public IDs, selection script, manifest hash, and handling of failed reads. Confirm whether 27 rows per category was designed before selection.
- **Bahasa Indonesia:** Berikan kerangka sampel yang memenuhi syarat, revisi dataset sumber, alokasi menurut kategori/pembicara/sumber/split, urutan deterministik, algoritme/library/versi acak, seed, aturan inklusi/eksklusi, path relatif/ID publik terpilih, skrip seleksi, hash manifes, dan penanganan file gagal dibaca. Konfirmasikan apakah 27 baris per kategori ditetapkan sebelum seleksi.

# F. Synthetic repair and split generation

## Q021 — Edge-TTS generation and rights

**Gap token:** `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]`

- **English:** Supply provider/library/version, generation dates, account/region if relevant and safe, exact voice IDs, command/configuration, input text and target mapping, rate/pitch/volume, output format, resampling/post-processing, retry/selection rules, automated/listening QC, generated/retained/rejected counts, and legal review of input/output redistribution. Confirm whether any cloning or adaptation was used.
- **Bahasa Indonesia:** Berikan penyedia/library/versi, tanggal pembuatan, akun/wilayah jika relevan dan aman, ID suara tepat, perintah/konfigurasi, teks input dan pemetaan target, rate/pitch/volume, format output, resampling/pasca-pemrosesan, aturan percobaan ulang/seleksi, QC otomatis/dengar, jumlah dibuat/dipertahankan/ditolak, serta tinjauan hukum redistribusi input/output. Konfirmasikan apakah ada kloning atau adaptasi suara.

## Q022 — Two source/target mismatch rows

**Gap token:** `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]`

- **English:** Select one documented action: regenerate with an approved source voice, exclude the rows, or retain them with explicit mismatch flags and rationale. Identify every affected row and approve regeneration of manifests, statistics, figures, checksums, and benchmark sensitivity results.
- **Bahasa Indonesia:** Pilih satu tindakan terdokumentasi: buat ulang dengan sumber suara yang disetujui, keluarkan baris tersebut, atau pertahankan dengan flag ketidakcocokan dan alasan eksplisit. Identifikasikan semua baris terdampak dan setujui pembuatan ulang manifes, statistik, gambar, checksum, serta hasil sensitivitas benchmark.

## Q023 — Split-generation reproducibility

**Gap token:** `[MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]`

- **English:** Provide the executed generator, source revision/hash, eligible human IDs, deterministic candidate ordering, assignment algorithm, seed 42 use, RNG/library/version, constraints, exact assignments, row manifests, output hashes, and assertions. State separately whether human IDs, prompts, sessions, source recordings, and TTS provider voices are disjoint.
- **Bahasa Indonesia:** Berikan generator yang dijalankan, revisi/hash sumber, ID manusia yang memenuhi syarat, urutan kandidat deterministik, algoritme penetapan, penggunaan seed 42, RNG/library/versi, batasan, penetapan tepat, manifes baris, hash output, dan assertion. Nyatakan secara terpisah apakah ID manusia, prompt, sesi, rekaman sumber, dan suara penyedia TTS saling terpisah.

## Q024 — Exact template-overlap audit

**Gap token:** `[MATERIAL GAP: exact benchmark template-overlap audit]`, sub-gate `SG-BENCHMARK-METHODS`

- **English:** Attach a pinned script/report comparing normalized transcript templates across train, development, and test for both release-target and frozen scopes. Define normalizer, template key, item counts, pair counts, overlap counts, hashes, and the approved “seen-script” wording. Attach every per-recipe method card, atomic checkpoint/tokenizer/prediction hashes, scorer environment, synthetic-excluded sensitivity, dependence-aware uncertainty, and systematic error analysis before promoting Supplementary Table S6.
- **Bahasa Indonesia:** Lampirkan skrip/laporan tetap yang membandingkan template transkrip ternormalisasi antar train, development, dan test untuk cakupan release-target dan frozen. Definisikan normalizer, kunci template, jumlah item, jumlah pasangan, jumlah overlap, hash, dan redaksi “seen-script” yang disetujui.

# G. Rights, access, privacy audit, and prior publication

## Q025 — Rights clearance

**Gap token:** `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`

- **English:** For each component, identify owner, third-party material, permission/consent basis, redistribution scope, derivative/model-training rights, restrictions, and approving legal/institutional authority. The related article's licence does not automatically license dataset components.
- **Bahasa Indonesia:** Untuk setiap komponen, identifikasikan pemilik, materi pihak ketiga, dasar izin/persetujuan, cakupan redistribusi, hak karya turunan/pelatihan model, pembatasan, serta otoritas hukum/institusi yang menyetujui. Lisensi artikel terkait tidak otomatis melisensikan komponen dataset.

## Q026 — Dataset and component licences

**Gap token:** `[MATERIAL GAP: exact dataset licence or component-specific licences]`

- **English:** Approve exact machine-readable licence identifiers and text for audio, prompts/transcripts, metadata, code, figures, and synthetic outputs, consistent with consent and third-party terms. If one licence cannot cover all components, provide a component map.
- **Bahasa Indonesia:** Setujui pengenal dan teks lisensi yang dapat dibaca mesin untuk audio, prompt/transkrip, metadata, kode, gambar, dan keluaran sintetis, sesuai persetujuan dan ketentuan pihak ketiga. Jika satu lisensi tidak mencakup semua komponen, berikan peta lisensi per komponen.

## Q027 — Repository, version, DOI, checksums, and access test

**Gap token:** `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`

- **English:** After all release gates close, provide repository, final title/version/date, persistent dataset DOI, direct URL, archive/revision identifier, complete SHA-256 manifest, component licences, and a clean unauthenticated-session access result. Do not present private staging as final availability.
- **Bahasa Indonesia:** Setelah seluruh gerbang rilis terpenuhi, berikan repositori, judul/versi/tanggal final, DOI dataset persisten, URL langsung, pengenal arsip/revisi, manifes SHA-256 lengkap, lisensi komponen, dan hasil uji akses dari sesi bersih tanpa autentikasi. Jangan menyajikan staging privat sebagai ketersediaan final.

## Q028 — Controlled access, if public release is not permitted

**Gap token:** `[MATERIAL GAP: approved controlled-access mechanism, if applicable]`

- **English:** If consent/privacy prevents open access, identify the institutionally governed request process, eligibility criteria, data-use agreement, identity/affiliation checks, secure delivery/analysis environment, reviewer access, decision authority, response time, revocation, audit logs, and written journal/editor approval.
- **Bahasa Indonesia:** Jika persetujuan/privasi mencegah akses terbuka, identifikasikan proses permohonan yang dikelola institusi, kriteria kelayakan, perjanjian penggunaan data, pemeriksaan identitas/afiliasi, lingkungan pengiriman/analisis aman, akses reviewer, otoritas keputusan, waktu respons, pencabutan, log audit, dan persetujuan tertulis jurnal/editor.

## Q029 — Whole-package identity/leakage audit

**Gap token:** `[MATERIAL GAP: final whole-package identity/leakage audit]`

- **English:** Approve and run an audit over archive paths/names, metadata values, audio tags, embedded images and OCR, document properties, PDFs, comments/revisions, logs, notebooks, code outputs, absolute paths, contact fields, secrets, and public-ID ranges. Record tool versions, findings, remediation, final hashes, and sign-off.
- **Bahasa Indonesia:** Setujui dan jalankan audit terhadap path/nama arsip, nilai metadata, tag audio, gambar tertanam dan OCR, properti dokumen, PDF, komentar/revisi, log, notebook, keluaran kode, path absolut, bidang kontak, rahasia, dan rentang ID publik. Catat versi alat, temuan, perbaikan, hash final, dan persetujuan.

## Q030 — Prior-publication overlap and eligibility

**Gap token:** `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]`

- **English:** Provide release/analysis chronology and exact row-level intersection between the earlier approximately 80,000-file state, the 102,544-file benchmark, and the 104,500-file release target. Inventory reused figures, tables, text, methods, predictions, and results; obtain co-author and journal/editor eligibility confirmation.
- **Bahasa Indonesia:** Berikan kronologi rilis/analisis dan irisan baris yang tepat antara kondisi terdahulu sekitar 80.000 file, benchmark 102.544 file, dan release target 104.500 file. Inventarisasikan gambar, tabel, teks, metode, prediksi, dan hasil yang digunakan kembali; dapatkan konfirmasi kelayakan dari seluruh penulis dan jurnal/editor.

# H. Declarations and final authorization

## Q031 — CRediT, funding, interests, and acknowledgements

**Gap tokens:** `[MATERIAL GAP: CRediT roles approved by every author]`; `[MATERIAL GAP: funding and sponsor role]`; `[MATERIAL GAP: competing-interest declaration approved by every author]`; `[MATERIAL GAP: acknowledgements]`

- **English:** Obtain every author's approval for CRediT roles and competing-interest disclosure. Verify funder/grant and sponsor role or an author-approved no-specific-funding statement. Identify non-author contributions and permissions for acknowledgements.
- **Bahasa Indonesia:** Dapatkan persetujuan setiap penulis untuk peran CRediT dan pengungkapan kepentingan. Verifikasi pendana/hibah dan peran sponsor atau pernyataan tanpa pendanaan khusus yang disetujui penulis. Identifikasikan kontribusi nonpenulis dan izin untuk ucapan terima kasih.

## Q032 — GenAI manuscript-preparation declaration

**Gap token:** `[MATERIAL GAP: GenAI manuscript-preparation determination and declaration]`

- **English:** Authors must decide whether current Elsevier policy requires a declaration. If required, record tool/service, purpose, affected tasks, human checking/editing, and author responsibility. Keep this separate from Edge-TTS data generation.
- **Bahasa Indonesia:** Para penulis harus menentukan apakah kebijakan Elsevier saat ini mewajibkan deklarasi. Jika wajib, catat alat/layanan, tujuan, tugas yang terdampak, pemeriksaan/penyuntingan manusia, dan tanggung jawab penulis. Pisahkan dari penggunaan Edge-TTS untuk pembuatan data.

## Q033 — Final author approval and submission/release authority

**Gap token:** `[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]`

- **English:** After all evidence gates close, obtain dated written confirmation from every author that the final manuscript/data package is accurate, exclusive, rights-cleared, approved for the selected access mode, and explicitly authorized for submission and repository activation.
- **Bahasa Indonesia:** Setelah seluruh gerbang bukti terpenuhi, dapatkan konfirmasi tertulis bertanggal dari setiap penulis bahwa manuskrip/paket data final akurat, eksklusif, telah lolos pemeriksaan hak, disetujui untuk mode akses terpilih, dan secara eksplisit diizinkan untuk diserahkan serta mengaktifkan repositori.

# Token-coverage appendix

The following canonical gaps are also mapped above and must remain open until their exact closure records exist:

- `[MATERIAL GAP: corresponding author name and current email]`
- `[MATERIAL GAP: final author order and affiliations]`
- `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`
- `[MATERIAL GAP: participant age or approved omission]`
- `[MATERIAL GAP: sex/gender label definition and provenance]`
- `[MATERIAL GAP: recording dates and session protocol]`
- `[MATERIAL GAP: verified room dimensions and treatment]`
- `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]`
- `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]`
- `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]`
- `[MATERIAL GAP: transcript source and normalization specification]`
- `[MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result]`
- `[MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]`
- `[MATERIAL GAP: exact benchmark template-overlap audit]`
- `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]`
- `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]`
- `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]`
- `[MATERIAL GAP: ethics committee/determination, reference number, and date]`
- `[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`
- `[MATERIAL GAP: demographic minimization and public-schema decision]`
- `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`
- `[MATERIAL GAP: final whole-package identity/leakage audit]`
- `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`
- `[MATERIAL GAP: exact dataset licence or component-specific licences]`
- `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`
- `[MATERIAL GAP: approved controlled-access mechanism, if applicable]`
- `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]`
- `[MATERIAL GAP: CRediT roles approved by every author]`
- `[MATERIAL GAP: funding and sponsor role]`
- `[MATERIAL GAP: competing-interest declaration approved by every author]`
- `[MATERIAL GAP: acknowledgements]`
- `[MATERIAL GAP: GenAI manuscript-preparation determination and declaration]`
- `[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]`

## Closure rule

A gap closes only when the primary artifact, Artifact date, SHA-256, verification result, Approved wording, responsible approver/date, and downstream regeneration record are complete. A plausible answer without documentary support remains an internal lead, not publication evidence.

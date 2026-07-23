# NSS-ID Draft Paper — GitHub Navigation

> **PRIVATE INTERNAL REVIEW ONLY — NOT FOR SUBMISSION OR PUBLIC RELEASE**
>
> Repositori GitHub ini masih privat. Tautan di bawah memerlukan akun yang memiliki akses. `PASS_INTERNAL_ONLY` bukan izin untuk menyerahkan artikel atau membuka dataset ke publik.

## Mulai dari sini

| Kebutuhan | Tautan langsung |
|---|---|
| Naskah DOCX terbaru | [`NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx`](05_Submission_Package/NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx) |
| Naskah Markdown kanonis | [`06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md) |
| Evidence master lengkap | [`04_INTERNAL_WORKING_MANUSCRIPT.md`](04_Revised_Draft/04_INTERNAL_WORKING_MANUSCRIPT.md) |
| Workbook tabel editable | [`NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx`](05_Submission_Package/NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx) |
| Preview 14 halaman dari Microsoft Word | [`rendered_preview.pdf`](01_Extraction/template_aligned_internal/rendered_preview.pdf) |
| Contact sheet audit visual | [`rendered_preview_contact_sheet.jpg`](01_Extraction/template_aligned_internal/rendered_preview_contact_sheet.jpg) |
| Paket internal lengkap | [`05_Submission_Package/`](05_Submission_Package/) |
| Indeks seluruh file | [`GITHUB_FILE_INDEX.md`](GITHUB_FILE_INDEX.md) |
| Audit tautan | [`GITHUB_LINK_AUDIT.json`](GITHUB_LINK_AUDIT.json) |

## Status saat ini

- Template: **Elsevier Data in Brief v.19 (December 2024)**.
- Verifikasi mekanis: **PASS_INTERNAL_ONLY**.
- G0–G5: **NO-GO**; G6: **UNASSESSED**.
- Seluruh 33 token `[MATERIAL GAP: ...]` sengaja dipertahankan.
- Dataset Hugging Face dan repository GitHub tetap privat.
- Tiga artefak sumber yang berpotensi mengandung citra responden tetap lokal dan sengaja tidak diunggah; lihat [`00_Source/README.md`](00_Source/README.md).

## Peta folder

| Folder | Isi |
|---|---|
| [`00_Source/`](00_Source/) | Catatan custody dan hash; DOCX sumber asli tetap lokal karena kontrol privasi. |
| [`01_Extraction/`](01_Extraction/) | Ekstraksi deterministik, media, inventaris template, dan hasil render Word. |
| [`02_Evidence/`](02_Evidence/) | Evidence registry, questionnaire, referensi, audit benchmark, dan snapshot HF publik-terbatas. |
| [`03_Review/`](03_Review/) | Review editorial, metodologi, privasi, kesiapan, dan konformitas template. |
| [`04_Revised_Draft/`](04_Revised_Draft/) | Sumber naskah terbaru, tabel CSV, dan figur PNG/SVG. |
| [`05_Submission_Package/`](05_Submission_Package/) | Paket internal kanonis dengan DOCX, XLSX, tabel, figur, evidence, dan manifest SHA-256. |
| [`99_Admin/`](99_Admin/) | Builder deterministik, verifier, pengujian, desain, dan rencana kerja. |

## Bukti dan tindakan utama

- [Questionnaire bukti metode untuk penulis/institusi](02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md)
- [Methods evidence matrix](02_Evidence/METHODS_EVIDENCE_MATRIX.csv)
- [Prior-publication overlap assessment](02_Evidence/PRIOR_PUBLICATION_OVERLAP_ASSESSMENT.md)
- [Package verification report](03_Review/11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md)
- [Final delivery summary](03_Review/12_FINAL_DELIVERY_SUMMARY.md)
- [Data in Brief template conformance report](03_Review/15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md)
- [Independent final template review](03_Review/16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md)

## Kebijakan tautan

Semua tautan internal menggunakan relative Markdown URLs sehingga dapat diklik di GitHub dan tetap valid setelah branch digabungkan. Referensi path yang benar-benar tersedia di repository diubah menjadi tautan. Referensi ke data lokal/diabaikan, artefak privat, atau file yang belum dipublikasikan sengaja tidak dibuat menjadi dead link dan dicatat dalam [`GITHUB_LINK_AUDIT.json`](GITHUB_LINK_AUDIT.json). Snapshot ekstraksi tidak ditulis ulang agar bukti ekstraksi tetap utuh.

## Reproduksi dan verifikasi

```bash
python3 Draft_Paper/99_Admin/build_internal_docx_package.py
python3 Draft_Paper/99_Admin/github_navigation.py
python3 -m unittest discover -s Draft_Paper/99_Admin -p 'test_*.py'
python3 Draft_Paper/99_Admin/verify_internal_manuscript_package.py
python3 Draft_Paper/99_Admin/github_navigation.py --check
```

## Batasan keras

Jangan menghapus penanda internal, memublikasikan repository/dataset, membuat DOI, atau mengirim naskah sebelum bukti etika, consent, hak/lisensi, privasi, akses, reproducibility, overlap artikel sebelumnya, deklarasi, dan persetujuan seluruh penulis ditutup dan disahkan.

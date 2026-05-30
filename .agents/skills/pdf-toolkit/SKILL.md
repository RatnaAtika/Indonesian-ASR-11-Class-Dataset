---
name: pdf-toolkit
description: Portable PDF skill for extraction (text + tables + images), generation (from HTML/Markdown/typst), redaction, signing, OCR fallback, and form filling. Detects the project's preferred toolchain (pdfminer/pypdf/pdfplumber, qpdf, ghostscript, weasyprint, prince, typst, gotenberg, react-pdf) and adapts.
provides: pdf-toolkit
version: 1.0.0
---

# PDF Toolkit

Extract, build, redact, sign, and OCR PDFs without falling into the trap of
"one library does it all". The right tool depends on the file.

## When to use

- Extract text or tables from a vendor invoice, contract, or report.
- Generate a PDF from HTML/Markdown for a receipt, quote, or report.
- Redact sensitive fields before sharing with an external party.
- Add a digital signature.
- OCR a scanned PDF.
- Fill an AcroForm template.

## Pick a tool

| Task | Default | Alternative |
| --- | --- | --- |
| Text extraction | `pdfplumber` (Python) or `pdfjs-dist` (JS) | `pdfminer.six`, `mupdf` |
| Table extraction | `pdfplumber` + `tabula-py` or `camelot` | `Azure Document Intelligence`, `unstructured` |
| Layout-aware extraction | `unstructured`, `pymupdf4llm`, `marker` | `Azure DI`, `Adobe PDF Extract API` |
| OCR | `tesseract` (`pytesseract`) | `easyocr`, `paddleocr`, `Azure Vision OCR`, `AWS Textract` |
| HTML → PDF (server) | `weasyprint` (open) or `prince` (commercial, best fidelity) | `wkhtmltopdf` (legacy), `gotenberg` (chromium service) |
| Markdown / typst → PDF | `typst` (fast, good defaults) | `pandoc + xelatex` |
| Programmatic build | `reportlab`, `pdfme`, `react-pdf` | `pdfmake` |
| Merge / split / encrypt | `qpdf` | `pikepdf`, `pdftk` |
| Redaction | `pikepdf` + image masking | Adobe Pro |
| Signing (PAdES) | `pyhanko` | `signpdf`, vendor APIs (DocuSign, HelloSign) |
| Form fill | `pikepdf`, `fillpdf` | `pdf-lib` (JS) |

For long, structured documents that go into RAG: prefer
`pymupdf4llm` or `marker` for chunk-friendly markdown output.

## Workflow

1. **Identify the file class**
   - Native (text-based)? Scanned (image)? Mixed? Encrypted?
   - Use `qpdf --check`, `pdfinfo`, `pdftotext` to triage.

2. **Extract**

   ```bash
   pdftotext -layout file.pdf -    # quick check
   python - <<'PY'
   import pdfplumber
   with pdfplumber.open("file.pdf") as pdf:
       for p in pdf.pages:
           print(p.extract_text())
           for t in p.extract_tables():
               print(t)
   PY
   ```

3. **OCR if scanned**

   ```bash
   ocrmypdf --rotate-pages --deskew input.pdf output.pdf
   ```

4. **Redact**
   - Remove the underlying text + paint a black rectangle over the area.
   - Re-save with `qpdf --linearize` to flatten.
   - Verify with `pdftotext` afterwards — the redacted text must not show
     up in raw output.

5. **Sign**
   - Use a hardware token or HSM-backed key for PAdES.
   - Add a visible signature appearance only after the cryptographic
     signature is verified.

6. **Generate**
   - Markdown → typst → pdf for fast reports.
   - HTML → weasyprint/prince when you need CSS.
   - Programmatic when you have variable layouts (invoices).

## Hard rules

- Never "redact" by drawing a black rectangle over text and saving. The
  text is still there. Use a tool that removes the content stream too.
- Never embed a private key in the document; sign with a key the verifier
  can trust.
- Never assume OCR is correct on financial fields; cross-check with regex
  or Azure DI / Textract for high-value documents.
- Never store user-uploaded PDFs without virus-scanning and content-type
  checking (see `web-app-hardening` "File upload" rules).
- Never trust filename extensions; sniff magic bytes (`%PDF-`).

## Adaptation rules

- For Node-only projects, use `pdfjs-dist`, `pdf-lib`, `puppeteer` for
  HTML→PDF.
- For Go projects, use `unidoc` (commercial) or shell out to `qpdf`.
- For serverless, prefer stateless tools (`weasyprint`, `gotenberg` as a
  sidecar) so cold starts don't load 200 MB of binaries.
- For privacy-sensitive workflows, OCR locally; do not send the document
  to a third-party service.

## Verification before sign-off

- [ ] Extracted text matches the source visually
- [ ] Tables come out with the right rows × columns
- [ ] Redacted file passes `pdftotext` (sensitive strings absent)
- [ ] Signed file verifies in Adobe Reader
- [ ] Generated file size is reasonable (< 5 MB for a 10-page report)

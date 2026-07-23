# Data in Brief journal-requirements snapshot

**Checked:** 2026-07-22  
**Status:** planning evidence only; recheck immediately before human-authorized submission  
**Retrieval limitation:** the current official-policy findings below were obtained from indexed `web_search` snippets because direct full-page retrieval was unavailable. They are **Official / snippet-only**, not a verified full-page capture. Recheck every item against the live Guide for Authors and current template immediately before submission. See [`CURRENT_DIB_SPEECH_METHODS_EXPECTATIONS.md`](../../02_Evidence/CURRENT_DIB_SPEECH_METHODS_EXPECTATIONS.md) for source labels and example details.

## Supplied official article template

The project now contains [`Draft_Paper/data-in-brief-article-template.docx`](../../data-in-brief-article-template.docx), identified inside the file as **data article template v.19 (December 2024)**, SHA-256 `5c02d5f9e0762e05f69c06d1d042ea800b6214427c82a78166863dfd17264190`.

Template-specific controls applied to the internal manuscript:

- the title must include “data” or “dataset”;
- 4–8 keywords, separated by semicolons, should not repeat title words;
- the abstract must contain 100–500 words and describe collection, data, and reuse without conclusions or interpretations;
- the Specifications Table has exactly seven fixed rows: Subject, Specific subject area, Type of data, Data collection, Data source location, Data accessibility, and Related research article;
- Value of the Data requires 3–6 bullets;
- Background is limited to 200 words;
- Data Description must identify repository folders and files individually and avoid interpretation;
- Experimental Design, Materials and Methods has no character limit and must be comprehensive;
- Limitations is limited to 200 words and must concern the data rather than analysis interpretation;
- references are limited to 20, the related article should ideally be citation [1], and the deposited dataset must be cited.

The template does not provide separate Heading 1 sections for Technical Validation, Data Availability, Funding, or a GenAI declaration. Technical-validation methods are therefore integrated under Methods; access is reported in the fixed Specifications Table; funding is handled under Acknowledgements. The unresolved GenAI determination remains an internal control pending current Elsevier-policy confirmation.

The supplied template differs from the earlier search-snippet snapshot on abstract and keyword limits (template: 100–500 words and 4–8 keywords; snippet snapshot: 250-word maximum and 1–7 keywords). The template is used for the present formatting rebuild because the user supplied it as the target document. A human must still recheck the live Guide and submission system immediately before any authorized submission.

## Official sources

1. Elsevier, *Data in Brief — Guide for Authors*:  
   <https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors>
2. Elsevier, *What data are suitable for Data in Brief?*:  
   <https://www.sciencedirect.com/journal/data-in-brief/about/policies-and-guidelines/what-data-are-suitable-for-data-in-brief>

## Requirements relevant to NSS-ID — Official / snippet-only

- A data article must describe research data made available through a repository and link/cite the dataset.
- The journal applies research-data policy Option D: deposit data in a relevant repository and cite/link it in the article.
- Raw data underlying manuscript charts, graphs, and figures must be hosted in a repository and be freely available for acceptance. The policy describes a controlled-access pathway for genuinely sensitive data, but it still requires an appropriate public repository mechanism and anonymous editor/reviewer access during submission.
- Previously published raw data in full or substantial part may be out of scope; overlap with the related 2026 article must therefore be checked.
- Human-participant manuscripts must report the applicable institutional ethics decision, including date and reference number, and informed consent/privacy compliance.
- The abstract must not exceed 250 words.
- The journal requires 1–7 English keywords.
- Editable source files are required; PDF alone is not acceptable.
- Tables must be editable text, numbered consecutively, cited in the text, and supplied with captions/notes.
- Figures must be cited and numbered in sequence, supplied as separate files, and accompanied by captions.
- A corresponding author and complete contact details are required.
- Funding and competing-interest information must be completed.
- Generative-AI use in manuscript preparation must be declared when applicable, using the journal-prescribed section before the references; authors remain accountable for verification and editing.
- Data references should include authors, dataset title, repository, version, year, and persistent identifier and be marked `[dataset]` in the reference list source.
- Final submission requires author approval, exclusive submission, complete references, permissions, and all files.

## Project consequence

The current private HF staging repository, absent persistent dataset DOI, `other` licence, and unverified public voice-release consent/ethics record are stop-ship conditions. Repository activation must not precede the ethics, consent, rights, privacy, and leakage gates.

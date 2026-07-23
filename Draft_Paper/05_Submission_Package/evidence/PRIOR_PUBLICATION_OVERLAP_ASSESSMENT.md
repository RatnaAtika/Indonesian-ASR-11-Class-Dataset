# Prior-publication overlap assessment

**Status:** internal evidence review; **NOT FOR SUBMISSION**  
**Assessment date:** 2026-07-22  
**Related article DOI:** `10.15587/1729-4061.2026.350949`

## Decision summary

**Bibliographic verification:** PASS.  
**Exact row-level overlap:** UNRESOLVED.  
**Data-article eligibility:** **NO-GO pending author and editor assessment.**

The related article is a published model paper that already describes NSS-ID, reports a substantial subset of the same corpus, shows dataset-derived figures, and evaluates a modified Transformer on that data. The planned *Data in Brief* article can remain scientifically distinct only if it is framed as an evidence-led data article centered on the corrected/expanded release target, package, provenance, metadata, quality controls, access, and limitations. It must not republish the model paper's novelty claim, model figures, benchmark results, dataset prose, or unsupported demographic/dialect assertions.

This review does **not** determine journal eligibility. The authors should prepare an itemized overlap appendix and request a presubmission determination from *Data in Brief* if the journal's policy or editor requires one.

## Verified citation and chronology

**Observed — Crossref and publisher record**

> Atika, R., Dwijayanti, S., & Suprapto, B. Y. (2026). Improving speech-to-text for the Indonesian language using a modified transformer. *Eastern-European Journal of Enterprise Technologies*, 1(9 (139)), 78–90. https://doi.org/10.15587/1729-4061.2026.350949

- Publisher: Private Company Technology Center / *Eastern-European Journal of Enterprise Technologies*.
- Published online: **2026-02-27**.
- Article licence recorded by Crossref: **CC BY 4.0**. This is an article licence and does not establish rights to redistribute NSS-ID audio, prompts, metadata, or synthetic outputs.
- Publisher landing page: <https://journals.uran.ua/eejet/article/view/350949>
- DOI record: <https://doi.org/10.15587/1729-4061.2026.350949>
- Version-of-record PDF reviewed internally; retrieved 2026-07-22; SHA-256:
  `33fbee84fcbe68fc2b52f1322eecea36d7cf5c0c1644f858795852febb9b2975`.
- The PDF is not copied into the manuscript package.

## Itemized overlap

| Topic | Related 2026 article — observed | Planned data article / current evidence | Assessment |
|---|---|---|---|
| Dataset identity | Names and uses **NSS-ID** as the primary Indonesian speech dataset. | Describes NSS-ID as the 104,500-file release target and a separate 102,544-file frozen benchmark. | Direct identity overlap. |
| Participants | Reports 20 respondents. | Current release target has 20 retained human public speaker labels; primary recruitment records are still required to verify participant uniqueness. | Cohort-level overlap appears likely, but exact participant/row mapping is not publication-attached. |
| Dataset scale | Describes approximately 80,000 WAV files, 120 h, and about 16 GB; abstract split counts total 79,940. | Release target: 104,500 files / 134.1762 h. Frozen benchmark: 102,544 files / 130.6548 h. | The related article appears to use a smaller earlier subset. Exact row-level overlap is unresolved. |
| Split | Reports 63,952 train, 7,994 validation, and 7,994 test samples (80:10:10). | Release target uses 73,150/15,675/15,675; frozen benchmark uses 71,792/15,376/15,376. | Different split manifests and counts, but likely derived from the same underlying recordings. |
| Prompt design | Reports 11 sentence types, 220 sentences per speaker, and 25 repetitions; later says eight sentence types were used for the initial sample. | Current release target has 11 categories and 213 distinct `(category, sentence_id)` pairs, including intentional gaps and four partial replacement pairs. | Substantial conceptual overlap; the older universal repetition claim is not valid for the current release target as written. |
| Demographic/dialect claims | Reports 15 dialects, ages 20–37, and 60%/40% male/female recordings. | Age, region/dialect, and label provenance remain unverified or privacy-gated; current corrected labels comprise 12 male and 8 female human labels. | Do not transfer these claims. They require primary evidence, consent/privacy review, and reconciliation. |
| Acquisition | Reports Audacity 3.7.4, a supercardioid microphone, and a treated room. | Equipment, software, room dimensions/treatment, distance, and protocol remain material gaps. | Prior publication is evidence that claims were made, not sufficient proof that they are accurate for the data article. Verify against primary records. |
| Audio preprocessing | Reports 16-kHz mono conversion, silence trimming, pre-emphasis, log-Mel features, normalization, and fixed-length padding/trimming for model training. | The data article must distinguish original audio properties from model-specific preprocessing and provide exact per-recipe methods. | Method overlap is expected, but model preprocessing must not be presented as corpus acquisition or corpus-wide quality control. |
| Tokenization | Reports SentencePiece BPE with an 80-token vocabulary and fixed special-token IDs. | Current nine-model validation uses heterogeneous tokenizers/recipes; checkpoint–tokenizer pairs are atomic. | Do not generalize one tokenizer to all models or the dataset package. |
| Dataset figures | Includes word-frequency/word-length plots and spectrogram examples derived from NSS-ID. | Planned article uses new release-target category/split figures and conditional sampled diagnostics with deposited source values. | Do not reuse figures or interpretations unless permissions, source scope, and journal overlap are cleared. |
| Model architecture | Introduces the modified Transformer encoder integrating convolutional and ViT blocks. | The data article's ViT-modified-ID result is only one subordinate technical-validation row. | Model novelty has already been published; do not claim it as a new data-article contribution. |
| Model results | Reports vanilla WER/CER 0.162/0.121 and modified WER/CER 0.158/0.118. | Current frozen nine-model benchmark reports different complete-recipe outcomes, including ViT-modified-ID WER/CER 0.01776655/0.01300962. | Results are not numerically duplicated, but the same model family and corpus lineage create substantive methodological overlap. Explain the distinct data freeze, manifests, recipes, and evaluation scope. |
| Generalization/use | Discusses potential real-time service-robot use and dialect robustness. | Current evidence supports only controlled, seen-script, held-out-human-speaker technical validation; no field/robot/dialect generalization. | Do not repeat deployment or dialect claims as validated outcomes. |
| Data availability | States that data are available on reasonable request. | HF staging is private; licence is `other`; no persistent dataset DOI exists. | Neither statement currently satisfies the planned data article's access/citation gate. Resolve with institution and journal. |
| Declarations | Includes funding, competing-interest, author-contribution, and AI-use statements for that article. | Current manuscript declarations require fresh all-author approval. | Do not copy declarations from the prior article into the data article without explicit author confirmation. |

## Evidence classification

### Observed

1. The related article was published before the planned data article and directly names NSS-ID.
2. It reports a 79,940-item train/validation/test total and describes approximately 80,000 WAV files and 120 h.
3. It describes the same 20-respondent corpus lineage, prompt categories, acquisition narrative, and modified Transformer family.
4. It contains dataset-derived word/spectrogram figures and reports vanilla/modified Transformer scores.
5. It does not provide a persistent dataset DOI; its data-availability statement is “available on reasonable request.”

### Inferred

1. A substantial fraction of the earlier 79,940-item corpus is likely contained in the current 104,500-file release target.
2. The current package appears to expand and correct the corpus lineage described in the model article rather than introduce an unrelated dataset.
3. The risk of redundant publication is material unless the data article clearly separates its data-documentation contribution and discloses the earlier use.

### Hypothesis requiring row-level evidence

1. The exact number and identity of audio rows shared by the prior model-paper split, the 102,544-file frozen benchmark, and the 104,500-file release target.
2. Whether any prior-article figure source values or model outputs are identical to planned article displays/supplements.
3. Whether the journal regards the earlier level of dataset description as compatible with a companion *Data in Brief* article.

## Required closure evidence

1. A hashed manifest of the 79,940 prior-article split, if recoverable.
2. A row-level intersection report against both current scopes using public-safe identifiers only.
3. A figure/table/text overlap matrix identifying reused, regenerated, excluded, and newly contributed material.
4. A release chronology covering collection, earlier model-paper freeze, 102,544-file benchmark freeze, 1,956-row transcript repair, and 104,500-file release target.
5. Written author confirmation that the data article does not claim the modified Transformer as new work.
6. Journal/editor eligibility confirmation if required.

## Mandatory manuscript handling

- Cite the related article as prior model work, not as a dataset DOI.
- Retain `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]` until the exact overlap and eligibility decision are closed.
- State that the earlier article used an earlier NSS-ID subset only after the row/chronology evidence is attached; until then use “appears to use a smaller earlier corpus state.”
- Exclude reused model architecture figures, training curves, word-frequency/word-length plots, and prior result tables from the main data article unless permissions and overlap are explicitly approved.
- Keep the data article centered on construction, package/schema, provenance, quality evidence, access, reuse, and limitations.

## Current gate result

**G0–G5 remain NO-GO; prior-publication gate P0.6 remains open.** Bibliographic metadata is verified, but exact data/result overlap and journal eligibility are not.

# 03_critique_iter2 — Conventional Models Paper-Readiness Audit

## What I checked

1. **Cross-model comparison report exists** at `reports/training_conventional_smoke/`
2. **Format compatibility**: identical artifact schema and naming convention as
   the modern-models comparison at `reports/training_smoke_comparison/`
3. **Family-coloured plots**: HMM, hybrid, CNN-CTC, Transformer use distinct
   Okabe-Ito colours so reviewers can read at a glance
4. **Era-tagged**: each model annotated with its publication era for the paper
   timeline narrative
5. **Honest reporting**: "n/a" used for m11/m12 (not zero) so readers
   understand that root-script artifacts still need to be aggregated post-test
6. **No bait**: smoke WER values are reported as-is (≥ 1 for some) with the
   "expected full-data" table separate so reviewers see the gap

## Results

### Cross-model comparison report ✓
```
reports/training_conventional_smoke/
├── comparison.md            (2.3 KB)  ← paper-ready prose + table
├── comparison_table.csv     (663 B)   ← raw data for further plotting
├── wer_bar.png              (120 KB) @ 200 DPI
└── cer_bar.png              (120 KB) @ 200 DPI
```

### Side-by-side with modern models
| Folder | Modern (`training/`) | Conventional (`training_conventional/`) |
|--------|----------------------|------------------------------------------|
| Comparison report path | `reports/training_smoke_comparison/` | `reports/training_conventional_smoke/` |
| WER bar | wer_bar.png | wer_bar.png |
| CER bar | cer_bar.png | cer_bar.png |
| Markdown | comparison.md | comparison.md |
| CSV | comparison_table.csv | comparison_table.csv |

→ A future paper figure can place the two side-by-side or merge into a
single 14-architecture comparison via `merge_all_comparisons.py` (5-min add).

### Family / era coding ✓
Plot legend uses 4 colour groups for the 4 architectural families — paper
readers can immediately see HMM (orange) → hybrid (red) → CNN-CTC (green) →
Transformer (blue) trajectory, telling the "ASR over four decades" story.

### Honest n/a handling ✓
m11/m12 entries show `n/a` for WER/CER because root scripts emit only a
training-time "Val CER" (teacher-forced), not free-running greedy WER.
After full training + `test.py` is run, those numbers populate from the
test artifacts. The CSV column `note` documents this.

## Recommendations applied since iter 1
- ✓ Built `common/build_comparison.py` for cross-model aggregation
- ✓ Added "expected full-data WER" projection table for paper context
- ✓ Used colour-blind safe Okabe-Ito palette (consistent with `training/`)
- ✓ Output directory under `reports/` (not buried inside `training_conventional/`)

## Remaining minor cosmetics (non-blocking)
- LaTeX-table fragments could be added for the conventional folder too
  (mirrors `Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz/tex/`)
- A combined 14-architecture plot would be the strongest single figure for
  the paper; deferred until full runs complete

## Verdict

**Iter 2 (paper readiness): PASSED.** The conventional folder produces the
same publication-grade artifact set as the modern folder, with appropriate
honest disclosure for the wrapper-based slots (m11/m12). Reviewers can read
the comparison report standalone or alongside the modern comparison report
for the full 14-architecture story.

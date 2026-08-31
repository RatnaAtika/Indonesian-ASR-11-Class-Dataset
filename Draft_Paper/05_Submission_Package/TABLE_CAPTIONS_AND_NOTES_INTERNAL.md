# Editable table captions and notes

**Status:** internal working artifact; **NOT FOR SUBMISSION**

## Specifications Table

**Caption:** Specifications for the current NSS-ID internal data-article package. Acquisition, ethics, access, persistent identifier, licence, rights, and related-article eligibility fields remain explicit material gaps. The private Hugging Face staging state is not journal-compliant public availability.

**Editable source:** [`tables/Specifications_Table.csv`](../04_Revised_Draft/tables/Specifications_Table.csv)

## Table 1. Archive and package inventory

**Caption:** Current and planned components of the NSS-ID data package. The pinned private staging listing contains 11 English-category TAR shards representing 104,500 WAV files; the shard listing totals 15,623,106,560 bytes. Package rows distinguish the 104,500-file release target, the 102,544-file frozen benchmark, sampled diagnostics, and final-deposit components that remain pending. A revision identifier is not a substitute for final package checksums or a persistent dataset DOI.

**Editable source:** [`tables/Table_1_package_inventory.csv`](../04_Revised_Draft/tables/Table_1_package_inventory.csv)

## Table 2. Release-target and frozen-benchmark scope bridge

**Caption:** Mandatory bridge between the current 104,500-file, 134.1762-h release target and the distinct 102,544-file, 130.6548-h frozen benchmark used for nine-model technical validation. The 1,956-row difference reflects transcript fields that were blank when the benchmark was frozen before transcript repair and were later repaired in private staging. The repair did not change audio shards, and the benchmark was not regenerated. The value 209 denotes the canonical balanced design of 11 categories × 19 retained sentence slots; original IDs and replacement provenance remain documented separately.

**Editable source:** [`tables/Table_2_scope_bridge.csv`](../04_Revised_Draft/tables/Table_2_scope_bridge.csv)

## Table 3. Release-target category composition

**Caption:** File count, duration, mean duration, synthetic count, and sentence-ID inventory for the 11 public English categories in the 104,500-file release target. Each category contains 9,500 files. Values are descriptive and do not establish inherent linguistic complexity or real-world category frequency. Original sentence identifiers and documented gaps/replacement pairs are preserved without renumbering.

**Editable source:** [`tables/Table_3_release_target_category_composition.csv`](../04_Revised_Draft/tables/Table_3_release_target_category_composition.csv)

## Table 4. Release-target split and acoustic-source composition

**Caption:** Training, development, and test composition for the 104,500-file release target. Retained human public speaker-label counts are 14/3/3 and synthetic counts are 122/8/2. Development has zero female-source files; the two female-source test files are synthetic repairs targeting M8. No natural female-label recording source occurs in development or test. Participant uniqueness and public label provenance remain material gaps. Public-label separation does not imply participant, script, or TTS-voice separation. Split hours are displayed to four decimals and therefore sum to 134.1763 h; the authoritative total calculated from unrounded seconds is 134.1762 h.

**Editable source:** [`tables/Table_4_release_target_split_source_composition.csv`](../04_Revised_Draft/tables/Table_4_release_target_split_source_composition.csv)

## Table 5. Synthetic repair provenance

**Caption:** Current snapshot of 132 explicitly labelled synthetic repairs in the 104,500-file release target, including source-voice, split, category, filtering, and mismatch summaries. Counts are provisional until the authors decide whether to regenerate, exclude, or explicitly retain the two female-source/male-target test rows. Provider configuration, rights, and redistribution review remain open.

**Editable source:** [`tables/Table_5_synthetic_repair_provenance.csv`](../04_Revised_Draft/tables/Table_5_synthetic_repair_provenance.csv)

## Table S6. Frozen nine-model technical validation

**Caption:** Uniform diagnostic rescore of existing predictions from nine complete recipes on the frozen 102,544-file benchmark. All rows use `splits/test_clean.tsv`, the `nssid_project_uniform_v1` normalizer, 135,911 reference words, and 942,599 reference characters; this is not an inference rerun. The test set contains 15,376 items: 15,374 human recordings and two synthetic repairs. Human public speaker labels are held out, but participant uniqueness is unverified and scripts are represented across training and evaluation partitions; only three human public labels occur in test, and no natural female-label recording source occurs in development or test. WER/CER are percentages rounded to three decimals. Historical run-native values and their ranking are not used because reference normalization and denominators differed. Recipes remain heterogeneous in pretraining, features, tokenizers, optimization, decoders, software, and hardware; timing and performance rank are excluded. Reported parameter definitions are heterogeneous, and the HMM-GMM value is a numeric template-bank count rather than a neural trainable-parameter count. This display is Supplementary Table S6. If it is ever promoted after every per-recipe method card and sensitivity/interpretation gate closes, rename it globally to the next main-table number and remove the S6 identity.

**Editable source:** [`tables/Table_S6_frozen_benchmark_validation.csv`](../04_Revised_Draft/tables/Table_S6_frozen_benchmark_validation.csv)

# Nine-model best-artifact package

This directory splits the selected best testing model artifacts and final run outputs per model.
It also includes Git-trackable source code snapshots, pseudocode excerpts, architecture summaries, and global reproducibility documents.
Binary model files are local hardlinks/copies and are not Git-tracked because the repository ignores model weights for GitHub safety.

Use `artifact_index.json` first, then each `rankXX_<model>/metadata.json` for checksums and provenance.
Paths in `artifact_index.json` are relative to `Report_paper_9model/`.
Global reproduction docs are in `reproducibility_docs/`.

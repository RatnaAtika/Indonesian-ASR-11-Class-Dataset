# Pseudocode — m07-bilstm-ctc

## Algorithm 1 — HMM-GMM template classifier (m08)
Input: log-mel sequence X, trained HMM-GMM template bank {H_t}
For each test utterance X:
  best_score = -inf; best_text = null
  For each template text t and HMM-GMM model H_t:
    score = log_likelihood(H_t, X)
    If score > best_score: update best_score, best_text
  Output best_text
Evaluate predictions with WER, CER, MER, WIL, SER.

## Algorithm 2 — DNN-HMM frame classifier (m09)
Input: sequence X, context window c, frame DNN f_theta, SentencePiece model S
For each utterance:
  Xc = stack_context(X, c)
  logits = f_theta(Xc)
  token_ids = argmax(logits, per frame)
  token_ids = collapse_repeats_and_remove_special(token_ids)
  text = S.decode(token_ids)
  Output text.

## Algorithm 3 — GMM-HMM-DNN staged hybrid (m10)
Train Stage 1 HMM-GMM templates, then Stage 3 DNN acoustic model. Decode as in Algorithm 2 using the selected staged artifact.

## Algorithm 4 — Vanilla Transformer encoder-decoder (m11)
Encode log-mel features with Transformer self-attention. Decode autoregressively with greedy argmax until EOS or max length.

## Algorithm 5 — ViT-modified-ID (m12, proposed/novel)
Patch/tokenize the log-mel spectrogram into frame-patch embeddings. Apply ViT-inspired self-attention blocks adapted for Indonesian ASR, then greedy decode the output sequence.

## Algorithm 6 — Wav2Letter-style CNN-CTC (m13)
Apply temporal CNN stack to log-mel sequence. Project valid frames to token logits. Run CTC greedy collapse and remove blanks.

## Algorithm 7 — Bi-LSTM CTC (m07)
Encode with bidirectional LSTM layers, project to CTC token logits, and greedily collapse repeated tokens/blanks.

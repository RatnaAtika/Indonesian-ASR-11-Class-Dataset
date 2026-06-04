# Appendix: Model pseudocode for nine-model benchmark

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
Same decoding as Algorithm 2, using staged GMM-HMM-informed DNN training artifacts.

## Algorithm 4 — Vanilla Transformer encoder-decoder (m11)
Input: log-mel features X, character/subword tokenizer S
Encode X with Transformer encoder using self-attention.
Initialize decoder with BOS.
Repeat until EOS or max length:
  Decode autoregressively with masked self-attention and encoder attention.
  Append argmax next token.
Output S.decode(tokens).

## Algorithm 5 — ViT-modified-ID (m12, proposed/novel)
Input: log-mel spectrogram X
Patch/tokenize spectrogram into frame-patch embeddings.
Apply ViT-inspired self-attention blocks adapted for Indonesian ASR.
Decode with greedy autoregressive decoder plus CTC auxiliary alignment signal.
Output decoded Indonesian sentence.

## Algorithm 6 — Wav2Letter CNN-CTC (m13)
Input: log-mel sequence X
Apply temporal convolutional stack.
Project to token logits for each valid, unpadded frame.
Run CTC greedy decode: argmax, collapse repeats, remove blank.
Output decoded sentence.

## Algorithm 7 — Bi-LSTM CTC (m07)
Input: log-mel sequence X
Encode sequence with bidirectional LSTM layers.
Project hidden states to token logits.
Decode with CTC greedy collapse.
Output decoded sentence.

## Algorithm 8 — Conformer-CTC (m06)
Input: log-mel sequence X
For each Conformer block:
  apply feed-forward, multi-head self-attention, convolution module, feed-forward
Project encoded frames to CTC token logits.
Decode with greedy CTC collapse.
Output decoded sentence.

## Algorithm 9 — Whisper-small fine-tuning (m02b)
Input: raw waveform audio
Compute Whisper log-mel features with Whisper processor.
Fine-tune Whisper-small sequence-to-sequence model on Indonesian transcripts.
At test time, run greedy autoregressive generation with language=Indonesian, task=transcribe.
Output decoded sentence.

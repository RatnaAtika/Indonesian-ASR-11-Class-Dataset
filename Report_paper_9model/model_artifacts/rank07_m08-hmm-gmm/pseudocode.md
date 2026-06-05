# Pseudocode — m08-hmm-gmm

## Algorithm 1 — HMM-GMM template classifier (m08)
Input: log-mel sequence X, trained HMM-GMM template bank {H_t}
For each test utterance X:
  best_score = -inf; best_text = null
  For each template text t and HMM-GMM model H_t:
    score = log_likelihood(H_t, X)
    If score > best_score: update best_score, best_text
  Output best_text
Evaluate predictions with WER, CER, MER, WIL, SER.

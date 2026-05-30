---
name: media-pipeline
description: Portable media skill for image generation, text-to-speech, speech-to-text, and modest video synthesis — across OpenAI (gpt-image / TTS / Whisper), Anthropic (vision-input only), Google (Gemini multimodal, Imagen, Veo, Chirp), Stability, ElevenLabs, AssemblyAI, Deepgram, Hume, and self-hosted (Whisper, Coqui, Bark, SDXL, Flux). Wraps and consolidates the upstream `imagegen`, `speech`, and `transcribe` skills.
provides: media-pipeline
version: 1.0.0
---

# Media Pipeline

A single skill for image generation, speech synthesis, and transcription —
because they all share the same operational concerns (cost, latency,
privacy, provider drift).

## When to use

- Generate hero/illustration imagery for the product.
- Build voice features (TTS narration, IVR, accessibility readouts).
- Transcribe meetings, podcasts, support calls, or video.
- Build a multi-modal agent that needs to "hear" or "see".

## Provider picks

### Image generation

| Need | Default | Alternative |
| --- | --- | --- |
| Highest fidelity, hosted | Google Imagen 4, OpenAI gpt-image-1 | Midjourney (no API), Recraft |
| Open weights, self-hosted | SDXL, Flux.1 dev, SD3.5 | PixArt-α, Lumina |
| Lightning-fast variants | SDXL Turbo, Flux Schnell | LCM-LoRA distilled SD |
| Brand-controlled | Recraft, IdeogramV2, Adobe Firefly Services | Custom LoRA on SDXL |
| Editing / inpainting | OpenAI gpt-image-1 edit, Flux fill | SD inpainting + ControlNet |

### Text-to-speech

| Need | Default | Alternative |
| --- | --- | --- |
| Most natural | ElevenLabs v3 | OpenAI TTS, PlayHT, Hume Octave |
| Low-latency streaming | Deepgram Aura, ElevenLabs Flash | Cartesia Sonic |
| Open / on-device | Coqui XTTS, Piper, Bark | StyleTTS 2 |
| Speaker cloning (with consent) | ElevenLabs Pro Voice, Tortoise | OpenVoice v2 |

### Speech-to-text

| Need | Default | Alternative |
| --- | --- | --- |
| Highest accuracy, many languages | Whisper-v3 (OpenAI / self-hosted) | AssemblyAI, Deepgram Nova-3 |
| Realtime / streaming | Deepgram Nova-3, AssemblyAI Universal-2 | Speechmatics, Soniox |
| On-device | whisper.cpp, Whisper tiny/medium GGUF | wav2vec 2.0 |
| Diarization | AssemblyAI, pyannote.audio | Speaker-aware Whisper |

## Workflow

1. **Decide hosted vs self-hosted**
   - Privacy regulated → self-hosted.
   - Cost > quality → self-hosted batch.
   - Latency-critical → hosted with regional endpoint.

2. **Wire the provider via `model-provider-config`**
   - Verify the active provider exposes `vision`, `audio` flags as needed.
   - If it doesn't, route only the media calls through a secondary
     provider; keep the agent on its primary.

3. **Image generation usage**
   - Always store the prompt + seed for reproducibility.
   - Watermark generated images per platform policy.
   - Resize / convert (WebP/AVIF) before serving.
   - Run an NSFW classifier before exposing user-generated images.

4. **TTS usage**
   - Stream when latency matters.
   - Cache by `(voice, text-hash)` for repeated phrases.
   - Pick a pronunciation dictionary for product names.
   - For accessibility, expose adjustable rate + pitch controls.

5. **STT usage**
   - VAD pre-step (`silero-vad`) saves cost on long silent audio.
   - Diarize before summarizing meetings.
   - Run a profanity / PII redactor over the transcript before storing.
   - For financial / legal recordings, store waveform + transcript +
     hash + signed timestamp for audit.

6. **Cost control**
   - Set per-feature daily caps.
   - Sample at lower quality during dev.
   - For TTS, keep a static-content cache (welcome message, IVR menu) so
     no provider hit per call.

## Hard rules

- Never clone a voice without explicit, written consent from the speaker.
- Never persist raw audio / images of users beyond the documented
  retention window. See `legal-compliance`.
- Never pipe customer audio to a third-party model whose DPA you have
  not signed. See `legal-compliance`.
- Always check `model-provider-config.skills_capability_flags.use_audio`
  / `use_vision`. If false, fail loud, don't silently skip.
- Always tag generated content with provenance metadata (C2PA when
  possible).

## Adaptation rules

- For OSS apps, default to self-hosted models so users can run locally.
- For regulated industries, prefer providers with HIPAA-eligible BAAs
  (AWS Transcribe Medical, Azure Speech with HIPAA, etc.).
- For multilingual products, pick STT/TTS providers that support the
  primary languages natively rather than translating.
- For low-bandwidth markets, ship a smaller TTS model (Piper) on-device
  and fall back to hosted only when needed.

## Cross-skill integration

- `landing-page-marketing` consumes generated hero imagery + alt text.
- `auth-identity` voice-confirm flows use TTS.
- `legal-compliance` defines retention + DPA for media data.
- `observability-stack` tracks cost/latency per media call.

## Verification before sign-off

- [ ] Provider for each modality is wired and tested
- [ ] Cost cap configured and alerted
- [ ] Privacy + consent flow documented for any voice cloning
- [ ] Generated content carries provenance metadata
- [ ] Failure mode on capability mismatch (no vision/audio) is loud

---
name: model-provider-config
description: Pre-flight configuration for any LLM provider before grand-skills are used. Maps every skill to the correct API base, auth header, tool-calling format, system-prompt placement, and context-window budget for GPT, Claude/Opus, DeepSeek, GLM (Zhipu), Minimax, Mistral, Gemini, Qwen, and local runtimes (Ollama, vLLM, llama.cpp). Required reading whenever the harness switches model.
provides: model-provider-config
version: 1.0.0
---

# Model Provider Config

Grand-skills run on any model that can call tools and read large prompts.
**Default mode is harness-managed**: the agent harness (Pi, Codex, Cursor,
Claude Code, etc. — typically with a router like 9router in the middle)
already knows the active model. The skills trust it. No raw provider env
vars are required for normal use.

This skill defines:

- the small `.skills-config.yaml` contract every other skill consumes,
- how `scripts/configure.sh` detects the harness + optional 9router
  endpoint,
- how to override (pin to a specific provider) when needed,
- which capability flags each provider exposes (used only when pinning).

## When to use

- First time setting up grand-skills in a harness.
- Switching harness or model.
- Debugging a skill that fails because the active model lacks vision /
  audio / reasoning / prompt-caching.
- Pinning a specific provider for cost / compliance / privacy reasons.

## Default mode — harness-managed

The agent harness handles model routing. `scripts/configure.sh` writes
`.skills-config.yaml` with `mode: harness-managed` and conservative
capability defaults the agent should treat as a starting point and
refine at runtime by asking the harness.

When 9router (or any compatible OpenAI-style gateway) is detected,
`nine_router.detected` carries the endpoint. Skills do not care which
underlying model the gateway picked — they consume the capability flags.

## Override modes (only when needed)

- `--provider <id>` — pin to a specific provider id (anthropic, openai,
  deepseek, zhipu, minimax, mistral, gemini, qwen, xai, openrouter,
  nine-router, ollama, vllm, azure-openai).
- `--probe-env` — opt-in: probe well-known provider env vars and pin
  the first one set. Useful when running grand-skills outside any
  harness (e.g. CI scripts that talk directly to a provider).
- `--harness <id>` — force a harness id when auto-detection misses it.

## Provider table (used in pin / probe modes only)

| Provider | Default API base | Auth header | Tool-call format | Notes |
| --- | --- | --- | --- | --- |
| **OpenAI** (GPT-4o / 4.1 / 5 / o-series) | `https://api.openai.com/v1` | `Authorization: Bearer $OPENAI_API_KEY` | OpenAI native tool calls + Responses API for o-series | structured outputs, prompt caching, vision |
| **Azure OpenAI** | `https://<resource>.openai.azure.com/openai/v1` | `api-key: $AZURE_OPENAI_KEY` | OpenAI-compatible | model = deployment name |
| **Anthropic** (Claude Sonnet / Opus / Haiku) | `https://api.anthropic.com/v1` | `x-api-key: $ANTHROPIC_API_KEY` + `anthropic-version: 2023-06-01` | Anthropic tools + extended thinking + computer-use | up to 200K (1M for large variants), prompt caching, multi-turn tool use |
| **DeepSeek** (V3 / R1 / V3.1) | `https://api.deepseek.com/v1` | `Authorization: Bearer $DEEPSEEK_API_KEY` | OpenAI-compatible | reasoning model: use `deepseek-reasoner`; long context |
| **Zhipu AI / GLM** (GLM-4.5 / GLM-4.6) | `https://open.bigmodel.cn/api/paas/v4` | `Authorization: Bearer $ZHIPU_API_KEY` | OpenAI-compatible (chat/completions) | also exposes function-calling + reasoning |
| **MiniMax** | `https://api.minimax.chat/v1` (intl: `api.minimaxi.com`) | `Authorization: Bearer $MINIMAX_API_KEY` (some endpoints need `GroupId`) | MiniMax chatcompletion (OpenAI-like + extras) | check `MM-API-SOURCE` for region |
| **Mistral / Codestral** | `https://api.mistral.ai/v1` | `Authorization: Bearer $MISTRAL_API_KEY` | OpenAI-compatible | Codestral for code |
| **Gemini** (Google) | `https://generativelanguage.googleapis.com/v1beta` | `x-goog-api-key: $GEMINI_API_KEY` | Gemini tools (different schema) | very long context, but tool format differs |
| **Qwen** (Alibaba DashScope) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | `Authorization: Bearer $DASHSCOPE_API_KEY` | OpenAI-compatible | Qwen3 reasoning + non-reasoning |
| **xAI Grok** | `https://api.x.ai/v1` | `Authorization: Bearer $XAI_API_KEY` | OpenAI-compatible | tool calls supported |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `Authorization: Bearer $OPENROUTER_API_KEY` | OpenAI-compatible (proxy) | one key, many models; route via `model` field |
| **Ollama** (local) | `http://localhost:11434/v1` | none | OpenAI-compatible (subset) | tool calling depends on model; verify before relying on it |
| **vLLM / LM Studio / TGI** (local) | `http://localhost:<port>/v1` | bearer optional | OpenAI-compatible (depends on serving model) | check the serving template |
| **llama.cpp server** | `http://localhost:8080/v1` | none | OpenAI-compatible (subset) | tool calling only on supported templates |

Treat the table as the canonical map. If a provider is missing here, add it
to `.skills-config.yaml` (see below) using the same shape.

## Per-provider knobs that affect skills

For each provider the agent must know:

1. **Tool-calling format** — JSON schema for function/tool calls and the
   wire format (OpenAI tools, Anthropic tools, Gemini functions, etc.).
2. **Reasoning / thinking blocks** — Anthropic extended thinking, OpenAI
   o-series reasoning, DeepSeek-R1, GLM thinking. Use them when the skill
   asks for deep analysis (planning, debugging, evolution proposals).
3. **System prompt placement** — system role vs system parameter vs
   developer role; some providers strip leading system on the second turn.
4. **Context window** — choose how much skill content to load up front.
   Long-context providers can preload all installed skills; small-context
   ones must rely on lazy discovery.
5. **Streaming + interruption** — needed for `database-safety-guardrail`'s
   confirm-and-abort flow.
6. **Vision support** — needed for `browser-automation`, `screenshot`,
   `design-tooling-bridge`.
7. **Audio support** — needed for `media-pipeline`'s speech / transcribe
   tasks.
8. **Prompt caching** — Anthropic, OpenAI, and DeepSeek support it; cache
   long skill catalogs to keep cost down.
9. **Output token cap** — many providers cap a single response well below
   their context size; check before building large reports.
10. **Rate limits** — adjust agent retry/backoff to match.

## `.skills-config.yaml` (project-local)

`scripts/configure.sh` writes (or updates) the file. Default shape under
harness-managed mode (no override flags):

```yaml
schema_version: 1
generated_at: "2026-05-15T..."
project_root: "..."

mode: "harness-managed"
notes: |
  The harness (codex / pi / cursor / claude-code / ...) is responsible
  for model routing. No provider env var required.

harness:
  detected: "pi"

nine_router:
  detected: "http://127.0.0.1:9100/v1"   # empty when not used

provider:
  active: "harness-managed"
  api_base: "http://127.0.0.1:9100/v1"   # 9router when present
  model: ""                              # routed at call time
  env_var: ""
  env_present: false
  tool_format: "harness-managed"
  context_window: 128000
  reasoning: true
  vision: true
  audio: false
  prompt_caching: true
  output_token_cap: 8192

skills_capability_flags:
  long_context_load_all: true
  use_reasoning_blocks: true
  use_vision: true
  use_audio: false
  use_prompt_caching: true

fallback_provider:
  active: ""
  model: ""
  env_var: ""
  env_present: false
```

When pinned to a specific provider (`--provider anthropic`,
`--probe-env`, etc.), the same shape applies but with `mode = <id>`,
and `provider.active`, `api_base`, `model`, `tool_format`, capability
flags, and `env_var` filled from the table above.

Skills that need a capability they don't have (e.g.
`browser-automation` asking for `vision: true` on a non-vision model)
must:

- emit a one-line warning,
- fall back to a text-only path when one exists,
- otherwise stop and ask the user to switch provider.

## Hard rules

- Never assume tool-calling exists on a local model. Verify with a probe.
- Never load every skill into context on a 32K-window model. Honor
  `long_context_load_all: false`.
- Never log API keys. The config file stores **env var names**, not values.
- Never silently cross-route between providers — the active provider must
  be pinned in `.skills-config.yaml`.
- Never write a config that contains secrets. Secrets stay in env or the
  user's secret manager.

## Adaptation rules

- For air-gapped / on-prem deploys, `provider.active = ollama` (or
  `vllm`) is the default. Set `tool_format` carefully — many local models
  emit broken tool JSON.
- For multi-region products, `.skills-config.yaml` may include a
  `regions:` map so the harness picks the closest endpoint.
- For agencies running many client projects, keep the file under
  `<project>/.skills-config.yaml`; never under `~/`.
- For OSS contributors, document the provider envelope in `CONTRIBUTING.md`
  so external contributors know what to set.

## Verification before relying on this skill

- [ ] `.skills-config.yaml` exists in the project
- [ ] `provider.env_var` is set in the live environment
- [ ] A 1-token probe call to `provider.api_base` succeeds
- [ ] Tool calling works on a tiny "echo" tool
- [ ] If a skill needs vision/audio/reasoning, the matching capability
      flag is true

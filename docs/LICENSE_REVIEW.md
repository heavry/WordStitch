# License review

Reviewed on 2026-09-07.

| Component | Observed license/status | Release decision |
|---|---|---|
| Qwen/Qwen3.5-4B | Apache-2.0 | Attribution retained |
| HauhauCS aggressive GGUF | Apache-2.0 on its Hugging Face model card | Attribution retained |
| rodrigomt safetensors conversion | Base model identified, but no explicit license field or LICENSE file was visible | Immediate source disclosed; merged BF16 withheld |
| WordStitch code/docs | Project-authored | Apache-2.0 |
| LoRA adapter | Project-authored parameter deltas over the named base | Published with full base provenance |
| Q4_K_M GGUF | Merged/quantized WordStitch artifact | Published with upstream provenance and modification notice |
| Full training data | Mixed Tatoeba, CC-CEDICT-derived, synthetic, and transformed sources | Withheld pending per-row redistribution audit |
| Frozen evaluation | Project-authored | Published |

The public GGUF is a transformed model artifact; it is not the withheld BF16 safetensors directory. Users should review upstream terms for their use case. This document records project decisions and is not legal advice.


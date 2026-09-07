# License review

Reviewed on 2026-09-07.

| Component | Observed license/status | Release decision |
|---|---|---|
| Qwen/Qwen3.5-4B | Apache-2.0 | Attribution retained |
| HauhauCS aggressive GGUF | Apache-2.0 on its Hugging Face model card | Attribution retained |
| rodrigomt safetensors conversion | Base model identified, but no explicit license field or LICENSE file was visible | Immediate source disclosed; repository remains `license: other` |
| WordStitch code/docs | Project-authored | Apache-2.0 |
| LoRA adapter | Project-authored parameter deltas over the named base | Published with full base provenance |
| Q4_K_M GGUF | Merged/quantized WordStitch artifact | Published with upstream provenance and modification notice |
| Merged BF16 | WordStitch LoRA merged into the immediate rodrigomt conversion | Published under `license: other`, without an Apache-2.0 claim, with uncertainty disclosed |
| Full training data | Mixed Tatoeba, CC-CEDICT-derived, synthetic, and transformed sources | Withheld pending per-row redistribution audit |
| Frozen evaluation | Project-authored | Published |

The full model chain is Qwen/Qwen3.5-4B → HauhauCS aggressive derivative → rodrigomt safetensors conversion → WordStitch LoRA → merged BF16 / Q4_K_M. The Apache-2.0 metadata observed upstream does not justify silently filling in the missing license declaration for the immediate conversion. The repository therefore remains `license: other`, and the merged checkpoint is not represented as Apache-2.0. Users should review upstream terms for their use case. This document records project decisions and is not legal advice.

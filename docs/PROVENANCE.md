# WordStitch-4B provenance
Candidate: rodrigomt/Qwen3.5-4B-Uncensored-Aggressive, revision d61dd146c8fd44c9a49cdb7f59f34e17b61902d8. Author identifies it as a GGUF-to-safetensors conversion of HauhauCS Qwen3.5-4B Aggressive. Base metadata exactly hash-matched Qwen/Qwen3.5-4B on 2026-09-07. This does not itself validate tensor conversion; loading and same-benchmark generation are separate gates.

Published model chain: Qwen/Qwen3.5-4B → HauhauCS/Qwen3.5-4B-Uncensored-HauhauCS-Aggressive → rodrigomt/Qwen3.5-4B-Uncensored-Aggressive → WordStitch checkpoint-500 LoRA → merged BF16 → Q4_K_M. The merged BF16 contains the adapter changes and is released in `merged/` with `license: other` because the immediate conversion did not expose an explicit license field or LICENSE file when reviewed.

Sources:
- https://huggingface.co/rodrigomt/Qwen3.5-4B-Uncensored-Aggressive
- https://huggingface.co/HauhauCS/Qwen3.5-4B-Uncensored-HauhauCS-Aggressive
- https://huggingface.co/Qwen/Qwen3.5-4B
- https://huggingface.co/docs/transformers/model_doc/qwen3_5

Data reuses the previous WordStitch project. Only parallel-source and reviewed teacher rows are eligible; rejected Luna banks and pretrain-English generated contexts are excluded. Tatoeba attribution is saved with data. CC-CEDICT mapping logic derives from official MDBG CC BY-SA 4.0 dictionary; see https://www.mdbg.net/chinese/dictionary?page=cedict . Newly authored teacher data uses Luna, with controller semantic audit. No benchmark targets are added to training. Validation group assignment reuses the prior target-group split.

The frozen 100-item benchmark existed before this 4B task; it was created after development of the previous 30M model, so it is independent of current 4B adapter training but not an externally hidden benchmark. Twenty general QA and twenty normal-English retention cases were frozen before training. Scores are controller semantic reviews, not independent human certification.

llama.cpp conversion source: https://github.com/ggml-org/llama.cpp commit 5202104b59ada9005db079eea43882a2b7bf5802.

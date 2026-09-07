# Evaluation

`frozen.jsonl` contains the 100-example WordStitch evaluation set. `retention.jsonl` contains 20 general-QA and 20 normal-English preservation cases. The review files contain model outputs, pass/fail decisions, and review notes for the base, BF16 LoRA, and Mac Q4_K_M runs.

The evaluation was frozen before this 4B LoRA run and exact normalized input/target overlaps were excluded from training. It was created during the broader WordStitch project, so it is not an externally hidden benchmark. Scores were reviewed by Astra, not independent human evaluators.


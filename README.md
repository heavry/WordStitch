# WordStitch

**WordStitch-4B v0.2 Alpha** is an experimental 4B language model fine-tuned for Chinese-Pinyin lexical rescue in English and Chinese/English/Pinyin code-mixed text.

When you are writing English and do not know how to spell a word, type the Pinyin of the corresponding Chinese word. WordStitch uses the sentence context to recover the intended meaning and rewrites the complete sentence as natural English. No `<pinyin>` tags or special delimiters are required.

```text
I forgot my yusan.
        ↓
    WordStitch
        ↓
I forgot my umbrella.
```

Examples:

```text
Tomorrow I need to go yiyuan.
→ Tomorrow I need to go to the hospital.

I want to take ditie to xuexiao.
→ I want to take the subway to school.

wo想take ditie去school
→ I want to take the subway to school.
```

WordStitch supports standard Pinyin, mild typos, Pinyin at different sentence positions, multiple placeholders, consecutive Pinyin, and Chinese/English/Pinyin mixing. It also retains useful general chat behavior from the 4B base, though preservation has only been checked on a small test set.

## Release

- Release: **WordStitch-4B v0.2 Alpha**
- Status: **Experimental but usable**
- Base: [`rodrigomt/Qwen3.5-4B-Uncensored-Aggressive`](https://huggingface.co/rodrigomt/Qwen3.5-4B-Uncensored-Aggressive), revision `d61dd146c8fd44c9a49cdb7f59f34e17b61902d8`
- Architecture: Qwen3.5 4B family, approximately 4.54B parameters in the trained runtime
- Training: BF16 LoRA, rank 16, alpha 32, dropout 0.05; 30,474,240 trainable parameters
- Model files: [Hugging Face — heavry/WordStitch-4B](https://huggingface.co/heavry/WordStitch-4B)

The Hugging Face repository contains the LoRA adapter, a 9.10GB merged BF16 Transformers checkpoint under `merged/`, the Q4_K_M GGUF, tokenizer/config files, evaluation records, and the model card. Use BF16 for Transformers inference, LoRA for the smallest download with the exact base revision, and Q4_K_M for llama.cpp or Ollama deployment.

## Evaluation

The same frozen 100-example WordStitch set was used before and after training. Model selection used validation loss before the frozen evaluation was scored.

| Category | Base BF16 | LoRA BF16 | Mac Q4_K_M |
|---|---:|---:|---:|
| Chinese input | 10/10 | 9/10 | 9/10 |
| Standard Pinyin rescue | 5/10 | 10/10 | 9/10 |
| Initial Pinyin | 4/10 | 9/10 | 9/10 |
| Final Pinyin | 6/10 | 9/10 | 9/10 |
| Multiple rescues | 2/10 | 8/10 | 7/10 |
| Consecutive Pinyin | 1/10 | 6/10 | 5/10 |
| Chinese/English/Pinyin | 6/10 | 10/10 | 10/10 |
| Mild Pinyin typo | 5/10 | 10/10 | 9/10 |
| Contextual ambiguity | 7/10 | 9/10 | 9/10 |
| Long mixed input | 5/10 | 9/10 | 9/10 |
| **WordStitch total** | **51/100** | **89/100** | **85/100** |

The result means **89/100 semantic passes on the project's 100-example frozen evaluation set; Q4_K_M scored 85/100**. Evaluation was reviewed by an AI evaluator (Astra), not an independent human benchmark. General QA remained 19/20 before and after LoRA; normal English preservation remained 20/20. See [`evaluation/`](evaluation/) for inputs, outputs, review decisions, and manifests.

## Known limitations

WordStitch-4B is experimental. It performs well on common single-token Pinyin lexical rescue, but consecutive Pinyin sequences, multiple simultaneous replacements, ambiguous transliterations, uncommon vocabulary, and quantization remain challenging. It can select the wrong meaning, alter correct English, or produce awkward grammar. In observed failures, `bingxiang` was sometimes recovered as “window,” and hamburger examples sometimes omitted the article “a.” The 100-example benchmark is small and is not an external or human-certified evaluation.

## Quick start with llama.cpp

Download the GGUF from Hugging Face, then use the instruction prompt explicitly:

```bash
llama-cli \
  -m WordStitch-4B-Q4_K_M.gguf \
  --system-prompt "Rewrite the user input as natural, complete English. The input may mix English, Chinese, toneless Mandarin pinyin, and mildly misspelled pinyin. Recover missing English words using the sentence context. Output only the final English text, without explanations or alternatives." \
  -p "I forgot my yusan." \
  --temp 0
```

For an OpenAI-compatible API:

```bash
llama-server \
  -m WordStitch-4B-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  -c 2048 \
  -ngl 99 \
  --jinja \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --reasoning-budget 0
```

```bash
python inference/client.py "I forgot my yusan." --port 8080
```

The same command is suitable for a Grok Bot VM after downloading `WordStitch-4B-Q4_K_M.gguf` directly from Hugging Face. Bind to a private interface or place authentication in front of the server before exposing it to a network.

## Ollama

```bash
curl -L -o WordStitch-4B-Q4_K_M.gguf \
  https://huggingface.co/heavry/WordStitch-4B/resolve/main/WordStitch-4B-Q4_K_M.gguf
ollama create wordstitch -f inference/Modelfile
ollama run wordstitch "I forgot my yusan."
```

## LoRA adapter

The adapter is in the Hugging Face model repository under `adapter/`. It must be applied to the exact training base revision above. The adapter config in the public model repository names that base explicitly.

## Merged BF16

Download the Transformers-ready full model without cloning the other artifacts:

```bash
hf download heavry/WordStitch-4B --include "merged/*" --local-dir ./WordStitch-4B
```

Load `./WordStitch-4B/merged` with `AutoTokenizer` and `Qwen3_5ForConditionalGeneration`. The three safetensors shards and their hashes are recorded in `merged/SHA256SUMS`.

## Training and data

Training used 9,710 rows and 576 group-isolated validation rows. The public repository includes the training and data-construction code, frozen evaluation, aggregate data manifest, and attribution. It does not publish the complete training corpus. Tatoeba-derived parallel text has attribution and source-specific terms; CC-CEDICT-derived mappings require CC BY-SA 4.0 attribution/share-alike; synthetic teacher rows and mixed-source transformations need a separate redistribution review. See [`docs/PROVENANCE.md`](docs/PROVENANCE.md) and [`docs/DATA.md`](docs/DATA.md).

## License

Repository code and original documentation are licensed under Apache-2.0. The model chain is Qwen → HauhauCS/rodrigomt → WordStitch LoRA → merged BF16/Q4_K_M. Because the immediate rodrigomt conversion did not expose explicit license metadata when reviewed, the Hugging Face model repository remains `license: other`, and the merged weights are not labeled Apache-2.0. Model artifacts remain subject to upstream terms; see [`NOTICE`](NOTICE) and [`docs/LICENSE_REVIEW.md`](docs/LICENSE_REVIEW.md). This is a provenance record, not legal advice.

## Citation

If you use this alpha release, link to this repository and the Hugging Face model page. A formal paper citation is not currently available.

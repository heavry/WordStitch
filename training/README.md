# Training notes

This directory preserves the scripts used for the v0.2 Alpha run. They are research artifacts rather than a turnkey hosted training product.

The run used Transformers 5.16.1, PEFT 0.20.0, PyTorch 2.6.0+cu124, BF16, and a single RTX 4090D 24GB. The exact effective configuration is recorded in `config.json`:

- LoRA rank 16, alpha 32, dropout 0.05
- target projections: attention, DeltaNet, and MLP projection modules
- effective batch size 16
- learning rate 5e-5
- maximum sequence length 384
- 600 steps; checkpoint 500 selected by validation loss

Scripts expect local `base`, `data`, and `runs` paths. Before reproducing, obtain the named base model, perform your own license review, and prepare data using the documented provenance rules. The full mixed-source training data is not included.


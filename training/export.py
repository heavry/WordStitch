import torch,json,shutil
from pathlib import Path
from transformers import AutoTokenizer,Qwen3_5ForConditionalGeneration
from peft import PeftModel
base=Qwen3_5ForConditionalGeneration.from_pretrained('base',dtype=torch.bfloat16,device_map='cpu')
m=PeftModel.from_pretrained(base,'runs/best').merge_and_unload();m.save_pretrained('merged',safe_serialization=True,max_shard_size='4GB');AutoTokenizer.from_pretrained('base').save_pretrained('merged')
for f in ['preprocessor_config.json','video_preprocessor_config.json','chat_template.jinja']:
 if Path('base',f).exists():shutil.copy(Path('base',f),Path('merged',f))
print('exported',sum(p.numel() for p in m.parameters()),flush=True)

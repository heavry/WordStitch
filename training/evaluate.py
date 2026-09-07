import argparse,json,time,torch
from pathlib import Path
from transformers import AutoTokenizer,Qwen3_5ForConditionalGeneration
from common import SYSTEM
p=argparse.ArgumentParser();p.add_argument('--base',default='base');p.add_argument('--adapter');p.add_argument('--out',required=True);p.add_argument('--limit',type=int);a=p.parse_args()
torch.set_num_threads(8)
tok=AutoTokenizer.from_pretrained(a.base)
m,info=Qwen3_5ForConditionalGeneration.from_pretrained(a.base,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
print('LOADING',info,flush=True)
if a.adapter:
 from peft import PeftModel
 m=PeftModel.from_pretrained(m,a.adapter)
m.eval();rows=[]
for fn in ['evaluation/frozen.jsonl','evaluation/retention.jsonl']:
 rows.extend(json.loads(l) for l in open(fn))
if a.limit:rows=rows[:a.limit]
with open(a.out,'w') as f:
 for r in rows:
  msgs=[{'role':'system','content':'You are a helpful assistant. Answer concisely.' if r.get('mode')=='general' else SYSTEM},{'role':'user','content':r['input']}]
  inp=tok.apply_chat_template(msgs,tokenize=True,add_generation_prompt=True,enable_thinking=False,return_tensors='pt',return_dict=True).to('cuda');t=time.time()
  with torch.inference_mode():out=m.generate(**inp,max_new_tokens=160,do_sample=False,pad_token_id=tok.eos_token_id)
  s=tok.decode(out[0,inp['input_ids'].shape[1]:],skip_special_tokens=True)
  r.update(output=s,seconds=time.time()-t);f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();print(r['id'],s,flush=True)
print('VRAM',torch.cuda.max_memory_allocated()/1e9,flush=True)

import os,json,time,math,random,argparse
from pathlib import Path
import torch
from torch.utils.data import Dataset,DataLoader
from transformers import AutoTokenizer,Qwen3_5ForConditionalGeneration
from peft import LoraConfig,get_peft_model
from common import SYSTEM
# Validated FLA forward/backward substitutes only the DeltaNet chunk core.
from fla.ops.gated_delta_rule import chunk_gated_delta_rule
import transformers.models.qwen3_5.modeling_qwen3_5 as qwen_impl
assert Path('evaluation/kernel_check.json').exists(), 'Run numerical kernel validation first'
def validated_delta(q,k,v,**kw):
 return chunk_gated_delta_rule(q,k,v,**{key:value for key,value in kw.items() if key in {'g','beta','scale','initial_state','output_final_state','use_qk_l2norm_in_kernel','cu_seqlens'}})
qwen_impl.torch_chunk_gated_delta_rule = validated_delta
p=argparse.ArgumentParser();p.add_argument('--steps',type=int,default=600);p.add_argument('--batch',type=int,default=2);p.add_argument('--accum',type=int,default=8);p.add_argument('--lr',type=float,default=5e-5);p.add_argument('--resume');a=p.parse_args()
import signal
signal.signal(signal.SIGTERM,lambda signum,frame: (_ for _ in ()).throw(KeyboardInterrupt()))
random.seed(9041);torch.manual_seed(9041);torch.set_num_threads(8)
tok=AutoTokenizer.from_pretrained('base');tok.pad_token=tok.eos_token
class Data(Dataset):
 def __init__(self,path):
  self.rows=[]
  for line in open(path):
   r=json.loads(line);msgs=[{'role':'system','content':'You are a helpful assistant. Answer concisely.' if r.get('mode')=='general' else SYSTEM},{'role':'user','content':r['input']}]
   prefix=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True,enable_thinking=False)
   x=tok.encode(prefix,add_special_tokens=False);y=tok.encode(r['target']+'<|im_end|>',add_special_tokens=False)
   if len(x)+len(y)<=384:self.rows.append((x+y,[-100]*len(x)+y))
 def __len__(self):return len(self.rows)
 def __getitem__(self,i):return self.rows[i]
def collate(rows):
 n=math.ceil(max(len(x[0]) for x in rows)/64)*64;return {'input_ids':torch.tensor([x+[tok.pad_token_id]*(n-len(x)) for x,y in rows]),'labels':torch.tensor([y+[-100]*(n-len(y)) for x,y in rows]),'attention_mask':torch.tensor([[1]*len(x)+[0]*(n-len(x)) for x,y in rows])}
train=Data('data/train.jsonl');val=Data('data/validation.jsonl')
loader=DataLoader(train,batch_size=a.batch,shuffle=True,collate_fn=collate,num_workers=2,pin_memory=True);vl=DataLoader(val,batch_size=a.batch,collate_fn=collate,num_workers=2,pin_memory=True)
m=Qwen3_5ForConditionalGeneration.from_pretrained('base',dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa')
cfg=LoraConfig(r=16,lora_alpha=32,lora_dropout=0.05,target_modules=['q_proj','k_proj','v_proj','o_proj','in_proj_qkv','in_proj_z','out_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM')
if a.resume:
 from peft import PeftModel
 m=PeftModel.from_pretrained(m,a.resume,is_trainable=True)
else:m=get_peft_model(m,cfg)
m.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});m.enable_input_require_grads();m.config.use_cache=False
params=[x for x in m.parameters() if x.requires_grad];opt=torch.optim.AdamW(params,lr=a.lr,weight_decay=.01)
Path('runs').mkdir(exist_ok=True);conf={**vars(a),'lora':cfg.to_dict(),'train_rows':len(train),'val_rows':len(val),'trainable_parameters':sum(x.numel() for x in params),'total_parameters':sum(x.numel() for x in m.parameters()),'precision':'BF16','seed':9041}
Path('runs/config.json').write_text(json.dumps(conf,default=list,indent=2));print(conf,flush=True)
def validate():
 m.eval();total=0;nt=0
 with torch.no_grad():
  for b in vl:
   b={k:v.cuda(non_blocking=True) for k,v in b.items()};n=(b['labels']!=-100).sum().item()
   with torch.autocast('cuda',dtype=torch.bfloat16):loss=m(**b).loss
   total+=loss.item()*n;nt+=n
 m.train();return total/nt
start_step=0
if a.resume:
 state=torch.load('runs/resume_state.pt',map_location='cpu',weights_only=False);start_step=state['step'];assert a.resume.endswith(str(start_step));opt.load_state_dict(state['optimizer']);torch.set_rng_state(state['torch_rng']);torch.cuda.set_rng_state(state['cuda_rng']);random.setstate(state['python_rng'])
start=time.time();best=validate();print('BASE VAL',best,flush=True);it=iter(loader);m.train();history=json.loads(Path('runs/history.json').read_text()) if a.resume else [];tokens=0;optimization_seconds=0
try:
 for step in range(start_step+1,a.steps+1):
  step_start=time.time();opt.zero_grad(set_to_none=True);loss_sum=0
  for micro in range(a.accum):
   try:b=next(it)
   except StopIteration:it=iter(loader);b=next(it)
   tokens+=int(b['attention_mask'].sum());b={k:v.cuda(non_blocking=True) for k,v in b.items()}
   with torch.autocast('cuda',dtype=torch.bfloat16):loss=m(**b).loss/a.accum
   loss.backward();loss_sum+=loss.item()
  grad=torch.nn.utils.clip_grad_norm_(params,1.0)
  if not torch.isfinite(grad):raise RuntimeError('Nonfinite gradient')
  scale=min(1,step/30)*(.1+.9*.5*(1+math.cos(math.pi*step/a.steps)))
  for g in opt.param_groups:g['lr']=a.lr*scale
  opt.step();torch.cuda.synchronize();optimization_seconds+=time.time()-step_start
  if step%10==0:
   row={'step':step,'loss':loss_sum,'seconds':time.time()-start,'tokens_s':tokens/(time.time()-start),'vram_gb':torch.cuda.max_memory_allocated()/1e9,'eta_s':(time.time()-start)/max(step-start_step,1)*(a.steps-step)};print(json.dumps(row),flush=True);history.append(row)
  if step%100==0 or step==a.steps:
   v=validate();row={'step':step,'validation_loss':v,'seconds':time.time()-start};history.append(row);print(json.dumps(row),flush=True)
   m.save_pretrained(f'runs/step-{step}');tok.save_pretrained(f'runs/step-{step}')
   torch.save({'step':step,'optimizer':opt.state_dict(),'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state(),'python_rng':random.getstate()},'runs/resume_state.pt')
   if v<best:best=v;Path('runs/best.json').write_text(json.dumps(row));m.save_pretrained('runs/best');tok.save_pretrained('runs/best')
   Path('runs/history.json').write_text(json.dumps(history,indent=2))
finally:
 m.save_pretrained('runs/latest');tok.save_pretrained('runs/latest');Path('runs/history.json').write_text(json.dumps(history,indent=2));Path('runs/duration.json').write_text(json.dumps({'seconds':time.time()-start,'optimization_seconds':optimization_seconds,'last_step':step if 'step' in locals() else 0}))

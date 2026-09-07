import json,re,hashlib,collections,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];work=root.parents[1]/'work/wordstitch4b'
def norm(s):return re.sub(r'[^\w]','',s.lower())
tests=[json.loads(l) for f in ['frozen.jsonl','retention.jsonl'] for l in open(root/'evaluation'/f)];blocked={norm(r[k]) for r in tests for k in ['input','target']}
sets={s:[json.loads(l) for l in open(root/f'data/{s}.jsonl')] for s in ['train','validation']}
known={norm(r['target']):s for s,rows in sets.items() for r in rows}
new=[]
for f in ['luna_new.jsonl','luna_rehearsal.jsonl']:
 for i,l in enumerate(open(work/f)):
  r=json.loads(l)
  if '蒸发' in r['input']:continue
  r['source']=f'luna_4b:{f}:{i+1}'
  for bad,good in [('sharp tupo','sharp jizeng'),('quehao field','queshi field'),('raw ceshi','raw celiang'),('two bianmaqi','two bianjiemaqi')]:r['input']=r['input'].replace(bad,good)
  if 'A heated argument delayed the ditie doors' in r['input']:
   r['input']='A heated argument prevented the ditie doors from closing for several minutes.';r['target']='A heated argument prevented the subway doors from closing for several minutes.'
  if norm(r['input']) in blocked or norm(r['target']) in blocked:continue
  g=norm(r['target']);split=known.get(g,'validation' if int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%100<5 else 'train')
  r['group']=g;r['split']=split
  if r.get('category')=='trilingual' and not re.search('[\u4e00-\u9fff]',r['input']):r['category']='standard_rescue'
  new.append(r);sets[split].extend([r]*(4 if split=='train' and r.get('mode')=='general' else 2 if split=='train' else 1))
(root/'data/luna_4b_reviewed.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in new))
for s,rows in sets.items():(root/f'data/{s}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
assert not ({norm(r['target']) for r in sets['train']} & {norm(r['target']) for r in sets['validation']})
m=json.loads((root/'data/manifest.json').read_text());m['teacher_augmentation']={'unique':len(new),'general_replay_train_weight':4,'new_rescue_train_weight':2};m['final']={s:{'rows':len(rows),'categories':dict(collections.Counter(r['category'] for r in rows)),'sha256':hashlib.sha256((root/f'data/{s}.jsonl').read_bytes()).hexdigest()} for s,rows in sets.items()};(root/'data/manifest.json').write_text(json.dumps(m,indent=2));print(m['final'])

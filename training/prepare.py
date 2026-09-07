import json,re,random,hashlib,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]; old=root.parent/'WordStitch';rng=random.Random(9041)
def norm(s):return re.sub(r'[^\w]','',s.lower())
tests=[json.loads(l) for f in ['frozen.jsonl','retention.jsonl'] for l in open(root/'evaluation'/f)]
blocked={norm(r[k]) for r in tests for k in ['input','target']}
limits={'typo_rescue':2200,'standard_rescue':1400,'spaced_rescue':1000,'trilingual_rescue':1000,'chinese_pinyin':800,'chinese_english':700,'chinese':600,'english_identity':1200}
manifest={};allrows=[]
for split in ['train','validation']:
 rows=[json.loads(l) for l in open(old/f'data/general/sft_{split}.jsonl')];rng.shuffle(rows);counts=collections.Counter();groups=collections.Counter();chosen=[];seen=set()
 for r in rows:
  if not r['source'].startswith(('parallel:','tatoeba:','luna','extra')):continue
  if not 4<=len(r['target'].split())<=42:continue
  if norm(r['input']) in blocked or norm(r['target']) in blocked:continue
  cat=r['category'];cap=limits.get(cat,200) if split=='train' else min(70,limits.get(cat,40))
  if counts[cat]>=cap or groups[norm(r['target'])]>=2:continue
  if (r['input'],r['target']) in seen:continue
  if any(x in r['target'] for x in ['<','>','http','  ']):continue
  chosen.append(r);seen.add((r['input'],r['target']));counts[cat]+=1;groups[norm(r['target'])]+=1
 (root/f'data/{split}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in chosen));manifest[split]={'n':len(chosen),'categories':dict(counts)}
manifest['policy']='Reuse parallel-source and audited Luna data only; max two variants per target; fixed prior group split; frozen test input/target normalized exact exclusion. No benchmark-answer training. MiniMind token caches not reused.'
(root/'data/manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest)

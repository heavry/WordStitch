import json,re,hashlib,collections
from pathlib import Path
p=Path('outputs/WordStitch-4B/data');sets={s:[json.loads(l) for l in open(p/f'{s}.jsonl')] for s in ['train','validation']};norm=lambda s:re.sub(r'[^\w]','',s.lower());known={norm(r['target']):s for s,rows in sets.items() for r in rows};blocked={norm(r[k]) for f in ['frozen.jsonl','retention.jsonl'] for r in map(json.loads,open(p.parent/'evaluation'/f)) for k in ['input','target']};new=[]
for i,l in enumerate(open('work/wordstitch4b/luna_extra80.jsonl')):
 r=json.loads(l);r['input']=r['input'].replace('wanzi','wan').replace('shan dong tunnel','shan ti tunnel');r['target']=r['target'].replace('late-night breeze','night breeze')
 if r['category']=='continuous_pinyin':r['category']='multi_or_initial_rescue'
 if any(norm(r[k]) in blocked for k in ['input','target']):continue
 g=norm(r['target']);s=known.get(g,'validation' if int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%100<5 else 'train');r.update(source=f'luna_extra80:{i+1}',group=g,split=s);sets[s].extend([r]*(2 if s=='train' else 1));new.append(r)
(p/'luna_extra80_reviewed.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in new));m=json.load(open(p/'manifest.json'));m['extra80_unique']=len(new)
for s,rows in sets.items():
 (p/f'{s}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));m['final'][s]={'rows':len(rows),'categories':dict(collections.Counter(r['category'] for r in rows)),'sha256':hashlib.sha256((p/f'{s}.jsonl').read_bytes()).hexdigest()}
assert not ({norm(r['target']) for r in sets['train']} & {norm(r['target']) for r in sets['validation']})
(p/'manifest.json').write_text(json.dumps(m,indent=2));print({s:len(rows) for s,rows in sets.items()})

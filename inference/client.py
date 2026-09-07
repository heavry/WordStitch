import json,urllib.request,argparse
from common import SYSTEM
p=argparse.ArgumentParser();p.add_argument('text');p.add_argument('--general',action='store_true');p.add_argument('--port',type=int,default=18787);a=p.parse_args()
b={'messages':[{'role':'system','content':'You are a helpful assistant. Answer concisely.' if a.general else SYSTEM},{'role':'user','content':a.text}],'temperature':0,'max_tokens':160,'chat_template_kwargs':{'enable_thinking':False}}
r=urllib.request.Request(f'http://127.0.0.1:{a.port}/v1/chat/completions',data=json.dumps(b).encode(),headers={'Content-Type':'application/json'})
print(json.load(urllib.request.urlopen(r,timeout=120))['choices'][0]['message']['content'].strip())

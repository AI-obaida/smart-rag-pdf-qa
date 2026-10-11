"""Read-only local accuracy response collector for Smart RAG.
Run from project directory with Python 3.11. Requires CSV template in cwd.
No database writes. Calls GET /api/documents and POST /api/ask only.
"""
import csv
import json
import time
import urllib.request
from pathlib import Path

BASE = 'http://127.0.0.1:5000'
INPUT = Path('Smart_RAG_Accuracy_Evaluation_Template.csv')
OUTPUT = Path('Smart_RAG_Accuracy_Observed_Responses.csv')

def api(path, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'} if data else {}, method='POST' if data else 'GET')
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.load(response)

if not INPUT.is_file():
    raise SystemExit('STOP: Place Smart_RAG_Accuracy_Evaluation_Template.csv in current project directory.')
with INPUT.open(encoding='utf-8-sig', newline='') as file:
    rows = list(csv.DictReader(file))
if len(rows) != 20:
    raise SystemExit('STOP: Expected 20 questions; no requests sent.')
docs = api('/api/documents').get('documents', [])
ready = [d for d in docs if d.get('ready')]
print('Ready documents:', len(ready))
for d in ready:
    print('Document:', d.get('id'), d.get('filename'), 'pages:', d.get('pages'))
try:
    document_id = int(input('Enter the verified 14-page requirements PDF document ID: ').strip())
except ValueError:
    raise SystemExit('STOP: Invalid document ID')
if not any(d.get('id') == document_id and d.get('pages') == 14 for d in ready):
    raise SystemExit('STOP: ID must refer to a ready 14-page document; verify source before proceeding.')
if OUTPUT.exists():
    raise SystemExit('STOP: Output already exists; refusing to overwrite.')
fields = ['ID','Category','Question','Expected answer / rubric','Observed response','Status','Latency seconds','Citations','Correct (1/0)','Citation correct (1/0)','Notes']
with OUTPUT.open('x', encoding='utf-8-sig', newline='') as file:
    writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
    for index, row in enumerate(rows, 1):
        print('Question', index, 'of', len(rows), row['ID'], flush=True)
        start=time.perf_counter()
        try:
            response=api('/api/ask',{'document_id':document_id,'question':row['Question'],'top_k':3})
            items=response.get('items',[])
            answer=' | '.join(str(item.get('fact','')) for item in items)
            citations=' | '.join(f"page {item.get('page_number')} / {item.get('source_id')}" for item in items)
            status=response.get('status','unknown')
        except Exception as exc:
            answer='REQUEST ERROR: '+str(exc);citations='';status='error'
        writer.writerow({'ID':row['ID'],'Category':row['Category'],'Question':row['Question'],'Expected answer / rubric':row['Expected answer / rubric'],'Observed response':answer,'Status':status,'Latency seconds':round(time.perf_counter()-start,3),'Citations':citations,'Correct (1/0)':'','Citation correct (1/0)':'','Notes':''})
        file.flush()
print('Saved:', OUTPUT.resolve())
print('Manual ground-truth scoring required; no numeric accuracy is claimed.')

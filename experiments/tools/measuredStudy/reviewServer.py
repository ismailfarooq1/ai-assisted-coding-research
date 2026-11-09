#!/usr/bin/env python3
"""Local human review UI with participant-controlled, heartbeat-bounded intervals."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import time
from urllib.parse import parse_qs, urlparse

import studyRunner as study

class ReviewTimer:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.start = None
        self.last = None
        self.intervals = []

    def expire(self):
        if self.start is not None and self.clock() - self.last > 10:
            self.pause('heartbeat-loss', self.last + 10)

    def resume(self):
        self.expire()
        if self.start is None:
            self.start = self.last = self.clock()

    def heartbeat(self):
        self.expire()
        if self.start is not None:
            self.last = self.clock()

    def pause(self, reason='participant', end=None):
        if self.start is not None:
            stop = min(self.clock(), end) if end is not None else self.clock()
            self.intervals.append({'activeSeconds': max(0, stop - self.start), 'reasonEnded': reason})
            self.start = self.last = None

    def value(self):
        self.expire()
        current = max(0, self.clock() - self.start) if self.start is not None else 0
        return {'active': self.start is not None, 'activeSeconds': sum(i['activeSeconds'] for i in self.intervals) + current, 'intervals': list(self.intervals)}

HTML = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Memos context review</title>
<style>body{max-width:1050px;margin:35px auto;padding:0 20px;font:17px/1.5 system-ui;color:#202124;background:#fafafa}h1{font-size:28px}button,select,textarea{font:inherit}button{padding:8px 16px;margin:5px;cursor:pointer}textarea{width:97%;min-height:90px;padding:10px}article,details,.panel{background:white;padding:20px;margin:18px 0;border:1px solid #ddd;border-radius:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}#bar{position:sticky;top:0;background:#fff;padding:12px;border:1px solid #aaa}label{display:block;margin:10px 0}.note{color:#555}#message{white-space:pre-wrap}#content[hidden]{display:none}</style>
<h1>Timed review of prepared Memos context</h1>
<p>Review the context against its cited source text. Correct factual mistakes or remove unsupported claims. This records your review participation, not an estimate based on agent runtime.</p>
<p class="note">Start when ready to read. Pause for breaks. Hiding this tab pauses the timer; resume explicitly when you return. Heartbeat loss pauses it within 10 seconds. This is study data collection; completing it does not launch coding.</p>
<div id="bar"><button id="start">Start / resume review</button><button id="pause">Pause</button><strong id="timer">Not started</strong></div>
<p id="message"></p><div id="content" hidden><div id="maintenance"></div><div id="claims"></div><h2>Coverage</h2><p>Record whether the final guide covers each topic. Missing coverage remains visible in the study.</p><div id="coverage"></div><h2>Review notes</h2><textarea id="notes" placeholder="Anything uncertain or relevant to your review"></textarea><div id="documents"></div><button id="save">Save draft</button><button id="complete">Complete review and save context</button></div>
<script>
const key = new URLSearchParams(location.search).get('key'); let packet=null, active=false, loaded=false;
const $=id=>document.getElementById(id);
async function api(action, extra={}){const r=await fetch('/api?key='+encodeURIComponent(key),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,...extra})});const v=await r.json();if(!r.ok)throw Error(v.error);return v}
function status(v){active=v.active;$('timer').textContent=(v.active?'Review active: ':'Paused: ')+Math.floor(v.activeSeconds/60)+'m '+Math.floor(v.activeSeconds%60)+'s'}
function selection(values){const s=document.createElement('select');for(const [value,label] of values){const o=document.createElement('option');o.value=value;o.textContent=label;s.append(o)}return s}
function render(p,draft){packet=p;$('content').hidden=false;if(p.beforeClaims){const panel=document.createElement('div');panel.className='panel';const h=document.createElement('h2');h.textContent='Controlled change and prior guidance';panel.append(h);const facts=document.createElement('pre');facts.textContent=JSON.stringify(p.metadata.facts,null,2);panel.append(facts);const note=document.createElement('p');note.textContent='Judge each prior item against the changed source. A multi-instruction item is stale if any actionable instruction is false; this counts review items, not atomic facts. Then verify the maintained documents below.';panel.append(note);for(const c of p.beforeClaims){const d=document.createElement('details');const h=document.createElement('summary');h.textContent=c.id+' · '+c.topic;const pre=document.createElement('pre');pre.textContent=c.text;d.append(h,pre);panel.append(d);const sel=selection([['','Judge prior item'],['supported','Still supported'],['stale','Contains stale instruction'],['unresolved','Unresolved']]);sel.dataset.before=c.id;sel.value=draft?.beforeJudgments?.[c.id]??'';panel.append(sel)}for(const [name,value] of Object.entries(p.metadata.facts)){const l=document.createElement('label');l.textContent=name+': '+value+' ';const sel=selection([['','Verify in final guidance'],['yes','Accurate and covered'],['no','Missing or inaccurate'],['unresolved','Unresolved']]);sel.dataset.fact=name;sel.value=draft?.requiredFacts?.[name]??'';l.append(sel);panel.append(l)}$('maintenance').append(panel);}for(const c of p.claims){const a=document.createElement('article');const h=document.createElement('h2');h.textContent=c.id+' · '+c.topic;a.append(h);const t=document.createElement('textarea');t.id='text-'+c.id;if(p.editableDocuments&&p.metadata.method==='A'){t.readOnly=true;}t.value=draft?.claims?.find(x=>x.id===c.id)?.text??c.text;a.append(t);const s=selection([['','Choose a judgment'],['supported','Supported by the source'],['corrected','Corrected after checking source'],['remove','Remove unsupported claim'],['unresolved','Unresolved']]);s.id='judgment-'+c.id;s.value=draft?.claims?.find(x=>x.id===c.id)?.judgment??'';a.append(s);for(const source of c.sources){const d=document.createElement('details');const summary=document.createElement('summary');summary.textContent=source;const pre=document.createElement('pre');pre.textContent=p.sourceTexts[source];d.append(summary,pre);a.append(d)}$('claims').append(a)}for(const topic of p.coverageTopics){const l=document.createElement('label');l.textContent=topic+' ';const s=selection([['','Choose'],['yes','Covered'],['no','Missing'],['unresolved','Unresolved']]);s.dataset.topic=topic;s.value=draft?.coverage?.[topic]??'';l.append(s);$('coverage').append(l)}$('notes').value=draft?.notes??'';if(p.editableDocuments){const h=document.createElement('h2');h.textContent='Maintained documentation (edit if needed)';$('documents').append(h);for(const [name,text]of Object.entries(p.editableDocuments)){const l=document.createElement('label');l.textContent=name;const t=document.createElement('textarea');t.style.minHeight='380px';t.dataset.document=name;t.value=draft?.documents?.[name]??text;l.append(t);$('documents').append(l)}}loaded=true}
function collect(){return {beforeJudgments:Object.fromEntries([...$('maintenance').querySelectorAll('select[data-before]')].map(s=>[s.dataset.before,s.value])),requiredFacts:Object.fromEntries([...$('maintenance').querySelectorAll('select[data-fact]')].map(s=>[s.dataset.fact,s.value])),claims:packet.claims.map(c=>({...c,text:$('text-'+c.id).value,judgment:$('judgment-'+c.id).value})),coverage:Object.fromEntries([...$('coverage').querySelectorAll('select')].map(s=>[s.dataset.topic,s.value])),notes:$('notes').value,documents:Object.fromEntries([...$('documents').querySelectorAll('textarea')].map(t=>[t.dataset.document,t.value]))}}
async function act(action,extra={}){try{const v=await api(action,extra);status(v.timer);if(v.packet&&!loaded)render(v.packet,v.draft);$('message').textContent=v.message??'';if(v.completed){$('complete').disabled=true;$('start').disabled=true;$('message').textContent='Review completed and recorded. You can return to the chat. Coding has not started.'}}catch(e){$('message').textContent=e.message}}
$('start').onclick=()=>act('start');$('pause').onclick=()=>act('pause',loaded?{draft:collect()}:{});$('save').onclick=()=>act('save',{draft:collect()});$('complete').onclick=()=>act('complete',{draft:collect()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)act('pause',loaded?{draft:collect()}:{});});setInterval(()=>{if(active&&!document.hidden)act('heartbeat')},3000);window.addEventListener('pagehide',()=>{if(active)fetch('/api?key='+encodeURIComponent(key),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'pause',draft:loaded?collect():null}),keepalive:true})});
</script></html>'''

def serve(identifier, port):
    directory = study.REPORT / 'humanReview' / identifier
    packet = study.read(directory / 'packet.json')
    completion = directory / 'completion.json'
    if completion.exists():
        raise RuntimeError('Review already completed; refusing to alter sealed human record')
    timer = ReviewTimer()
    prior = directory / 'timerState.json'
    if prior.exists():
        state = study.read(prior)
        timer.intervals = state.get('intervals', [])
        # A crash does not grant an unobserved interval. Last heartbeat snapshot is the boundary.
        remaining = max(0, state.get('activeSeconds', 0) - sum(v['activeSeconds'] for v in timer.intervals))
        if remaining:
            timer.intervals.append({'activeSeconds': remaining, 'reasonEnded': 'server-restart-last-observed-snapshot'})
    token = secrets.token_urlsafe(24)
    draft_path = directory / 'draft.json'
    def save_state():
        state = timer.value()
        study.write(prior, state)
        return state
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def respond(self, code, body, kind='application/json'):
            data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(code); self.send_header('Content-Type', kind); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
        def authorized(self):
            return secrets.compare_digest(parse_qs(urlparse(self.path).query).get('key',[''])[0], token) and self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'
        def do_GET(self):
            if not self.authorized():
                return self.respond(403, {'error':'Invalid local review link'})
            self.respond(200, HTML, 'text/html; charset=utf-8')
        def do_POST(self):
            origin = self.headers.get('Origin')
            if not self.authorized() or (origin and origin != f'http://127.0.0.1:{self.server.server_port}'):
                return self.respond(403, {'error':'Invalid origin or review key'})
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length < 500000:
                    raise ValueError('Invalid request size')
                payload = json.loads(self.rfile.read(length))
                if completion.exists():
                    return self.respond(409, {'error':'Review already completed'})
                timer.expire()
                action = payload['action']
                if action in ('start','save','complete') and action != 'start' and not timer.value()['active']:
                    raise ValueError('Resume review before saving judgments or completing')
                if action == 'start': timer.resume()
                elif action == 'heartbeat': timer.heartbeat()
                elif action == 'pause': timer.pause()
                elif action not in ('save', 'complete'): raise ValueError('Unknown action')
                if payload.get('draft') is not None:
                    study.write(draft_path, payload['draft'])
                if action == 'complete':
                    draft = payload['draft']
                    if {c['id'] for c in draft['claims']} != {c['id'] for c in packet['claims']}:
                        raise ValueError('All claims must be reviewed')
                    if any(c.get('judgment') not in ('supported','corrected','remove') for c in draft['claims']):
                        raise ValueError('Resolve every claim or remove unsupported claims before completion')
                    if any(draft.get('coverage',{}).get(topic) not in ('yes','no') for topic in packet['coverageTopics']):
                        raise ValueError('Record coverage for each topic')
                    if packet.get('beforeClaims'):
                        if any(draft.get('beforeJudgments',{}).get(c['id']) not in ('supported','stale','unresolved') for c in packet['beforeClaims']):
                            raise ValueError('Judge every prior maintenance item')
                        if any(draft.get('requiredFacts',{}).get(name) not in ('yes','no','unresolved') for name in packet['metadata']['facts']):
                            raise ValueError('Record each required current fact')
                    original = {c['id']:c for c in packet['claims']}
                    claims = {'claims': [{**original[c['id']], 'text':c['text']} for c in draft['claims'] if c['judgment'] != 'remove']}
                    target = study.ROOT / packet['target']
                    if packet.get('editableDocuments') is None:
                        sources = study.read(target / 'sourceMap.json')['sources']
                        study.render_pack(claims, target, sources)
                    else:
                        documents = draft.get('documents',{})
                        if set(documents) != set(packet['editableDocuments']):
                            raise ValueError('Review all maintained documents')
                        for name, text in documents.items():
                            path = target / name
                            if not path.resolve().is_relative_to(target.resolve()): raise ValueError('Invalid document path')
                            path.write_text(text)
                        if packet['metadata']['method'] == 'B':
                            study.render_pack(claims, target / 'contextPack', study.read(target / 'contextPack/sourceMap.json')['sources'])
                    timer.pause('completed')
                    state = save_state()
                    study.write(completion, {'completed': True, 'completedAt': study.now(), 'activeSeconds':state['activeSeconds'], 'intervals':state['intervals'], 'judgments':draft, 'maintenanceItemCounts': {'beforeItems':len(packet.get('beforeClaims',[])), 'beforeStale':sum(v == 'stale' for v in draft.get('beforeJudgments',{}).values()), 'beforeUnresolved':sum(v == 'unresolved' for v in draft.get('beforeJudgments',{}).values()), 'requiredFactsCovered':sum(v == 'yes' for v in draft.get('requiredFacts',{}).values()), 'requiredFactsTotal':len(packet.get('metadata',{}).get('facts',{}))} if packet.get('beforeClaims') else None, 'beforeHashes':packet['beforeHashes'], 'afterHashes':{str(p.relative_to(target)):study.digest(p) for p in target.rglob('*') if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts} if packet.get('editableDocuments') else {p.name:study.digest(p) for p in target.glob('*') if p.is_file()}, 'measurement':'Participant-controlled active review intervals; heartbeat tolerance 10s; not verified attention'})
                state = save_state()
                self.respond(200, {'timer':state, 'packet':packet if action == 'start' else None, 'draft':study.read(draft_path) if draft_path.exists() and action == 'start' else None, 'completed':completion.exists()})
            except (ValueError, KeyError, TypeError, OSError) as error:
                self.respond(400, {'error':str(error), 'timer':save_state()})
    server = HTTPServer(('127.0.0.1', port), Handler)
    link = f'http://127.0.0.1:{server.server_port}/?key={token}'
    study.write(directory / 'server.json', {'url':link, 'startedAt':study.now(), 'port':server.server_port})
    print(json.dumps({'reviewUrl':link, 'packet':identifier, 'codingAutomaticallyStarted':False}), flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        timer.pause('server-stop'); save_state(); server.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', default='preparationB')
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    serve(args.packet, args.port)

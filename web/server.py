"""SciFlow 学术助手 - Web 前端 v3
多会话隔离 + 工作流展示
"""
import os, json, time, uuid, threading, requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

app = Flask(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GATEWAY_PORT = 18789
GATEWAY_BASE = f"http://127.0.0.1:{GATEWAY_PORT}"
SESSIONS_FILE = PROJECT_ROOT / "web" / "sessions.json"
_lock = threading.Lock()

def _load_token():
    try:
        conf = json.load(open(Path.home() / ".openclaw" / "openclaw.json"))
        return conf["gateway"]["auth"]["token"]
    except:
        return ""
GATEWAY_TOKEN = _load_token()

def ls(): return json.loads(SESSIONS_FILE.read_text()) if SESSIONS_FILE.exists() else {"sessions":{},"order":[]}
def ss(d): SESSIONS_FILE.write_text(json.dumps(d,ensure_ascii=False,indent=2))

@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/sessions", methods=["GET"])
def api_sessions():
    d=ls(); return jsonify([{"id":s,**d["sessions"].get(s,{})} for s in d["order"]])

@app.route("/api/sessions", methods=["POST"])
def api_create_session():
    d=ls(); sid=f"sess_{uuid.uuid4().hex[:12]}"
    d["sessions"][sid]={"id":sid,"title":"新对话","created":time.strftime("%H:%M"),"updated":time.strftime("%H:%M"),"message_count":0}
    d["order"].insert(0,sid); ss(d)
    return jsonify({"id":sid})

@app.route("/api/sessions/<sid>", methods=["DELETE"])
def api_delete_session(sid):
    d=ls(); d["sessions"].pop(sid,None); d["order"]=[s for s in d["order"] if s!=sid]
    mf=PROJECT_ROOT/"web"/"messages"/f"{sid}.json"
    if mf.exists(): mf.unlink()
    ss(d); return jsonify({"ok":True})

@app.route("/api/messages/<sid>", methods=["GET"])
def api_get_messages(sid):
    mf=PROJECT_ROOT/"web"/"messages"/f"{sid}.json"
    return jsonify(json.loads(mf.read_text()) if mf.exists() else [])

@app.route("/api/messages/<sid>", methods=["POST"])
def api_save_message(sid):
    data=request.json or {}
    mf=PROJECT_ROOT/"web"/"messages"/f"{sid}.json"
    mf.parent.mkdir(parents=True,exist_ok=True)
    msgs=data.get("messages",[])
    mf.write_text(json.dumps(msgs,ensure_ascii=False))
    d=ls()
    if sid in d["sessions"]:
        d["sessions"][sid]["message_count"]=len(msgs)
        d["sessions"][sid]["updated"]=time.strftime("%H:%M")
        if d["sessions"][sid]["title"]=="新对话":
            for m in msgs:
                if m.get("role")=="user":
                    t=m["content"][:30]
                    d["sessions"][sid]["title"]=t+("…" if len(m["content"])>30 else "")
                    break
        ss(d)
    return jsonify({"ok":True})

@app.route("/api/chat", methods=["POST"])
def chat():
    data=request.json or {}
    msgs=data.get("messages",[])
    sid=data.get("session_id","default")
    if not msgs: return jsonify({"error":"no messages"}),400
    fm=[{"role":m["role"],"content":m["content"]} for m in msgs]
    def gen():
        try:
            r=requests.post(f"{GATEWAY_BASE}/v1/chat/completions",
                headers={"Authorization":f"Bearer {GATEWAY_TOKEN}","Content-Type":"application/json"},
                json={"model":"openclaw","messages":fm,"user":sid,"stream":True},
                stream=True,timeout=(30,600))
            if r.status_code!=200:
                yield f"data: {json.dumps({'error':f'Gateway {r.status_code}'})}\n\n"; return
            lh=time.time()
            for line in r.iter_lines():
                if time.time()-lh>15: yield ": heartbeat\n\n"; lh=time.time()
                if not line: continue
                line=line.decode("utf-8")
                if line.startswith("data: "):
                    ds=line[6:]
                    if ds=="[DONE]": break
                    try:
                        c=json.loads(ds); txt=c["choices"][0].get("delta",{}).get("content","")
                        if txt: yield f"data: {json.dumps({'content':txt})}\n\n"
                    except: continue
            yield "data: [DONE]\n\n"
        except Exception as e: yield f"data: {json.dumps({'error':str(e)[:200]})}\n\n"
    return Response(stream_with_context(gen()),mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/health")
def health():
    try:
        r=requests.get(f"{GATEWAY_BASE}/v1/models",headers={"Authorization":f"Bearer {GATEWAY_TOKEN}"},timeout=5)
        return jsonify({"status":"ok","gateway":"connected","models":len(r.json().get("data",[]))})
    except: return jsonify({"status":"ok","gateway":"disconnected"})

# ─── 知识库 ──────────────────────────────────
KM_DIR = PROJECT_ROOT / "shared" / "knowledge_md"

@app.route("/api/knowledge", methods=["GET"])
def api_knowledge_list():
    files = []
    if KM_DIR.exists():
        for f in sorted(KM_DIR.rglob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            files.append({"name": f.stem, "path": f.name, "size": f.stat().st_size, "updated": time.strftime("%m-%d %H:%M", time.localtime(f.stat().st_mtime))})
    return jsonify(files)

@app.route("/api/knowledge/<path:fname>", methods=["GET"])
def api_knowledge_read(fname):
    fpath = KM_DIR / fname
    if not fpath.exists(): return jsonify({"error":"not found"}), 404
    return jsonify({"name": fpath.stem, "content": fpath.read_text(encoding="utf-8")})


# ─── 知识图谱 API ────────────────────────────────
import re
from collections import defaultdict

@app.route("/api/knowledge-graph", methods=["GET"])
def api_knowledge_graph():
    """从知识库构建关联图谱数据（力导向图格式）"""
    dba_path = PROJECT_ROOT / "shared" / "db_a" / "paper_knowledge.pkl"
    if not dba_path.exists():
        return jsonify({"nodes": [], "edges": []})

    import pickle
    with open(dba_path, "rb") as f:
        data = pickle.load(f)
    records = data.get("records", [])

    # 按 paper_id 去重，保留第一个
    seen = {}
    for r in records:
        pid = r["paper_id"]
        if pid not in seen:
            seen[pid] = r
    papers = list(seen.values())

    nodes = []
    edges = []
    node_ids = set()

    def add_node(nid, label, ntype, **kw):
        if nid not in node_ids:
            nodes.append({"id": nid, "label": label, "type": ntype, **kw})
            node_ids.add(nid)

    for p in papers:
        pid = p["paper_id"]
        short = p["title"][:32] + ("…" if len(p["title"]) > 32 else "")
        add_node(pid, short, "paper", title=p["title"], summary=p.get("summary", ""),
                 topics=p.get("related_topics", []), methods=p.get("methods_used", []),
                 tags=p.get("tags", []))

        for t in p.get("related_topics", []):
            t = t.strip()
            if not t:
                continue
            tid = f"topic:{t}"
            add_node(tid, t, "topic")
            edges.append({"source": pid, "target": tid, "relation": "belongs_to"})

        for m in p.get("methods_used", []):
            m = m.strip()
            if not m:
                continue
            mid = f"method:{m}"
            add_node(mid, m, "method")
            edges.append({"source": pid, "target": mid, "relation": "uses"})

    # 论文间共享主题 or 方法的隐含关联
    topic_papers = defaultdict(list)
    method_papers = defaultdict(list)
    for p in papers:
        pid = p["paper_id"]
        for t in p.get("related_topics", []):
            topic_papers[t.strip()].append(pid)
        for m in p.get("methods_used", []):
            method_papers[m.strip()].append(pid)

    related_seen = set()
    for cluster in [topic_papers, method_papers]:
        for _, pids in cluster.items():
            if len(pids) >= 2:
                for i in range(len(pids)):
                    for j in range(i + 1, len(pids)):
                        key = tuple(sorted([pids[i], pids[j]]))
                        if key not in related_seen:
                            related_seen.add(key)
                            edges.append({"source": pids[i], "target": pids[j], "relation": "related", "style": "dashed"})

    return jsonify({"nodes": nodes, "edges": edges})


if __name__=="__main__":
    print(f"🚀 SciFlow Web v3 | http://localhost:5000")
    app.run(host="0.0.0.0",port=5000,debug=False)

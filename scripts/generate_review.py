#!/usr/bin/env python3
"""
EN Learning Review Card Generator - 重写版
从学习库读取数据，生成每日复习 HTML 卡片页面
"""

import re
import os
import json
import random
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "daily_review.html")
DOCS_FILE = os.path.join(BASE_DIR, "docs", "index.html")

def load_config():
    config_path = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CONFIG = load_config()

def clean_text(text):
    """清理 Markdown，返回纯净文本"""
    lines = text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('|') or line.startswith('---'):
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        line = re.sub(r'\*(.+?)\*', r'\1', line)
        line = re.sub(r'^[-*]\s*', '', line)
        line = re.sub(r'^\[.*?\]：', '', line)
        line = re.sub(r'[^\x00-\x7F\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\s\w.,;:!?()/\-\'\"（）。，；：！？、]', '', line)
        line = line.strip()
        if line:
            result.append(line)
    return ' / '.join(result[:2]) if result else ''

def parse_words(filepath):
    items = []
    if not os.path.exists(filepath):
        return items
    content = open(filepath, encoding='utf-8').read()
    for entry in re.split(r'\n---\n', content):
        m = re.search(r'### (.+)', entry)
        if not m:
            continue
        word = m.group(1).strip()

        meaning = ''
        mm = re.search(r'\*\*中文释义\*\*：\s*\n(.*?)(?=\n\n|\*\*)', entry, re.DOTALL)
        if mm:
            meaning = clean_text(mm.group(1))
        if not meaning:
            # 备用：找第一个释义行
            mm2 = re.search(r'\[.*?\]：(.+)', entry)
            if mm2:
                meaning = mm2.group(1).strip()

        count = 1
        cm = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if cm:
            count = int(cm.group(1))

        ex_en = ''
        ex_cn = ''
        em = re.search(r'EN:\s*(.+)', entry)
        if em:
            ex_en = em.group(1).strip().lstrip('*').rstrip('*')
        cm2 = re.search(r'CN:\s*(.+)', entry)
        if cm2:
            ex_cn = cm2.group(1).strip()

        if word:
            items.append({
                'word': word,
                'meaning': meaning or '（查看词库了解详情）',
                'count': count,
                'type': 'word',
                'example_en': ex_en,
                'example_cn': ex_cn,
            })
    return items

def parse_usage(filepath):
    items = []
    if not os.path.exists(filepath):
        return items
    content = open(filepath, encoding='utf-8').read()
    for entry in re.split(r'\n---\n', content):
        m = re.search(r'### (.+)', entry)
        if not m:
            continue
        title = m.group(1).strip()
        count = 1
        cm = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if cm:
            count = int(cm.group(1))
        meaning = '用法辨析 - 查看词库了解详情'
        mm = re.search(r'\*\*核心区别\*\*\s*\n(.*?)(?=\*\*)', entry, re.DOTALL)
        if mm:
            meaning = clean_text(mm.group(1)) or meaning
        if title:
            items.append({'word': title, 'meaning': meaning, 'count': count,
                          'type': 'usage', 'example_en': '', 'example_cn': ''})
    return items

def parse_grammar(filepath):
    items = []
    if not os.path.exists(filepath):
        return items
    content = open(filepath, encoding='utf-8').read()
    for entry in re.split(r'\n---\n', content):
        m = re.search(r'### (.+)', entry)
        if not m:
            continue
        title = m.group(1).strip()
        count = 1
        cm = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if cm:
            count = int(cm.group(1))
        meaning = '语法规则 - 查看词库了解详情'
        mm = re.search(r'\*\*规则说明\*\*：(.+)', entry)
        if mm:
            meaning = clean_text(mm.group(1)) or meaning
        if title:
            items.append({'word': title, 'meaning': meaning, 'count': count,
                          'type': 'grammar', 'example_en': '', 'example_cn': ''})
    return items

def select_items(all_items, n=999):
    """返回所有需要今天复习的词，不设上限"""
    st = {}
    progress_file = os.path.join(BASE_DIR, "progress.json")
    if os.path.exists(progress_file):
        try:
            with open(progress_file, encoding="utf-8") as f:
                st = json.load(f)
        except Exception:
            st = {}

    def days_since(iso):
        if not iso:
            return 999
        try:
            from datetime import timezone
            last = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - last).days
        except Exception:
            return 999

    def needs_review(item_id):
        d = st.get(item_id)
        if not d or not d.get("lastDate"):
            return True
        gaps = [1, 2, 4, 7, 14, 30, 60]
        last = d.get("last", "")
        streak = d.get("streak", 0)
        if last == "forgot":
            return days_since(d["lastDate"]) >= 1
        if last == "fuzzy":
            return days_since(d["lastDate"]) >= 2
        gap = gaps[min(streak, len(gaps) - 1)]
        return days_since(d["lastDate"]) >= gap

    need = []
    rest = []
    for item in all_items:
        item_id = item["type"] + "_" + re.sub(r"\W+", "_", item["word"])
        item["id"] = item_id
        d = st.get(item_id)
        if needs_review(item_id):
            item["_streak"] = d.get("streak", 0) if d else 0
            item["_last"] = d.get("last", "") if d else ""
            need.append(item)
        # 不需要今天复习的就不加入

    # 排序：不认识 > 模糊 > 新词 > 认识中（按 streak 升序）
    def sort_key(item):
        last = item.get("_last", "")
        if last == "forgot":  return (0, 0)
        if last == "fuzzy":   return (1, 0)
        if last == "":        return (2, 0)
        return (3, item.get("_streak", 0))

    need.sort(key=sort_key)
    return need

def make_html(items):
    today = datetime.now().strftime('%Y-%m-%d')

    # 安全序列化成 JS 数组
    safe_items = []
    for item in items:
        safe_items.append({
            'id':   item['type'] + '_' + re.sub(r'\W+', '_', item['word']),
            'word': item['word'],
            'type': item['type'],
            'meaning':    item['meaning'],
            'example_en': item.get('example_en', ''),
            'example_cn': item.get('example_cn', ''),
            'count': item['count'],
        })

    data_json = json.dumps(safe_items, ensure_ascii=False)

    label = {'word': '单词', 'usage': '用法', 'grammar': '语法'}

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>英文复习 {today}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:#1a1a2e;min-height:100vh;color:#fff;padding:16px}}
h1{{text-align:center;font-size:22px;margin:20px 0 4px}}
.sub{{text-align:center;color:#aaa;font-size:13px;margin-bottom:20px}}
.stats{{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
.stat{{background:rgba(255,255,255,.1);border-radius:10px;padding:10px 18px;text-align:center}}
.stat .n{{font-size:22px;font-weight:bold}}
.stat .l{{font-size:11px;color:#aaa;margin-top:2px}}
.bar-wrap{{max-width:420px;margin:0 auto 6px;height:6px;background:rgba(255,255,255,.1);border-radius:6px;overflow:hidden}}
.bar{{height:100%;background:linear-gradient(90deg,#34c759,#30d158);border-radius:6px;transition:width .4s}}
.bar-txt{{text-align:center;font-size:12px;color:#aaa;margin-bottom:20px}}
/* 卡片 */
.deck{{max-width:420px;margin:0 auto}}
.card{{display:none;flex-direction:column;gap:14px}}
.card.active{{display:flex}}
.flip-area{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);
  border-radius:16px;padding:28px 24px;cursor:pointer;min-height:180px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-align:center;transition:background .2s;position:relative;user-select:none}}
.flip-area:active{{background:rgba(255,255,255,.13)}}
.badge{{position:absolute;top:12px;right:12px;font-size:11px;padding:2px 8px;border-radius:20px}}
.badge.weak{{background:rgba(255,59,48,.3)}}
.badge.medium{{background:rgba(255,204,0,.3)}}
.badge.new{{background:rgba(52,199,89,.3)}}
.card-type{{font-size:11px;color:#888;margin-bottom:8px}}
.card-word{{font-size:32px;font-weight:700;margin-bottom:6px;word-break:break-word}}
.card-hint{{font-size:12px;color:#666;margin-top:8px}}
.card-streak{{font-size:11px;color:#555;margin-top:4px}}
/* 答案面 */
.answer{{display:none;width:100%}}
.answer.show{{display:block}}
.answer-word{{font-size:18px;font-weight:600;color:#7dd3fc;margin-bottom:10px}}
.answer-meaning{{font-size:15px;line-height:1.7;color:#ddd;margin-bottom:10px}}
.answer-ex{{margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.1)}}
.ex-en{{font-size:13px;color:#7dd3fc;font-style:italic}}
.ex-cn{{font-size:12px;color:#aaa;margin-top:3px}}
/* 发音 */
.speak-btn{{background:none;border:1px solid rgba(125,211,252,.4);color:#7dd3fc;
  width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:15px;
  display:inline-flex;align-items:center;justify-content:center;
  margin-left:8px;vertical-align:middle;transition:background .2s}}
.speak-btn:hover{{background:rgba(125,211,252,.15)}}
/* 打分按钮 */
.rating{{display:flex;gap:10px;justify-content:center}}
.btn{{padding:12px 0;border:none;border-radius:10px;font-size:14px;
  font-weight:600;cursor:pointer;flex:1;transition:opacity .15s;
  -webkit-tap-highlight-color:transparent}}
.btn:active{{opacity:.75}}
.btn.forgot{{background:linear-gradient(135deg,#ff3b30,#ff6b6b);color:#fff}}
.btn.fuzzy{{background:linear-gradient(135deg,#ff9500,#ffcc00);color:#333}}
.btn.known{{background:linear-gradient(135deg,#34c759,#30d158);color:#fff}}
/* 导航 */
.nav{{display:flex;gap:10px;justify-content:center;margin-top:14px}}
.nav-btn{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);
  color:#fff;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:13px}}
.nav-btn:disabled{{opacity:.3;cursor:default}}
/* 完成页 */
.done{{display:none;max-width:420px;margin:0 auto;text-align:center;
  background:rgba(255,255,255,.08);border-radius:16px;padding:30px 24px}}
.done h2{{font-size:20px;margin-bottom:16px}}
.done-stats{{display:flex;gap:16px;justify-content:center;margin:16px 0}}
.done-item .dn{{font-size:28px;font-weight:700}}
.done-item .dl{{font-size:12px;color:#aaa;margin-top:3px}}
.done-list{{margin-top:16px;text-align:left}}
.done-row{{display:flex;justify-content:space-between;padding:6px 0;
  border-bottom:1px solid rgba(255,255,255,.06);font-size:13px}}
.done-actions{{display:flex;gap:10px;margin-top:20px;justify-content:center}}
.footer{{text-align:center;margin-top:30px;color:#444;font-size:11px}}
</style>
</head>
<body>

<h1>Daily English Review</h1>
<div class="sub">{today} · 点击卡片翻转查看答案</div>

<div class="stats">
  <div class="stat"><div class="n" id="sTotal">0</div><div class="l">总数</div></div>
  <div class="stat"><div class="n" id="sDone" style="color:#34c759">0</div><div class="l">已完成</div></div>
  <div class="stat"><div class="n" id="sKnown" style="color:#34c759">0</div><div class="l">认识</div></div>
  <div class="stat"><div class="n" id="sFuzzy" style="color:#ffcc00">0</div><div class="l">模糊</div></div>
  <div class="stat"><div class="n" id="sForgot" style="color:#ff3b30">0</div><div class="l">不认识</div></div>
</div>
<div class="bar-wrap"><div class="bar" id="bar" style="width:0"></div></div>
<div class="bar-txt" id="barTxt">开始复习吧</div>

<div class="deck" id="deck"></div>

<div class="done" id="done">
  <h2>今日复习完成！</h2>
  <div class="done-stats">
    <div class="done-item"><div class="dn" id="dKnown" style="color:#34c759">0</div><div class="dl">认识</div></div>
    <div class="done-item"><div class="dn" id="dFuzzy" style="color:#ffcc00">0</div><div class="dl">模糊</div></div>
    <div class="done-item"><div class="dn" id="dForgot" style="color:#ff3b30">0</div><div class="dl">不认识</div></div>
  </div>
  <div class="bar-txt" id="dRate"></div>
  <div class="done-list" id="dList"></div>
  <div class="done-actions">
    <button class="nav-btn" onclick="replayWeak()">重练不认识+模糊</button>
    <button class="nav-btn" onclick="replayAll()">全部重新来</button>
    <button class="nav-btn" onclick="saveProgress()" style="background:rgba(52,199,89,.25);border-color:#34c759">💾 保存进度</button>
  </div>
  <div id="saveHint" style="margin-top:12px;font-size:12px;color:#aaa;display:none">
    progress.json 已下载，请将它放到 EN_Learning_OC 文件夹里覆盖同名文件。
  </div>
</div>

<div class="nav" id="nav">
  <button class="nav-btn" id="btnPrev" onclick="prev()" disabled>← 上一个</button>
  <button class="nav-btn" id="btnSkip" onclick="skip()">跳过 →</button>
</div>

<div class="footer">EN Learning · {today}</div>

<script>
var ITEMS = {data_json};
var SK = 'enReview2';
var cur = 0, queue = [], res = {{}};

function store() {{
  try {{ return JSON.parse(localStorage.getItem(SK)) || {{}}; }} catch(e) {{ return {{}}; }}
}}
function save(d) {{
  try {{ localStorage.setItem(SK, JSON.stringify(d)); }} catch(e) {{}}
}}

function daysSince(iso) {{
  if (!iso) return 999;
  return Math.floor((Date.now() - new Date(iso)) / 86400000);
}}

function needsReview(d) {{
  if (!d || !d.lastDate) return true;
  var gaps = [1,2,4,7,14,30,60];
  if (d.last === 'forgot') return daysSince(d.lastDate) >= 1;
  if (d.last === 'fuzzy')  return daysSince(d.lastDate) >= 2;
  var gap = gaps[Math.min(d.streak||0, gaps.length-1)];
  return daysSince(d.lastDate) >= gap;
}}

function buildQueue() {{
  var st = store();
  var need = [], fresh = [];
  ITEMS.forEach(function(item) {{
    var d = st[item.id];
    if (!d) {{ fresh.push(item); return; }}
    if (needsReview(d)) {{
      item._pri = d.last==='forgot'?0:(d.last==='fuzzy'?1:2);
      need.push(item);
    }}
  }});
  need.sort(function(a,b){{ return (a._pri||0)-(b._pri||0); }});
  // 随机打乱 fresh
  for (var i=fresh.length-1;i>0;i--){{
    var j=Math.floor(Math.random()*(i+1));
    var t=fresh[i];fresh[i]=fresh[j];fresh[j]=t;
  }}
  queue = need.concat(fresh);
  if (queue.length === 0) queue = ITEMS.slice();
}}

function badgeClass(item) {{
  var d = store()[item.id];
  if (!d) return 'new';
  if (d.last==='forgot') return 'weak';
  if (d.last==='fuzzy') return 'medium';
  return 'new';
}}

function badgeLabel(item) {{
  var d = store()[item.id];
  if (!d) return '🟢 新学';
  if (d.last==='forgot') return '🔴 不认识';
  if (d.last==='fuzzy') return '🟡 模糊';
  if ((d.streak||0)>=3) return '🔵 已掌握';
  return '🟢 复习中';
}}

function streakText(item) {{
  var d = store()[item.id];
  if (!d) return '首次复习';
  return '连续认识 '+(d.streak||0)+' 次';
}}

function renderDeck() {{
  var deck = document.getElementById('deck');
  deck.innerHTML = '';
  queue.forEach(function(item, i) {{
    var typeLabel = {{'word':'单词','usage':'用法','grammar':'语法'}}[item.type]||item.type;
    var exHtml = '';
    if (item.example_en) {{
      exHtml = '<div class="answer-ex"><div class="ex-en">'+esc(item.example_en)+'</div>'
             + (item.example_cn?'<div class="ex-cn">'+esc(item.example_cn)+'</div>':'')
             + '</div>';
    }}
    var div = document.createElement('div');
    div.className = 'card' + (i===0?' active':'');
    div.dataset.i = i;
    div.innerHTML =
      '<div class="flip-area" onclick="flip(this)">'
      + '<span class="badge '+badgeClass(item)+'">'+badgeLabel(item)+'</span>'
      + '<div class="card-type">'+typeLabel+' · '+(i+1)+'/'+queue.length+'</div>'
      + '<div class="card-word">'+esc(item.word)+'</div>'
      + '<div class="answer" id="ans'+i+'">'
      + '<div class="answer-word">'+esc(item.word)
      + '<button class="speak-btn" onclick="speak(event,this)">&#128264;</button>'
      + '</div>'
      + '<div class="answer-meaning">'+esc(item.meaning)+'</div>'
      + exHtml
      + '</div>'
      + '<div class="card-hint" id="hint'+i+'">点击查看答案</div>'
      + '<div class="card-streak">'+streakText(item)+'</div>'
      + '</div>'
      + '<div class="rating" id="rating'+i+'" style="display:none">'
      + '<button class="btn forgot" onclick="rate('+i+',&quot;forgot&quot;)">不认识</button>'
      + '<button class="btn fuzzy"  onclick="rate('+i+',&quot;fuzzy&quot;)">模糊</button>'
      + '<button class="btn known"  onclick="rate('+i+',&quot;known&quot;)">认识</button>'
      + '</div>';
    deck.appendChild(div);
  }});
  updateStats();
}}

function flip(el) {{
  var i = el.closest('.card').dataset.i;
  var ans = document.getElementById('ans'+i);
  var hint = document.getElementById('hint'+i);
  var rating = document.getElementById('rating'+i);
  if (ans.classList.contains('show')) return;
  ans.classList.add('show');
  hint.style.display = 'none';
  rating.style.display = 'flex';
}}

function rate(i, r) {{
  var item = queue[i];
  var st = store();
  if (!st[item.id]) st[item.id] = {{streak:0}};
  st[item.id].last = r;
  st[item.id].lastDate = new Date().toISOString();
  if (r==='known') st[item.id].streak = (st[item.id].streak||0)+1;
  else             st[item.id].streak = 0;
  save(st);
  res[item.id] = r;
  updateStats();
  setTimeout(function(){{ goNext(); }}, 350);
}}

function goNext() {{
  var cards = document.querySelectorAll('.card');
  if (cur < cards.length-1) {{
    cards[cur].classList.remove('active');
    cur++;
    cards[cur].classList.add('active');
    document.getElementById('btnPrev').disabled = cur===0;
  }} else {{
    showDone();
  }}
}}

function prev() {{
  var cards = document.querySelectorAll('.card');
  if (cur > 0) {{
    cards[cur].classList.remove('active');
    cur--;
    cards[cur].classList.add('active');
    document.getElementById('btnPrev').disabled = cur===0;
  }}
}}

function skip() {{ goNext(); }}

function updateStats() {{
  var total = queue.length;
  var done  = Object.keys(res).length;
  var known  = Object.values(res).filter(function(v){{return v==='known';}}).length;
  var fuzzy  = Object.values(res).filter(function(v){{return v==='fuzzy';}}).length;
  var forgot = Object.values(res).filter(function(v){{return v==='forgot';}}).length;
  document.getElementById('sTotal').textContent  = total;
  document.getElementById('sDone').textContent   = done;
  document.getElementById('sKnown').textContent  = known;
  document.getElementById('sFuzzy').textContent  = fuzzy;
  document.getElementById('sForgot').textContent = forgot;
  var pct = total>0 ? Math.round(done/total*100) : 0;
  document.getElementById('bar').style.width = pct+'%';
  document.getElementById('barTxt').textContent = done===0
    ? '开始复习吧'
    : ('已完成 '+done+'/'+total+'，正确率 '+Math.round(known/Math.max(done,1)*100)+'%');
}}

function showDone() {{
  document.getElementById('deck').style.display = 'none';
  document.getElementById('nav').style.display  = 'none';
  var done = document.getElementById('done');
  done.style.display = 'block';
  var known  = Object.values(res).filter(function(v){{return v==='known';}}).length;
  var fuzzy  = Object.values(res).filter(function(v){{return v==='fuzzy';}}).length;
  var forgot = Object.values(res).filter(function(v){{return v==='forgot';}}).length;
  var total  = known+fuzzy+forgot;
  document.getElementById('dKnown').textContent  = known;
  document.getElementById('dFuzzy').textContent  = fuzzy;
  document.getElementById('dForgot').textContent = forgot;
  document.getElementById('dRate').textContent   =
    '正确率 '+Math.round(known/Math.max(total,1)*100)+'%';
  var html = '';
  queue.forEach(function(item) {{
    var r = res[item.id];
    if (!r) return;
    var dot = r==='known'?'🟢':(r==='fuzzy'?'🟡':'🔴');
    var label = r==='known'?'认识':(r==='fuzzy'?'模糊':'不认识');
    html += '<div class="done-row"><span>'+dot+' '+esc(item.word)+'</span><span>'+label+'</span></div>';
  }});
  document.getElementById('dList').innerHTML = html;
}}

function saveProgress() {{
  var st = store();
  var blob = new Blob([JSON.stringify(st, null, 2)], {{type:'application/json'}});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'progress.json';
  a.click();
  document.getElementById('saveHint').style.display = 'block';
}}

function replayWeak() {{
  var weak = queue.filter(function(item){{
    return res[item.id]==='forgot'||res[item.id]==='fuzzy';
  }});
  if (weak.length===0){{ alert('全部认识了！'); return; }}
  queue = weak; cur = 0; res = {{}};
  document.getElementById('done').style.display = 'none';
  document.getElementById('deck').style.display = '';
  document.getElementById('nav').style.display  = '';
  renderDeck();
}}

function replayAll() {{
  queue = ITEMS.slice(); cur = 0; res = {{}};
  document.getElementById('done').style.display = 'none';
  document.getElementById('deck').style.display = '';
  document.getElementById('nav').style.display  = '';
  renderDeck();
}}

function speak(e, btn) {{
  e.stopPropagation();
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var word = btn.closest('.answer').querySelector('.answer-word').childNodes[0].textContent.trim();
  var u = new SpeechSynthesisUtterance(word);
  u.lang = 'en-GB';
  u.rate = 0.85;
  var voices = window.speechSynthesis.getVoices();
  var v = voices.find(function(x){{return x.lang==='en-GB';}})
       || voices.find(function(x){{return x.lang.startsWith('en');}});
  if (v) u.voice = v;
  window.speechSynthesis.speak(u);
}}

function esc(s) {{
  if (!s) return '';
  return String(s)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}}

// 预加载语音
if (window.speechSynthesis) {{
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = function(){{ window.speechSynthesis.getVoices(); }};
}}

buildQueue();
renderDeck();
</script>
</body>
</html>'''

def sync_to_github():
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(["git", "commit", "-m", f"update: review {today}"],
                       cwd=BASE_DIR, capture_output=True, timeout=10)
        result = subprocess.run(["git", "push"], cwd=BASE_DIR,
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("已同步到 GitHub Pages：" + CONFIG.get('github_pages_url', ''))
        else:
            print("GitHub 同步失败，可稍后手动运行 git push")
    except subprocess.TimeoutExpired:
        print("GitHub 同步超时，卡片已在本地生成，可稍后手动运行 git push")
    except Exception as e:
        print(f"同步出错：{e}")

def main():
    words   = parse_words(os.path.join(BASE_DIR, "vocabulary", "words.md"))
    usages  = parse_usage(os.path.join(BASE_DIR, "usage", "usage.md"))
    grammar = parse_grammar(os.path.join(BASE_DIR, "grammar", "grammar.md"))

    all_items = words + usages + grammar
    if not all_items:
        print("学习库为空")
        return

    selected = select_items(all_items)
    html = make_html(selected)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    os.makedirs(os.path.dirname(DOCS_FILE), exist_ok=True)
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"已生成复习卡片：{OUTPUT_FILE}")
    print(f"共 {len(selected)} 个知识点")
    sync_to_github()

if __name__ == "__main__":
    main()

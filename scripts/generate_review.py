#!/usr/bin/env python3
"""
EN Learning Review Card Generator
从学习库读取数据，生成每日复习 HTML 卡片页面
"""

import re
import os
import json
import random
import subprocess
from datetime import datetime

# 动态推断 BASE_DIR：脚本在 scripts/ 下，BASE_DIR 就是上一级
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "daily_review.html")
DOCS_FILE = os.path.join(BASE_DIR, "docs", "index.html")

# 读取配置文件
def load_config():
    config_path = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"github_pages_url": "", "github_repo": ""}

CONFIG = load_config()

def parse_vocabulary(filepath):
    """解析单词库，提取每个单词条目"""
    words = []
    if not os.path.exists(filepath):
        return words
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 按 ### 分割每个单词条目
    entries = re.split(r'\n---\n', content)
    for entry in entries:
        match = re.search(r'### (\w+)', entry)
        if not match:
            continue
        word = match.group(1)
        
        # 提取中文释义
        meaning = ""
        meaning_match = re.search(r'\*\*中文释义\*\*：\s*\n(.*?)(?=\n\n|\*\*)', entry, re.DOTALL)
        if meaning_match:
            meaning = meaning_match.group(1).strip()
        
        # 提取提问次数
        count = 1
        count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if count_match:
            count = int(count_match.group(1))
        
        # 提取关键差异
        diff = ""
        diff_match = re.search(r'\*\*关键差异\*\*\n(.*?)(?=\*\*实际应用场景\*\*)', entry, re.DOTALL)
        if diff_match:
            diff = diff_match.group(1).strip()
        
        # 提取一个例句
        example_en = ""
        example_cn = ""
        ex_match = re.search(r'EN: (.+)', entry)
        if ex_match:
            example_en = ex_match.group(1).strip()
        cx_match = re.search(r'CN: (.+)', entry)
        if cx_match:
            example_cn = cx_match.group(1).strip()
        
        words.append({
            "word": word,
            "meaning": meaning,
            "count": count,
            "diff": diff,
            "example_en": example_en,
            "example_cn": example_cn,
            "type": "vocabulary"
        })
    return words

def parse_usage(filepath):
    """解析用法库"""
    usages = []
    if not os.path.exists(filepath):
        return usages
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    entries = re.split(r'\n---\n', content)
    for entry in entries:
        match = re.search(r'### (.+)', entry)
        if not match:
            continue
        title = match.group(1).strip()
        
        core = ""
        core_match = re.search(r'\*\*核心区别\*\*\s*\n(.*?)(?=\*\*详细说明\*\*|\*\*记忆技巧\*\*)', entry, re.DOTALL)
        if core_match:
            core = core_match.group(1).strip()
        
        count = 1
        count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if count_match:
            count = int(count_match.group(1))
        
        usages.append({
            "word": title,
            "meaning": core,
            "count": count,
            "type": "usage"
        })
    return usages

def parse_grammar(filepath):
    """解析语法库"""
    grammars = []
    if not os.path.exists(filepath):
        return grammars
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    entries = re.split(r'\n---\n', content)
    for entry in entries:
        match = re.search(r'### (.+)', entry)
        if not match:
            continue
        title = match.group(1).strip()
        
        rule = ""
        rule_match = re.search(r'\*\*规则说明\*\*\s*\n(.*?)(?=\*\*结构公式\*\*|\*\*例句\*\*)', entry, re.DOTALL)
        if rule_match:
            rule = rule_match.group(1).strip()
        
        count = 1
        count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
        if count_match:
            count = int(count_match.group(1))
        
        grammars.append({
            "word": title,
            "meaning": rule,
            "count": count,
            "type": "grammar"
        })
    return grammars

def select_review_items(all_items, max_items=10):
    """
    选择今日复习项目
    规则：薄弱项优先（提问次数>=3），然后待巩固（2次），最后新学（1次）
    """
    weak = [i for i in all_items if i["count"] >= 3]
    medium = [i for i in all_items if i["count"] == 2]
    new = [i for i in all_items if i["count"] == 1]
    
    selected = []
    selected.extend(weak)
    selected.extend(medium)
    
    remaining = max_items - len(selected)
    if remaining > 0:
        random.shuffle(new)
        selected.extend(new[:remaining])
    
    return selected[:max_items]

def generate_html(items):
    """生成带自测打分和间隔复习的 HTML 页面"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    import json
    items_json = json.dumps([{
        "id": f"{item['type']}_{item['word'].replace(' ', '_').replace('/', '_')}",
        "word": item["word"],
        "meaning": item["meaning"].replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;"),
        "count": item["count"],
        "type": item["type"],
        "example_en": item.get("example_en", ""),
        "example_cn": item.get("example_cn", ""),
    } for item in items], ensure_ascii=False)

    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日英文复习 - {today}</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh; color: #fff; padding: 16px;
        }}
        .header {{ text-align:center; padding:20px 0; }}
        .header h1 {{ font-size:24px; margin-bottom:6px; }}
        .header .date {{ color:#aaa; font-size:13px; }}
        .stats {{
            display:flex; justify-content:center; gap:10px;
            margin:16px 0; flex-wrap:wrap;
        }}
        .stat-item {{
            background:rgba(255,255,255,0.1); border-radius:10px;
            padding:10px 16px; text-align:center; min-width:70px;
        }}
        .stat-num {{ font-size:22px; font-weight:bold; }}
        .stat-label {{ font-size:11px; color:#aaa; margin-top:3px; }}
        .progress-bar {{
            max-width:500px; margin:0 auto 20px; background:rgba(255,255,255,0.1);
            border-radius:10px; height:8px; overflow:hidden;
        }}
        .progress-fill {{
            height:100%; border-radius:10px; transition:width 0.5s ease;
            background: linear-gradient(90deg, #34c759, #30d158);
        }}
        .progress-text {{
            text-align:center; font-size:12px; color:#aaa; margin-bottom:20px;
        }}
        .card-wrapper {{
            max-width:400px; margin:0 auto; position:relative;
            min-height:350px;
        }}
        .card {{
            width:100%; min-height:300px; perspective:1000px;
            display:none; flex-direction:column;
        }}
        .card.active {{ display:flex; }}
        .card-inner {{
            width:100%; min-height:300px; transition:transform 0.6s;
            transform-style:preserve-3d; position:relative; cursor:pointer;
        }}
        .card-inner.flipped {{ transform:rotateY(180deg); }}
        .card-front, .card-back {{
            position:absolute; width:100%; min-height:300px;
            backface-visibility:hidden; border-radius:16px; padding:24px;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
        }}
        .card-front {{
            background:linear-gradient(145deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
            border:1px solid rgba(255,255,255,0.2);
        }}
        .card-back {{
            background:linear-gradient(145deg, rgba(255,255,255,0.2), rgba(255,255,255,0.08));
            border:1px solid rgba(255,255,255,0.3);
            transform:rotateY(180deg); overflow-y:auto;
            justify-content:flex-start; align-items:flex-start;
        }}
        .card-badge {{
            position:absolute; top:12px; right:12px; font-size:11px;
            padding:3px 8px; border-radius:20px;
        }}
        .card-badge.weak {{ background:rgba(255,59,48,0.3); }}
        .card-badge.medium {{ background:rgba(255,204,0,0.3); }}
        .card-badge.new {{ background:rgba(52,199,89,0.3); }}
        .card-badge.mastered {{ background:rgba(100,100,255,0.3); }}
        .card-type {{ font-size:12px; color:#aaa; margin-bottom:8px; }}
        .card-word {{ font-size:30px; font-weight:bold; margin:10px 0; }}
        .card-hint {{ font-size:12px; color:#888; margin-top:12px; }}
        .card-count {{ font-size:11px; color:#666; margin-top:8px; }}
        .card-word-small {{ font-size:20px; font-weight:bold; margin-bottom:12px; color:#7dd3fc; }}
        .speak-btn {{
            background:none; border:1px solid rgba(255,255,255,0.3); color:#7dd3fc;
            width:36px; height:36px; border-radius:50%; cursor:pointer;
            font-size:18px; display:inline-flex; align-items:center; justify-content:center;
            margin-top:8px; transition:background 0.2s, transform 0.15s;
        }}
        .speak-btn:hover {{ background:rgba(255,255,255,0.1); }}
        .speak-btn:active {{ transform:scale(0.9); }}
        .speak-btn.playing {{ background:rgba(125,211,252,0.2); border-color:#7dd3fc; }}
        .card-meaning {{ font-size:14px; line-height:1.6; color:#ddd; }}
        .example {{ margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.1); width:100%; }}
        .example-en {{ font-size:13px; color:#7dd3fc; font-style:italic; }}
        .example-cn {{ font-size:12px; color:#aaa; margin-top:4px; }}
        .rating-buttons {{
            display:flex; gap:10px; margin-top:20px; width:100%;
            justify-content:center;
        }}
        .rating-btn {{
            padding:12px 20px; border:none; border-radius:10px;
            font-size:14px; font-weight:600; cursor:pointer; flex:1;
            max-width:120px; transition:transform 0.15s, opacity 0.15s;
        }}
        .rating-btn:active {{ transform:scale(0.95); }}
        .rating-btn.forgot {{
            background:linear-gradient(135deg, #ff3b30, #ff6b6b); color:#fff;
        }}
        .rating-btn.fuzzy {{
            background:linear-gradient(135deg, #ff9500, #ffcc00); color:#333;
        }}
        .rating-btn.known {{
            background:linear-gradient(135deg, #34c759, #30d158); color:#fff;
        }}
        .nav {{
            display:flex; justify-content:center; gap:12px; margin-top:20px;
        }}
        .nav button {{
            background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.2);
            color:#fff; padding:10px 20px; border-radius:8px; cursor:pointer;
            font-size:13px; transition:background 0.2s;
        }}
        .nav button:hover {{ background:rgba(255,255,255,0.25); }}
        .nav button:disabled {{ opacity:0.3; cursor:not-allowed; }}
        .summary {{
            display:none; max-width:400px; margin:0 auto; text-align:center;
            background:rgba(255,255,255,0.1); border-radius:16px; padding:30px;
        }}
        .summary h2 {{ font-size:22px; margin-bottom:16px; }}
        .summary-stats {{ display:flex; justify-content:center; gap:20px; margin:20px 0; }}
        .summary-item {{ text-align:center; }}
        .summary-item .num {{ font-size:28px; font-weight:bold; }}
        .summary-item .label {{ font-size:12px; color:#aaa; margin-top:4px; }}
        .history {{ max-width:400px; margin:20px auto; }}
        .history h3 {{ font-size:16px; margin-bottom:10px; color:#aaa; }}
        .history-item {{
            display:flex; justify-content:space-between; align-items:center;
            padding:8px 12px; border-bottom:1px solid rgba(255,255,255,0.05);
            font-size:13px;
        }}
        .history-dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:8px; }}
        .dot-red {{ background:#ff3b30; }}
        .dot-yellow {{ background:#ffcc00; }}
        .dot-green {{ background:#34c759; }}
        .footer {{ text-align:center; margin-top:40px; color:#666; font-size:12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Daily English Review</h1>
        <div class="date">{today}</div>
    </div>
    <div class="stats">
        <div class="stat-item">
            <div class="stat-num" id="stat-total">0</div>
            <div class="stat-label">总数</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" id="stat-done" style="color:#34c759">0</div>
            <div class="stat-label">已完成</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" id="stat-known" style="color:#34c759">0</div>
            <div class="stat-label">认识</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" id="stat-fuzzy" style="color:#ffcc00">0</div>
            <div class="stat-label">模糊</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" id="stat-forgot" style="color:#ff3b30">0</div>
            <div class="stat-label">不认识</div>
        </div>
    </div>
    <div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>
    <div class="progress-text" id="progress-text">点击卡片翻转，然后评估你的掌握程度</div>

    <div class="card-wrapper" id="card-wrapper"></div>

    <div class="summary" id="summary">
        <h2>今日复习完成！</h2>
        <div class="summary-stats">
            <div class="summary-item">
                <div class="num" id="sum-known" style="color:#34c759">0</div>
                <div class="label">认识</div>
            </div>
            <div class="summary-item">
                <div class="num" id="sum-fuzzy" style="color:#ffcc00">0</div>
                <div class="label">模糊</div>
            </div>
            <div class="summary-item">
                <div class="num" id="sum-forgot" style="color:#ff3b30">0</div>
                <div class="label">不认识</div>
            </div>
        </div>
        <div class="progress-text" id="sum-rate"></div>
        <div class="nav" style="margin-top:20px">
            <button onclick="restartWeak()">重新复习「不认识+模糊」</button>
            <button onclick="restartAll()">全部重新复习</button>
        </div>
        <div class="history" id="history">
            <h3>本次详情</h3>
        </div>
    </div>

    <div class="nav" id="nav-buttons">
        <button id="btn-prev" onclick="prevCard()" disabled>&larr; 上一个</button>
        <button id="btn-skip" onclick="skipCard()">跳过 &rarr;</button>
    </div>

    <div class="history" id="past-sessions" style="display:none">
        <h3>历史复习记录</h3>
        <div id="past-list"></div>
    </div>

    <div class="footer">
        EN Learning Knowledge Base | {today}<br>
        <span style="cursor:pointer;text-decoration:underline" onclick="document.getElementById('past-sessions').style.display=document.getElementById('past-sessions').style.display==='none'?'block':'none'">查看历史记录</span>
        &nbsp;|&nbsp;
        <span style="cursor:pointer;text-decoration:underline" onclick="clearHistory()">清除本地数据</span>
    </div>

    <script>
    const ALL_ITEMS = {items_json};
    const STORAGE_KEY = 'en_review_data';
    const SESSION_KEY = 'en_review_sessions';

    let currentIndex = 0;
    let results = {{}};
    let reviewQueue = [];

    // ========== 本地存储 ==========
    function getReviewData() {{
        try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{}}; }}
        catch(e) {{ return {{}}; }}
    }}
    function saveReviewData(data) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }}
            }} catch(e) {{}}
        }}
        const dot = document.getElementById('sync-dot');
        const txt = document.getElementById('sync-txt');
        if (dot && txt) {{
            dot.style.color = serverAvailable ? '#34c759' : '#888';
            txt.textContent = serverAvailable
                ? `已连接同步服务器 (${{SYNC_SERVER}})`
                : '离线模式（仅本地）';
        }}
    }}

    async function loadFromServer() {{
        if (!serverAvailable) return null;
        try {{
            const r = await fetch(SYNC_SERVER + '/progress', {{signal: AbortSignal.timeout(2000)}});
            if (r.ok) return await r.json();
        }} catch(e) {{}}
        return null;
    }}

    async function saveToServer(data) {{
        if (!serverAvailable) return;
        try {{
            await fetch(SYNC_SERVER + '/progress', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data),
                signal: AbortSignal.timeout(3000)
            }});
        }} catch(e) {{}}
    }}

    // ========== 间隔复习算法 ==========
    function getReviewData() {{
        try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{}}; }}
        catch(e) {{ return {{}}; }}
    }}
    function saveReviewData(data) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        // 同时异步推送到服务器
        saveToServer(data);
    }}

    function shouldReviewToday(itemData) {{
        if (!itemData || !itemData.lastReview) return true;
        const now = new Date();
        const last = new Date(itemData.lastReview);
        const daysSince = Math.floor((now - last) / 86400000);
        // 间隔复习间距：不认识=1天, 模糊=2天, 认识=按次数递增(1,2,4,7,14,30)
        const intervals = [1, 2, 4, 7, 14, 30, 60];
        if (itemData.lastRating === 'forgot') return daysSince >= 1;
        if (itemData.lastRating === 'fuzzy') return daysSince >= 2;
        // known: 根据连续答对次数决定间隔
        const streak = itemData.streak || 0;
        const interval = intervals[Math.min(streak, intervals.length - 1)];
        return daysSince >= interval;
    }}

    function buildReviewQueue() {{
        const data = getReviewData();
        let needReview = [];
        let noRecord = [];

        ALL_ITEMS.forEach(item => {{
            const d = data[item.id];
            if (!d) {{
                noRecord.push(item);
            }} else if (shouldReviewToday(d)) {{
                item._priority = d.lastRating === 'forgot' ? 0 : (d.lastRating === 'fuzzy' ? 1 : 2);
                needReview.push(item);
            }}
        }});

        // 排序：不认识 > 模糊 > 认识
        needReview.sort((a, b) => (a._priority || 0) - (b._priority || 0));
        // 没有记录的放后面
        reviewQueue = [...needReview, ...noRecord];
        
        if (reviewQueue.length === 0) {{
            reviewQueue = [...ALL_ITEMS]; // 全部已掌握就全部复习
        }}
    }}

    // ========== 卡片渲染 ==========
    function renderCards() {{
        const wrapper = document.getElementById('card-wrapper');
        wrapper.innerHTML = '';
        const data = getReviewData();

        reviewQueue.forEach((item, i) => {{
            const d = data[item.id];
            let level, levelText, levelEmoji;
            if (d && d.lastRating === 'forgot') {{
                level='weak'; levelText='不认识'; levelEmoji='🔴';
            }} else if (d && d.lastRating === 'fuzzy') {{
                level='medium'; levelText='模糊'; levelEmoji='🟡';
            }} else if (d && d.streak >= 3) {{
                level='mastered'; levelText='已掌握'; levelEmoji='🔵';
            }} else {{
                level='new'; levelText='待复习'; levelEmoji='🟢';
            }}
            const typeText = {{'vocabulary':'单词','usage':'用法','grammar':'语法'}}[item.type]||'其他';
            const exHtml = item.example_en ? `
                <div class="example">
                    <div class="example-en">${{item.example_en}}</div>
                    <div class="example-cn">${{item.example_cn}}</div>
                </div>` : '';
            const streakInfo = d ? `连续认识 ${{d.streak||0}} 次` : '首次复习';

            const card = document.createElement('div');
            card.className = 'card' + (i === 0 ? ' active' : '');
            card.dataset.index = i;
            card.innerHTML = `
                <div class="card-inner" onclick="this.classList.toggle('flipped')">
                    <div class="card-front">
                        <div class="card-badge ${{level}}">${{levelEmoji}} ${{levelText}}</div>
                        <div class="card-type">${{typeText}} | ${{i+1}}/${{reviewQueue.length}}</div>
                        <div class="card-word">${{item.word}}</div>
                        <button class="speak-btn" onclick="speak('${{item.word}}', this, event)" title="英式发音">&#128264;</button>
                        <div class="card-hint">点击卡片查看答案</div>
                        <div class="card-count">${{streakInfo}}</div>
                    </div>
                    <div class="card-back">
                        <div class="card-badge ${{level}}">${{levelEmoji}} ${{levelText}}</div>
                        <div class="card-word-small">${{item.word}} <button class="speak-btn" onclick="speak('${{item.word}}', this, event)" title="英式发音" style="width:28px;height:28px;font-size:14px;vertical-align:middle">&#128264;</button></div>
                        <div class="card-meaning">${{item.meaning}}</div>
                        ${{exHtml}}
                    </div>
                </div>
                <div class="rating-buttons">
                    <button class="rating-btn forgot" onclick="rate('${{item.id}}', 'forgot', event)">不认识</button>
                    <button class="rating-btn fuzzy" onclick="rate('${{item.id}}', 'fuzzy', event)">模糊</button>
                    <button class="rating-btn known" onclick="rate('${{item.id}}', 'known', event)">认识</button>
                </div>`;
            wrapper.appendChild(card);
        }});
        updateStats();
    }}

    // ========== 打分逻辑 ==========
    function rate(id, rating, event) {{
        event.stopPropagation();
        results[id] = rating;

        // 更新 localStorage 中的间隔复习数据
        const data = getReviewData();
        if (!data[id]) data[id] = {{ streak: 0, totalReviews: 0, history: [] }};
        data[id].lastReview = new Date().toISOString();
        data[id].lastRating = rating;
        data[id].totalReviews = (data[id].totalReviews || 0) + 1;
        if (rating === 'known') {{
            data[id].streak = (data[id].streak || 0) + 1;
        }} else {{
            data[id].streak = 0;
        }}
        // 保存最近5次记录
        if (!data[id].history) data[id].history = [];
        data[id].history.push({{ date: new Date().toISOString().slice(0,10), rating }});
        if (data[id].history.length > 10) data[id].history = data[id].history.slice(-10);
        saveReviewData(data);

        updateStats();
        // 自动跳转下一张
        setTimeout(() => nextCard(), 400);
    }}

    // ========== 导航 ==========
    function nextCard() {{
        const cards = document.querySelectorAll('.card');
        if (currentIndex < cards.length - 1) {{
            cards[currentIndex].classList.remove('active');
            currentIndex++;
            cards[currentIndex].classList.add('active');
            // 重置翻转状态
            cards[currentIndex].querySelector('.card-inner').classList.remove('flipped');
            updateNav();
            updateStats();
        }} else {{
            showSummary();
        }}
    }}
    function prevCard() {{
        const cards = document.querySelectorAll('.card');
        if (currentIndex > 0) {{
            cards[currentIndex].classList.remove('active');
            currentIndex--;
            cards[currentIndex].classList.add('active');
            updateNav();
        }}
    }}
    function skipCard() {{ nextCard(); }}

    function updateNav() {{
        document.getElementById('btn-prev').disabled = currentIndex === 0;
    }}

    // ========== 统计更新 ==========
    function updateStats() {{
        const total = reviewQueue.length;
        const done = Object.keys(results).length;
        const known = Object.values(results).filter(r=>r==='known').length;
        const fuzzy = Object.values(results).filter(r=>r==='fuzzy').length;
        const forgot = Object.values(results).filter(r=>r==='forgot').length;

        document.getElementById('stat-total').textContent = total;
        document.getElementById('stat-done').textContent = done;
        document.getElementById('stat-known').textContent = known;
        document.getElementById('stat-fuzzy').textContent = fuzzy;
        document.getElementById('stat-forgot').textContent = forgot;

        const pct = total > 0 ? Math.round(done / total * 100) : 0;
        document.getElementById('progress-fill').style.width = pct + '%';
        document.getElementById('progress-text').textContent =
            done === 0 ? '点击卡片翻转，然后评估你的掌握程度'
            : `已完成 ${{done}}/${{total}}（正确率 ${{total > 0 ? Math.round(known/Math.max(done,1)*100) : 0}}%）`;
    }}

    // ========== 完成总结 ==========
    function showSummary() {{
        document.getElementById('card-wrapper').style.display = 'none';
        document.getElementById('nav-buttons').style.display = 'none';
        const summary = document.getElementById('summary');
        summary.style.display = 'block';

        const known = Object.values(results).filter(r=>r==='known').length;
        const fuzzy = Object.values(results).filter(r=>r==='fuzzy').length;
        const forgot = Object.values(results).filter(r=>r==='forgot').length;
        const total = known + fuzzy + forgot;

        document.getElementById('sum-known').textContent = known;
        document.getElementById('sum-fuzzy').textContent = fuzzy;
        document.getElementById('sum-forgot').textContent = forgot;
        document.getElementById('sum-rate').textContent =
            `正确率 ${{Math.round(known/Math.max(total,1)*100)}}% | 模糊的词会在2天后再次出现，不认识的词明天就会再次出现`;

        // 详情列表
        const history = document.getElementById('history');
        let listHtml = '';
        reviewQueue.forEach(item => {{
            const r = results[item.id];
            if (!r) return;
            const dotClass = r==='known'?'dot-green':(r==='fuzzy'?'dot-yellow':'dot-red');
            const ratingText = r==='known'?'认识':(r==='fuzzy'?'模糊':'不认识');
            listHtml += `<div class="history-item">
                <span><span class="history-dot ${{dotClass}}"></span>${{item.word}}</span>
                <span>${{ratingText}}</span>
            </div>`;
        }});
        history.innerHTML = '<h3>本次详情</h3>' + listHtml;

        // 保存本次 session
        saveSession(known, fuzzy, forgot);
    }}

    function saveSession(known, fuzzy, forgot) {{
        try {{
            const sessions = JSON.parse(localStorage.getItem(SESSION_KEY)) || [];
            sessions.push({{
                date: new Date().toISOString(),
                total: known + fuzzy + forgot,
                known, fuzzy, forgot,
                rate: Math.round(known / Math.max(known+fuzzy+forgot, 1) * 100)
            }});
            if (sessions.length > 30) sessions.splice(0, sessions.length - 30);
            localStorage.setItem(SESSION_KEY, JSON.stringify(sessions));
            renderPastSessions();
        }} catch(e) {{}}
    }}

    function renderPastSessions() {{
        try {{
            const sessions = JSON.parse(localStorage.getItem(SESSION_KEY)) || [];
            const list = document.getElementById('past-list');
            if (sessions.length === 0) {{ list.innerHTML = '<div style="color:#666;font-size:12px">暂无记录</div>'; return; }}
            list.innerHTML = sessions.slice().reverse().map(s => `
                <div class="history-item">
                    <span>${{new Date(s.date).toLocaleString('zh-CN',{{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}})}}</span>
                    <span style="color:#34c759">${{s.known}}</span> /
                    <span style="color:#ffcc00">${{s.fuzzy}}</span> /
                    <span style="color:#ff3b30">${{s.forgot}}</span>
                    <span style="color:#aaa">${{s.rate}}%</span>
                </div>
            `).join('');
        }} catch(e) {{}}
    }}

    // ========== 重新复习 ==========
    function restartWeak() {{
        const weakItems = reviewQueue.filter(item => {{
            const r = results[item.id];
            return r === 'forgot' || r === 'fuzzy';
        }});
        if (weakItems.length === 0) {{ alert('没有需要重新复习的词！全部认识了！'); return; }}
        reviewQueue = weakItems;
        currentIndex = 0;
        results = {{}};
        document.getElementById('summary').style.display = 'none';
        document.getElementById('card-wrapper').style.display = '';
        document.getElementById('nav-buttons').style.display = '';
        renderCards();
    }}

    function restartAll() {{
        reviewQueue = [...ALL_ITEMS];
        currentIndex = 0;
        results = {{}};
        document.getElementById('summary').style.display = 'none';
        document.getElementById('card-wrapper').style.display = '';
        document.getElementById('nav-buttons').style.display = '';
        renderCards();
    }}

    function clearHistory() {{
        if (confirm('确定要清除所有本地学习数据吗？这将重置所有间隔复习进度。')) {{
            localStorage.removeItem(STORAGE_KEY);
            localStorage.removeItem(SESSION_KEY);
            location.reload();
        }}
    }}

    // ========== 英式发音 ==========
    function speak(word, btn, event) {{
        event.stopPropagation(); // 阻止卡片翻转
        if (!window.speechSynthesis) {{ alert('你的浏览器不支持语音功能'); return; }}
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-GB'; // 英式发音
        utterance.rate = 0.85;    // 稍慢一点，听得更清楚
        utterance.pitch = 1;
        // 尝试选择英式语音
        const voices = window.speechSynthesis.getVoices();
        const britishVoice = voices.find(v => v.lang === 'en-GB')
            || voices.find(v => v.lang.startsWith('en-GB'))
            || voices.find(v => v.lang.startsWith('en'));
        if (britishVoice) utterance.voice = britishVoice;
        // 按钮动画
        btn.classList.add('playing');
        utterance.onend = () => btn.classList.remove('playing');
        utterance.onerror = () => btn.classList.remove('playing');
        window.speechSynthesis.speak(utterance);
    }}
    // 预加载语音列表（某些浏览器需要异步加载）
    if (window.speechSynthesis) {{
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }}

    // ========== 初始化 ==========
    buildReviewQueue();
    renderCards();
    renderPastSessions();
    </script>
</body>
</html>'''
    return html

def sync_to_github():
    """将更新同步到 GitHub Pages（带超时，不阻塞主流程）"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR,
                       capture_output=True, timeout=10)
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ["git", "commit", "-m", f"update: daily review {today}"],
            cwd=BASE_DIR, capture_output=True, timeout=10
        )
        result = subprocess.run(
            ["git", "push"],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"已同步到 GitHub Pages：{CONFIG.get('github_pages_url', '')}")
        else:
            print(f"GitHub 同步失败（可手动运行 git push）：{result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("GitHub 同步超时（网络较慢），卡片已在本地生成，可稍后手动运行 git push")
    except Exception as e:
        print(f"GitHub 同步出错：{e}")

def main():
    vocab = parse_vocabulary(os.path.join(BASE_DIR, "vocabulary", "words.md"))
    usage = parse_usage(os.path.join(BASE_DIR, "usage", "usage.md"))
    grammar = parse_grammar(os.path.join(BASE_DIR, "grammar", "grammar.md"))
    
    all_items = vocab + usage + grammar
    
    if not all_items:
        print("学习库中还没有任何记录，无法生成复习卡片。")
        return
    
    selected = select_review_items(all_items)
    html = generate_html(selected)
    
    # 写入本地文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    # 同时写入 docs/ 目录供 GitHub Pages 使用
    os.makedirs(os.path.dirname(DOCS_FILE), exist_ok=True)
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"已生成每日复习卡片：{OUTPUT_FILE}")
    print(f"共 {len(selected)} 个知识点（薄弱项 {len([i for i in selected if i['count']>=3])} | 待巩固 {len([i for i in selected if i['count']==2])} | 新学 {len([i for i in selected if i['count']==1])}）")
    
    # 自动同步到 GitHub Pages
    sync_to_github()

if __name__ == "__main__":
    main()

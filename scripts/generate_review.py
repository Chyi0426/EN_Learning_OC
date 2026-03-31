#!/usr/bin/env python3
"""
EN Learning Review Card Generator
从学习库读取数据，生成每日复习 HTML 卡片页面
"""

import re
import os
import random
from datetime import datetime

BASE_DIR = "/Users/raymond.zhong/Desktop/EN_Learning_OC"
OUTPUT_FILE = os.path.join(BASE_DIR, "daily_review.html")

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
    """生成复习卡片 HTML 页面"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    cards_html = ""
    for i, item in enumerate(items):
        level = "weak" if item["count"] >= 3 else ("medium" if item["count"] == 2 else "new")
        level_text = "薄弱项" if level == "weak" else ("待巩固" if level == "medium" else "新学")
        level_emoji = "🔴" if level == "weak" else ("🟡" if level == "medium" else "🟢")
        type_text = {"vocabulary": "单词", "usage": "用法", "grammar": "语法"}.get(item["type"], "其他")
        
        meaning_escaped = item["meaning"].replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
        
        example_html = ""
        if item.get("example_en"):
            example_html = f'''
            <div class="example">
                <div class="example-en">{item["example_en"]}</div>
                <div class="example-cn">{item.get("example_cn", "")}</div>
            </div>'''
        
        cards_html += f'''
        <div class="card" id="card-{i}" data-index="{i}">
            <div class="card-inner" onclick="this.classList.toggle('flipped')">
                <div class="card-front">
                    <div class="card-badge {level}">{level_emoji} {level_text}</div>
                    <div class="card-type">{type_text}</div>
                    <div class="card-word">{item["word"]}</div>
                    <div class="card-hint">点击卡片查看答案</div>
                    <div class="card-count">已提问 {item["count"]} 次</div>
                </div>
                <div class="card-back">
                    <div class="card-badge {level}">{level_emoji} {level_text}</div>
                    <div class="card-word-small">{item["word"]}</div>
                    <div class="card-meaning">{meaning_escaped}</div>
                    {example_html}
                </div>
            </div>
        </div>'''
    
    weak_count = len([i for i in items if i["count"] >= 3])
    medium_count = len([i for i in items if i["count"] == 2])
    new_count = len([i for i in items if i["count"] == 1])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日英文复习 - {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        .header .date {{
            color: #aaa;
            font-size: 14px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0 30px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 12px 20px;
            text-align: center;
            min-width: 100px;
        }}
        .stat-num {{ font-size: 24px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; color: #aaa; margin-top: 4px; }}
        .cards-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            width: 320px;
            height: 280px;
            perspective: 1000px;
            cursor: pointer;
        }}
        .card-inner {{
            width: 100%;
            height: 100%;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            position: relative;
        }}
        .card-inner.flipped {{
            transform: rotateY(180deg);
        }}
        .card-front, .card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 16px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .card-front {{
            background: linear-gradient(145deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }}
        .card-back {{
            background: linear-gradient(145deg, rgba(255,255,255,0.2), rgba(255,255,255,0.08));
            border: 1px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
            transform: rotateY(180deg);
            overflow-y: auto;
            justify-content: flex-start;
            align-items: flex-start;
        }}
        .card-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 20px;
        }}
        .card-badge.weak {{ background: rgba(255,59,48,0.3); }}
        .card-badge.medium {{ background: rgba(255,204,0,0.3); }}
        .card-badge.new {{ background: rgba(52,199,89,0.3); }}
        .card-type {{
            font-size: 12px;
            color: #aaa;
            margin-bottom: 8px;
        }}
        .card-word {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .card-word-small {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 12px;
            color: #7dd3fc;
        }}
        .card-hint {{
            font-size: 12px;
            color: #888;
            margin-top: 12px;
        }}
        .card-count {{
            font-size: 11px;
            color: #666;
            margin-top: 8px;
        }}
        .card-meaning {{
            font-size: 14px;
            line-height: 1.6;
            color: #ddd;
        }}
        .example {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.1);
            width: 100%;
        }}
        .example-en {{
            font-size: 13px;
            color: #7dd3fc;
            font-style: italic;
        }}
        .example-cn {{
            font-size: 12px;
            color: #aaa;
            margin-top: 4px;
        }}
        .nav {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 30px;
        }}
        .nav button {{
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 10px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }}
        .nav button:hover {{
            background: rgba(255,255,255,0.25);
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Daily English Review</h1>
        <div class="date">{today} | 点击卡片翻转查看答案</div>
    </div>
    <div class="stats">
        <div class="stat-item">
            <div class="stat-num">{len(items)}</div>
            <div class="stat-label">今日复习</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" style="color:#ff3b30">{weak_count}</div>
            <div class="stat-label">薄弱项</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" style="color:#ffcc00">{medium_count}</div>
            <div class="stat-label">待巩固</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" style="color:#34c759">{new_count}</div>
            <div class="stat-label">新学</div>
        </div>
    </div>
    <div class="cards-container">
        {cards_html}
    </div>
    <div class="nav">
        <button onclick="flipAll(false)">全部翻回正面</button>
        <button onclick="flipAll(true)">全部显示答案</button>
        <button onclick="shuffleCards()">随机排列</button>
    </div>
    <div class="footer">
        EN Learning Knowledge Base | Generated at {datetime.now().strftime("%H:%M:%S")}
    </div>
    <script>
        function flipAll(show) {{
            document.querySelectorAll('.card-inner').forEach(el => {{
                if (show) el.classList.add('flipped');
                else el.classList.remove('flipped');
            }});
        }}
        function shuffleCards() {{
            const container = document.querySelector('.cards-container');
            const cards = Array.from(container.children);
            for (let i = cards.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                container.appendChild(cards[j]);
                cards.splice(j, 1, cards[i]);
            }}
        }}
    </script>
</body>
</html>'''
    return html

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
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"已生成每日复习卡片：{OUTPUT_FILE}")
    print(f"共 {len(selected)} 个知识点（薄弱项 {len([i for i in selected if i['count']>=3])} | 待巩固 {len([i for i in selected if i['count']==2])} | 新学 {len([i for i in selected if i['count']==1])}）")

if __name__ == "__main__":
    main()

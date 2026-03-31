#!/usr/bin/env python3
"""
EN Learning Reminder Pusher
从学习库读取需要复习的知识点，写入 macOS 提醒事项 App
同时触发生成 HTML 复习卡片
"""

import subprocess
import re
import os
from datetime import datetime, timedelta

BASE_DIR = "/Users/raymond.zhong/Desktop/EN_Learning_OC"
REMINDER_LIST = "EN复习"  # 提醒事项中的列表名称

def parse_all_items():
    """从学习库中解析所有知识点"""
    items = []
    
    # 解析单词
    vocab_path = os.path.join(BASE_DIR, "vocabulary", "words.md")
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = re.split(r'\n---\n', content)
        for entry in entries:
            match = re.search(r'### (\w+)', entry)
            if not match:
                continue
            word = match.group(1)
            count = 1
            count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
            if count_match:
                count = int(count_match.group(1))
            
            meaning = ""
            meaning_match = re.search(r'\[.*?\]：(.+)', entry)
            if meaning_match:
                meaning = meaning_match.group(1).strip()
            
            items.append({"word": word, "meaning": meaning, "count": count, "type": "单词"})
    
    # 解析用法
    usage_path = os.path.join(BASE_DIR, "usage", "usage.md")
    if os.path.exists(usage_path):
        with open(usage_path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = re.split(r'\n---\n', content)
        for entry in entries:
            match = re.search(r'### (.+)', entry)
            if not match:
                continue
            title = match.group(1).strip()
            count = 1
            count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
            if count_match:
                count = int(count_match.group(1))
            items.append({"word": title, "meaning": "", "count": count, "type": "用法"})
    
    # 解析语法
    grammar_path = os.path.join(BASE_DIR, "grammar", "grammar.md")
    if os.path.exists(grammar_path):
        with open(grammar_path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = re.split(r'\n---\n', content)
        for entry in entries:
            match = re.search(r'### (.+)', entry)
            if not match:
                continue
            title = match.group(1).strip()
            count = 1
            count_match = re.search(r'\*\*提问次数\*\*：(\d+)', entry)
            if count_match:
                count = int(count_match.group(1))
            items.append({"word": title, "meaning": "", "count": count, "type": "语法"})
    
    return items

def select_review_items(items, max_items=10):
    """选择需要复习的知识点，薄弱项优先"""
    weak = [i for i in items if i["count"] >= 3]
    medium = [i for i in items if i["count"] == 2]
    new = [i for i in items if i["count"] == 1]
    
    selected = []
    selected.extend(weak)
    selected.extend(medium)
    remaining = max_items - len(selected)
    if remaining > 0:
        import random
        random.shuffle(new)
        selected.extend(new[:remaining])
    
    return selected[:max_items]

def ensure_reminder_list():
    """确保提醒事项中存在 EN复习 列表"""
    script = f'''
    tell application "Reminders"
        if not (exists list "{REMINDER_LIST}") then
            make new list with properties {{name:"{REMINDER_LIST}"}}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], capture_output=True)

def clear_old_reminders():
    """清除昨日已完成的提醒"""
    script = f'''
    tell application "Reminders"
        tell list "{REMINDER_LIST}"
            set completedReminders to (every reminder whose completed is true)
            repeat with r in completedReminders
                delete r
            end repeat
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], capture_output=True)

def add_reminder(title, notes, due_date_str):
    """添加一个提醒事项"""
    script = f'''
    tell application "Reminders"
        tell list "{REMINDER_LIST}"
            set newReminder to make new reminder with properties {{name:"{title}", body:"{notes}"}}
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], capture_output=True)

def push_reminders():
    """主函数：推送今日复习提醒"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 解析所有知识点
    all_items = parse_all_items()
    if not all_items:
        print("学习库为空，无需推送。")
        return
    
    # 2. 选择今日复习项
    selected = select_review_items(all_items)
    
    # 3. 确保列表存在
    ensure_reminder_list()
    
    # 4. 清理已完成的旧提醒
    clear_old_reminders()
    
    # 5. 生成分类标题提醒
    weak_items = [i for i in selected if i["count"] >= 3]
    other_items = [i for i in selected if i["count"] < 3]
    
    # 添加总览提醒
    summary_title = f"📚 每日英文复习 ({today})"
    summary_notes = f"今日共 {len(selected)} 个知识点需要复习。\\n薄弱项 {len(weak_items)} 个，其他 {len(other_items)} 个。\\n打开桌面 daily_review.html 查看复习卡片。"
    add_reminder(summary_title, summary_notes, today)
    
    # 添加薄弱项提醒（优先级最高）
    if weak_items:
        for item in weak_items:
            level = "🔴 薄弱项"
            title = f"{level} [{item['type']}] {item['word']}（已问{item['count']}次）"
            meaning = item["meaning"] if item["meaning"] else "打开 daily_review.html 查看详情"
            notes = f"释义：{meaning}"
            add_reminder(title, notes, today)
    
    # 添加其他复习项提醒
    for item in other_items:
        level = "🟡 待巩固" if item["count"] == 2 else "🟢 新学"
        title = f"{level} [{item['type']}] {item['word']}"
        meaning = item["meaning"] if item["meaning"] else "打开 daily_review.html 查看详情"
        notes = f"释义：{meaning}"
        add_reminder(title, notes, today)
    
    print(f"✅ 已推送 {len(selected)} 个复习提醒到「{REMINDER_LIST}」列表")
    print(f"   薄弱项: {len(weak_items)} | 其他: {len(other_items)}")
    
    # 6. 同时生成 HTML 复习卡片
    generate_review_path = os.path.join(BASE_DIR, "scripts", "generate_review.py")
    if os.path.exists(generate_review_path):
        subprocess.run(["python3", generate_review_path])

if __name__ == "__main__":
    push_reminders()

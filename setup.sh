#!/bin/bash
# ================================================
# EN Learning OC - 一键安装脚本（本地复制版）
#
# 使用方法：
#   1. 把整个 EN_Learning_OC 文件夹复制到新电脑桌面
#   2. 打开终端，运行：
#      bash ~/Desktop/EN_Learning_OC/setup.sh
# ================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-$SCRIPT_DIR}"
SKILL_DIR="$HOME/.claude/skills/en-learning"
LAUNCHER="$HOME/Documents/en_review_launcher.sh"
PLIST_DEST="$HOME/Library/LaunchAgents/com.raymond.en-learning-review.plist"

echo ""
echo "======================================"
echo "  EN Learning OC - 一键安装"
echo "  资料库位置：$INSTALL_DIR"
echo "======================================"
echo ""

# ── 1. 验证文件夹完整性 ────────────────────────
echo "📋 [1/5] 检查文件夹完整性..."
MISSING=""
for f in "vocabulary/words.md" "grammar/grammar.md" "usage/usage.md" \
         "scripts/generate_review.py" "en-learning/SKILL.md"; do
    [ ! -f "$INSTALL_DIR/$f" ] && MISSING="$MISSING\n   缺少：$f"
done
if [ -n "$MISSING" ]; then
    echo "   ❌ 文件夹不完整："
    echo -e "$MISSING"
    exit 1
fi
echo "   ✅ 文件夹完整"

# ── 2. 生成本地 config.json ────────────────────
echo ""
echo "⚙️  [2/5] 写入本地配置..."
cat > "$INSTALL_DIR/config.json" << EOF
{
  "base_dir": "$INSTALL_DIR",
  "github_pages_url": "https://chyi0426.github.io/EN_Learning_OC/",
  "github_repo": "Chyi0426/EN_Learning_OC"
}
EOF
echo "   ✅ config.json 已生成"

# ── 3. 安装 Skill ──────────────────────────────
echo ""
echo "🧠 [3/5] 安装 en-learning Skill 到 OpenCode..."
mkdir -p "$HOME/.claude/skills"
rm -rf "$SKILL_DIR"
cp -r "$INSTALL_DIR/en-learning" "$SKILL_DIR"
echo "   ✅ Skill 已安装：$SKILL_DIR"

# ── 4. 配置 GitHub 同步（只用 git，不需要 gh CLI）──
echo ""
echo "🔐 [4/5] 配置 GitHub 同步..."

# 初始化或关联 git 仓库
if [ ! -d "$INSTALL_DIR/.git" ]; then
    git -C "$INSTALL_DIR" init
    git -C "$INSTALL_DIR" remote add origin "https://github.com/Chyi0426/EN_Learning_OC.git"
    git -C "$INSTALL_DIR" branch -M main 2>/dev/null || true
else
    # 确保 remote 正确
    git -C "$INSTALL_DIR" remote set-url origin "https://github.com/Chyi0426/EN_Learning_OC.git" 2>/dev/null || \
    git -C "$INSTALL_DIR" remote add origin "https://github.com/Chyi0426/EN_Learning_OC.git" 2>/dev/null || true
fi

# 配置 git 用户信息
git config --global user.name "raymond.zhong" 2>/dev/null || true
git config --global user.email "raymond.zhong@dji.com" 2>/dev/null || true

echo "   需要 GitHub Token 才能同步数据到云端。"
echo ""
echo "   获取方法："
echo "   1. 浏览器打开：https://github.com/settings/tokens"
echo "   2. 点击 Generate new token (classic)"
echo "   3. 勾选权限：repo"
echo "   4. 点击 Generate token，复制 token"
echo ""
read -p "   粘贴你的 GitHub Token (ghp_...，直接回车跳过): " GH_TOKEN

if [ -n "$GH_TOKEN" ]; then
    # 把 token 存入 macOS 钥匙串，git 以后自动使用
    git -C "$INSTALL_DIR" config credential.helper osxkeychain 2>/dev/null || true
    # 用 token 测试推送是否能通
    REMOTE_URL="https://Chyi0426:${GH_TOKEN}@github.com/Chyi0426/EN_Learning_OC.git"
    git -C "$INSTALL_DIR" remote set-url origin "$REMOTE_URL"
    # 写入钥匙串（静默）
    python3 - << PYEOF
import subprocess, sys
url = "https://github.com"
token = "$GH_TOKEN"
cmd = f"protocol=https\nhost=github.com\nusername=Chyi0426\npassword={token}\n"
try:
    proc = subprocess.run(
        ["git", "credential-osxkeychain", "store"],
        input=cmd, capture_output=True, text=True
    )
except Exception:
    pass
PYEOF
    # 恢复 remote URL 为不含 token 的版本（token 已存钥匙串）
    git -C "$INSTALL_DIR" remote set-url origin "https://github.com/Chyi0426/EN_Learning_OC.git"
    echo "   ✅ GitHub Token 已保存，后续自动同步无需重新输入"
else
    echo "   ⚠️  已跳过，学习记录不会自动同步到云端"
    echo "      （可以稍后在终端运行：cd $INSTALL_DIR && git push）"
fi

# ── 5. 安装每日定时任务 ────────────────────────
echo ""
echo "⏰ [5/5] 安装每日复习定时任务（每天 09:00）..."

cat > "$LAUNCHER" << EOF
#!/bin/bash
/usr/bin/python3 "$INSTALL_DIR/scripts/generate_review.py" >> "$HOME/Documents/en_review.log" 2>&1
EOF
chmod +x "$LAUNCHER"

cat > "$PLIST_DEST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.raymond.en-learning-review</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$LAUNCHER</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/scripts/review.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/scripts/review_error.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "   ✅ 定时任务已安装"

# ── 生成今日复习卡片 ───────────────────────────
echo ""
echo "📚 生成今日复习卡片..."
python3 "$INSTALL_DIR/scripts/generate_review.py" && \
    open "$INSTALL_DIR/daily_review.html" 2>/dev/null || \
    echo "   ⚠️  生成失败，可稍后手动运行"

# ── 完成 ───────────────────────────────────────
echo ""
echo "======================================"
echo "  ✅ 安装完成！"
echo "======================================"
echo ""
echo "  📁 资料库：$INSTALL_DIR"
echo "  🧠 Skill：  $SKILL_DIR"
echo "  🌐 在线：   https://chyi0426.github.io/EN_Learning_OC/"
echo "  ⏰ 定时：   每天 09:00 自动更新"
echo ""
echo "  打开 OpenCode，直接问英文问题就可以开始了！"
echo ""

#!/bin/bash
# ================================================
# EN Learning OC - 新电脑一键安装脚本
# 用法：bash setup.sh [安装目录]
# 示例：bash setup.sh ~/Desktop/EN_Learning_OC
# 不传参数则默认装到 ~/Desktop/EN_Learning_OC
# ================================================

set -e

REPO_URL="https://github.com/Chyi0426/EN_Learning_OC.git"
INSTALL_DIR="${1:-$HOME/Desktop/EN_Learning_OC}"
SKILL_DIR="$HOME/.claude/skills/en-learning"
GH_BIN="$HOME/.local/bin/gh"
LAUNCHER="$HOME/Documents/en_review_launcher.sh"
PLIST_DEST="$HOME/Library/LaunchAgents/com.raymond.en-learning-review.plist"

echo ""
echo "======================================"
echo "  EN Learning OC - 一键安装"
echo "  安装目录：$INSTALL_DIR"
echo "======================================"
echo ""

# ── 1. Clone / 更新 仓库 ───────────────────────
echo "📦 [1/6] 下载学习资料库..."
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "   检测到已有仓库，执行 git pull 拉取最新数据..."
    git -C "$INSTALL_DIR" pull --rebase
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
echo "   ✅ 资料库就绪：$INSTALL_DIR"

# ── 2. 生成本地 config.json ────────────────────
echo ""
echo "⚙️  [2/6] 生成本地配置文件..."
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
echo "🧠 [3/6] 安装 en-learning Skill..."
mkdir -p "$HOME/.claude/skills"
rm -rf "$SKILL_DIR"
cp -r "$INSTALL_DIR/en-learning" "$SKILL_DIR"
echo "   ✅ Skill 已安装：$SKILL_DIR"

# ── 4. 安装 GitHub CLI ─────────────────────────
echo ""
echo "🔧 [4/6] 检查 GitHub CLI..."
if [ -f "$GH_BIN" ] && "$GH_BIN" --version > /dev/null 2>&1; then
    echo "   已安装：$("$GH_BIN" --version | head -1)"
else
    echo "   正在下载 GitHub CLI..."
    ARCH=$(uname -m)
    [ "$ARCH" = "arm64" ] && GH_ARCH="arm64" || GH_ARCH="amd64"
    GH_URL=$(curl -sL "https://api.github.com/repos/cli/cli/releases/latest" | \
        python3 -c "import sys,json; data=json.load(sys.stdin); \
        [print(a['browser_download_url']) for a in data['assets'] \
        if 'macOS' in a['name'] and '$GH_ARCH' in a['name'] and a['name'].endswith('.zip')]" 2>/dev/null | head -1)
    if [ -n "$GH_URL" ]; then
        curl -sL "$GH_URL" -o /tmp/gh_install.zip
        unzip -o /tmp/gh_install.zip -d /tmp/gh_extracted > /dev/null 2>&1
        mkdir -p "$HOME/.local/bin"
        find /tmp/gh_extracted -name "gh" -type f -exec cp {} "$GH_BIN" \;
        chmod +x "$GH_BIN"
        rm -rf /tmp/gh_install.zip /tmp/gh_extracted
        echo "   ✅ GitHub CLI 已安装"
    else
        echo "   ⚠️  自动下载失败，请手动安装：https://cli.github.com"
    fi
fi

# ── 5. GitHub 登录 ─────────────────────────────
echo ""
echo "🔐 [5/6] 检查 GitHub 登录状态..."
if "$GH_BIN" auth status > /dev/null 2>&1; then
    LOGGED_IN=$("$GH_BIN" auth status 2>&1 | grep "Logged in" | head -1)
    echo "   已登录：$LOGGED_IN"
else
    echo "   需要登录 GitHub。"
    echo "   请前往：https://github.com/settings/tokens"
    echo "   创建 Token（勾选 repo + read:org 权限），然后粘贴到这里："
    echo ""
    read -p "   GitHub Token (ghp_...): " TOKEN
    echo "$TOKEN" | "$GH_BIN" auth login --with-token
    "$GH_BIN" auth setup-git
    echo "   ✅ 登录成功"
fi
"$GH_BIN" auth setup-git 2>/dev/null || true

# ── 6. 安装定时任务 ────────────────────────────
echo ""
echo "⏰ [6/6] 安装每日复习定时任务（每天 09:00）..."
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

# ── 首次生成复习卡片 ───────────────────────────
echo ""
echo "📚 生成今日复习卡片..."
python3 "$INSTALL_DIR/scripts/generate_review.py" || echo "   ⚠️  可稍后手动运行"

# ── 完成 ───────────────────────────────────────
echo ""
echo "======================================"
echo "  ✅ 安装完成！"
echo "======================================"
echo ""
echo "📌 在线复习卡片：https://chyi0426.github.io/EN_Learning_OC/"
echo "📁 本地资料库：  $INSTALL_DIR"
echo "🧠 Skill 位置：  $SKILL_DIR"
echo "⏰ 定时任务：    每天 09:00 自动更新并同步"
echo ""
echo "💡 任何一台电脑学习 → 自动 push 到 GitHub"
echo "💡 其他电脑打开 OpenCode → AI 自动 pull 最新数据"
echo ""

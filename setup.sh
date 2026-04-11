#!/bin/bash
# ================================================
# EN Learning OC - 新电脑一键安装脚本
# 使用方法：bash setup.sh
# ================================================

set -e

REPO_URL="https://github.com/Chyi0426/EN_Learning_OC.git"
INSTALL_DIR="$HOME/Desktop/EN_Learning_OC"
SKILL_DIR="$HOME/.claude/skills/en-learning"
GH_BIN="$HOME/.local/bin/gh"

echo ""
echo "======================================"
echo "  EN Learning OC - 环境安装"
echo "======================================"
echo ""

# ── 1. Clone 仓库 ──────────────────────────────
echo "📦 第一步：下载学习资料库..."
if [ -d "$INSTALL_DIR" ]; then
    echo "   已存在，执行 git pull 更新..."
    git -C "$INSTALL_DIR" pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    echo "   ✅ 下载完成：$INSTALL_DIR"
fi

# ── 2. 安装 Skill ──────────────────────────────
echo ""
echo "🧠 第二步：安装 en-learning Skill..."
mkdir -p "$HOME/.claude/skills"
if [ -d "$SKILL_DIR" ]; then
    echo "   已存在，覆盖更新..."
    rm -rf "$SKILL_DIR"
fi
cp -r "$INSTALL_DIR/en-learning" "$SKILL_DIR"
echo "   ✅ Skill 已安装到：$SKILL_DIR"

# ── 3. 安装 GitHub CLI ─────────────────────────
echo ""
echo "🔧 第三步：安装 GitHub CLI（用于同步复习卡片）..."
if [ -f "$GH_BIN" ]; then
    echo "   已安装：$($GH_BIN --version | head -1)"
else
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        GH_ARCH="arm64"
    else
        GH_ARCH="amd64"
    fi
    GH_URL=$(curl -sL "https://api.github.com/repos/cli/cli/releases/latest" | python3 -c "import sys,json; data=json.load(sys.stdin); [print(a['browser_download_url']) for a in data['assets'] if 'macOS' in a['name'] and '$GH_ARCH' in a['name'] and a['name'].endswith('.zip')]" 2>/dev/null | head -1)
    if [ -n "$GH_URL" ]; then
        curl -sL "$GH_URL" -o /tmp/gh.zip
        unzip -o /tmp/gh.zip -d /tmp/gh_extracted > /dev/null 2>&1
        mkdir -p "$HOME/.local/bin"
        find /tmp/gh_extracted -name "gh" -type f -exec cp {} "$GH_BIN" \;
        chmod +x "$GH_BIN"
        rm -rf /tmp/gh.zip /tmp/gh_extracted
        echo "   ✅ GitHub CLI 安装完成"
    else
        echo "   ⚠️  自动下载失败，请手动安装 GitHub CLI：https://cli.github.com"
    fi
fi

# ── 4. GitHub 登录 ─────────────────────────────
echo ""
echo "🔐 第四步：GitHub 登录..."
if $GH_BIN auth status > /dev/null 2>&1; then
    echo "   已登录：$($GH_BIN auth status 2>&1 | grep 'Logged in' | head -1)"
else
    echo "   需要登录 GitHub，请按以下步骤操作："
    echo "   1. 打开 https://github.com/settings/tokens"
    echo "   2. 点击 Generate new token (classic)"
    echo "   3. 勾选：repo + read:org"
    echo "   4. 生成后将 token 粘贴到下面："
    echo ""
    read -p "   请输入你的 GitHub Token (ghp_...): " TOKEN
    echo "$TOKEN" | $GH_BIN auth login --with-token
    $GH_BIN auth setup-git
    echo "   ✅ GitHub 登录成功"
fi

# ── 5. 安装定时任务 ────────────────────────────
echo ""
echo "⏰ 第五步：安装每日复习定时任务（每天 9:00 自动更新）..."

LAUNCHER="$HOME/Documents/en_review_launcher.sh"
PLIST_SRC="$INSTALL_DIR/scripts/com.raymond.en-learning-review.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.raymond.en-learning-review.plist"

# 修正 SKILL.md 中的路径（替换旧用户名为新用户名）
NEW_USER=$(whoami)
sed -i '' "s|/Users/[^/]*/Desktop/EN_Learning_OC|$INSTALL_DIR|g" \
    "$INSTALL_DIR/scripts/generate_review.py" \
    "$INSTALL_DIR/scripts/push_reminders.py" 2>/dev/null || true

# 创建启动脚本
cat > "$LAUNCHER" << EOF
#!/bin/bash
/usr/bin/python3 $INSTALL_DIR/scripts/generate_review.py >> $HOME/Documents/en_review.log 2>&1
EOF
chmod +x "$LAUNCHER"

# 生成适配新路径的 plist
cat > "$PLIST_DEST" << EOF
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
EOF

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "   ✅ 定时任务安装完成，每天 09:00 自动更新"

# ── 6. 生成今日复习卡片 ────────────────────────
echo ""
echo "📚 第六步：生成今日复习卡片..."
python3 "$INSTALL_DIR/scripts/generate_review.py"

# ── 完成 ───────────────────────────────────────
echo ""
echo "======================================"
echo "  ✅ 安装完成！"
echo "======================================"
echo ""
echo "📌 在线复习卡片：https://chyi0426.github.io/EN_Learning_OC/"
echo "📁 本地资料库：  $INSTALL_DIR"
echo "🧠 Skill 位置：  $SKILL_DIR"
echo "⏰ 定时任务：    每天 09:00 自动更新"
echo ""
echo "🚀 现在打开 OpenCode，就能直接使用 en-learning Skill 了！"
echo ""

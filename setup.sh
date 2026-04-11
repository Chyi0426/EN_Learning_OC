#!/bin/bash
# ================================================
# EN Learning OC - 一键安装脚本（本地复制版）
#
# 使用方法：
#   1. 把整个 EN_Learning_OC 文件夹复制到新电脑桌面
#   2. 打开终端，运行：
#      bash ~/Desktop/EN_Learning_OC/setup.sh
#
# 支持自定义安装路径：
#   bash setup.sh /你想放的位置/EN_Learning_OC
# ================================================

set -e

# ── 确定安装目录 ───────────────────────────────
# 优先用用户传入的参数，否则用脚本自身所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-$SCRIPT_DIR}"

SKILL_DIR="$HOME/.claude/skills/en-learning"
GH_BIN="$HOME/.local/bin/gh"
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
    echo "   ❌ 文件夹不完整，请确认复制了完整的 EN_Learning_OC 文件夹："
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
echo "   ✅ config.json 已生成（路径：$INSTALL_DIR）"

# ── 3. 安装 Skill ──────────────────────────────
echo ""
echo "🧠 [3/5] 安装 en-learning Skill 到 OpenCode..."
mkdir -p "$HOME/.claude/skills"
rm -rf "$SKILL_DIR"
cp -r "$INSTALL_DIR/en-learning" "$SKILL_DIR"
echo "   ✅ Skill 已安装：$SKILL_DIR"

# ── 4. 安装 GitHub CLI + 登录 ──────────────────
echo ""
echo "🔧 [4/5] 配置 GitHub（用于多设备同步）..."

# 安装 gh CLI
if [ -f "$GH_BIN" ] && "$GH_BIN" --version > /dev/null 2>&1; then
    echo "   GitHub CLI 已安装：$("$GH_BIN" --version | head -1)"
else
    echo "   正在下载 GitHub CLI..."
    ARCH=$(uname -m)
    [ "$ARCH" = "arm64" ] && GH_ARCH="arm64" || GH_ARCH="amd64"
    GH_URL=$(curl -sL "https://api.github.com/repos/cli/cli/releases/latest" | \
        python3 -c "import sys,json; d=json.load(sys.stdin); \
        [print(a['browser_download_url']) for a in d['assets'] \
        if 'macOS' in a['name'] and '$GH_ARCH' in a['name'] and a['name'].endswith('.zip')]" 2>/dev/null | head -1)
    if [ -n "$GH_URL" ]; then
        curl -sL "$GH_URL" -o /tmp/gh_install.zip
        unzip -o /tmp/gh_install.zip -d /tmp/gh_extracted > /dev/null 2>&1
        mkdir -p "$HOME/.local/bin"
        find /tmp/gh_extracted -name "gh" -type f -exec cp {} "$GH_BIN" \;
        chmod +x "$GH_BIN"
        rm -rf /tmp/gh_install.zip /tmp/gh_extracted
        echo "   ✅ GitHub CLI 安装完成"
    else
        echo "   ⚠️  GitHub CLI 下载失败，跳过（同步功能将不可用）"
        GH_BIN=""
    fi
fi

# 登录 GitHub
if [ -n "$GH_BIN" ] && [ -f "$GH_BIN" ]; then
    if "$GH_BIN" auth status > /dev/null 2>&1; then
        echo "   已登录 GitHub：$("$GH_BIN" auth status 2>&1 | grep 'Logged in' | head -1)"
    else
        echo ""
        echo "   需要登录 GitHub 才能同步数据到云端。"
        echo "   请按以下步骤获取 Token："
        echo "   1. 浏览器打开：https://github.com/settings/tokens"
        echo "   2. 点击 Generate new token (classic)"
        echo "   3. 勾选权限：repo 和 read:org"
        echo "   4. 点击 Generate token，复制生成的 token"
        echo ""
        read -p "   粘贴你的 GitHub Token (ghp_...): " GH_TOKEN
        if [ -n "$GH_TOKEN" ]; then
            echo "$GH_TOKEN" | "$GH_BIN" auth login --with-token
            "$GH_BIN" auth setup-git
            echo "   ✅ GitHub 登录成功"
        else
            echo "   ⚠️  未输入 Token，跳过（同步功能将不可用）"
        fi
    fi
    # 配置 git 使用 gh 认证
    "$GH_BIN" auth setup-git 2>/dev/null || true
fi

# 初始化 git（如果还不是 git 仓库）
if [ ! -d "$INSTALL_DIR/.git" ]; then
    echo ""
    echo "   初始化 git 仓库并关联远程..."
    git -C "$INSTALL_DIR" init
    git -C "$INSTALL_DIR" remote add origin "https://github.com/Chyi0426/EN_Learning_OC.git"
    git -C "$INSTALL_DIR" fetch origin main 2>/dev/null || true
    git -C "$INSTALL_DIR" branch -M main 2>/dev/null || true
    git -C "$INSTALL_DIR" branch --set-upstream-to=origin/main main 2>/dev/null || true
    echo "   ✅ git 已关联远程仓库"
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
echo "   ✅ 定时任务已安装（每天 09:00 自动更新）"

# ── 生成今日复习卡片 ───────────────────────────
echo ""
echo "📚 生成今日复习卡片..."
python3 "$INSTALL_DIR/scripts/generate_review.py" && \
    open "$INSTALL_DIR/daily_review.html" || \
    echo "   ⚠️  生成失败，可稍后手动运行"

# ── 完成 ───────────────────────────────────────
echo ""
echo "======================================"
echo "  ✅ 安装完成！"
echo "======================================"
echo ""
echo "  📁 资料库位置：$INSTALL_DIR"
echo "  🧠 Skill 位置：$SKILL_DIR"
echo "  🌐 在线复习：  https://chyi0426.github.io/EN_Learning_OC/"
echo "  ⏰ 定时任务：  每天 09:00 自动更新"
echo ""
echo "  打开 OpenCode，直接问英文问题就可以开始了！"
echo ""

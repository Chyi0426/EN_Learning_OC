#!/bin/bash
# EN Learning Review - 安装/卸载定时任务的辅助脚本

PLIST_NAME="com.raymond.en-learning-review.plist"
PLIST_SOURCE="/Users/raymond.zhong/Desktop/EN_Learning_OC/scripts/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

case "$1" in
    install)
        echo "正在安装每日复习定时任务..."
        cp "$PLIST_SOURCE" "$PLIST_DEST"
        launchctl load "$PLIST_DEST"
        echo "✅ 安装成功！每天早上 9:00 将自动推送复习提醒。"
        echo "   提醒会出现在 macOS 提醒事项 App 的「EN复习」列表中。"
        echo "   同时会在桌面生成 daily_review.html 复习卡片页面。"
        ;;
    uninstall)
        echo "正在卸载每日复习定时任务..."
        launchctl unload "$PLIST_DEST" 2>/dev/null
        rm -f "$PLIST_DEST"
        echo "✅ 已卸载定时任务。"
        ;;
    run)
        echo "手动执行一次复习推送..."
        python3 /Users/raymond.zhong/Desktop/EN_Learning_OC/scripts/push_reminders.py
        ;;
    status)
        if launchctl list | grep -q "com.raymond.en-learning-review"; then
            echo "✅ 定时任务已启用，每天 9:00 自动运行。"
        else
            echo "❌ 定时任务未启用。运行 '$0 install' 来安装。"
        fi
        ;;
    *)
        echo "用法: $0 {install|uninstall|run|status}"
        echo ""
        echo "  install   - 安装每日 9:00 自动推送"
        echo "  uninstall - 卸载定时任务"
        echo "  run       - 手动执行一次推送"
        echo "  status    - 查看定时任务状态"
        ;;
esac

#!/bin/bash
# 清理剪贴板格式，只保留纯文本
pbpaste | pbcopy
# 可选：显示通知
osascript -e 'display notification "剪贴板已清理为纯文本" with title "Clean Paste"' 2>/dev/null || true 
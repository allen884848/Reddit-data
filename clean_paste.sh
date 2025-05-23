#!/bin/bash
# 清理剪贴板格式，只保留纯文本
pbpaste | pbcopy
echo "剪贴板已清理为纯文本" 
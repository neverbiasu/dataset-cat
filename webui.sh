#!/bin/bash
echo "Starting Dataset Cat WebUI..."

# 使用 Poetry 安装依赖（可选）
poetry install
if [ $? -ne 0 ]; then
    echo "Poetry install failed, continuing anyway..."
fi

# 启动原始 WebUI（包含国际化支持）
python -m dataset_cat.webui

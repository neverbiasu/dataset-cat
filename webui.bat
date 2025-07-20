@echo off
echo Starting Dataset Cat WebUI...

REM 使用 Poetry 安装依赖（可选）
poetry install
if %errorlevel% neq 0 (
    echo Poetry install failed, continuing anyway...
)

REM 启动原始 WebUI（包含国际化支持）
python -m dataset_cat.webui
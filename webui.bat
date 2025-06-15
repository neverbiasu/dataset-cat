@echo off
poetry install
if %errorlevel% neq 0 (
    echo Poetry install failed.
    exit /b %errorlevel%
)
dataset-cat-webui
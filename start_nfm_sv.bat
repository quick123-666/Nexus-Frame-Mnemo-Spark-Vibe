@echo off
echo ========================================
echo    NFM-SV 正在启动...
echo ========================================
cd /d "%~dp0"
echo [1/2] 检查并安装依赖...
python -m pip install -r requirements.txt -q
echo [2/2] 启动服务...
python -m uvicorn web.server:app --host 0.0.0.0 --port 8000 --reload
pause

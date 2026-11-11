@echo off
chcp 65001 >nul
cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo 未检测到 Node.js，请先安装 18 或更高版本：https://nodejs.org/
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo 已生成 .env，可直接运行；需要在线模型时再填写 DEEPSEEK_API_KEY。
)

echo.
echo 启动地址：http://127.0.0.1:8787
echo 按 Ctrl+C 停止服务。
echo.
node server.js
pause

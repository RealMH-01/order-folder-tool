@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title 订单文件夹工具 - 一键打包

echo ============================================================
echo                订单文件夹自动创建工具 - 一键打包
echo ============================================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 国内镜像源（无需 VPN）
set MIRROR=-i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
set TIMEOUT=--timeout 60

REM 1. 检查 Python
echo [1/4] 检查 Python 环境...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ****************************************************************
    echo   没有检测到 Python！
    echo.
    echo   请先从官网下载并安装 Python 3.9 或更高版本：
    echo       https://www.python.org/downloads/
    echo.
    echo   安装时，请务必勾选 【Add Python to PATH】 这个选项！
    echo   安装完成后，关闭此窗口，重新双击本文件即可。
    echo ****************************************************************
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM 2. 安装依赖
echo [2/4] 安装依赖（使用清华镜像源，无需 VPN）...
echo.
python -m pip install --upgrade pip %MIRROR% %TIMEOUT%
if errorlevel 1 (
    echo [提示] pip 升级跳过，不影响打包。
)
python -m pip install -r requirements.txt %MIRROR% %TIMEOUT%
if errorlevel 1 (
    echo.
    echo 依赖安装失败，请检查网络后重试。
    pause
    exit /b 1
)
python -m pip install pyinstaller %MIRROR% %TIMEOUT%
if errorlevel 1 (
    echo.
    echo PyInstaller 安装失败，请检查网络后重试。
    pause
    exit /b 1
)
echo.
echo      依赖安装完成！
echo.

REM 3. 打包
echo [3/4] 正在打包（约 3~5 分钟）...
echo.
if exist "dist\订单文件夹工具.exe" del /f /q "dist\订单文件夹工具.exe"
pyinstaller --onefile --windowed --noconfirm --clean --name "订单文件夹工具" main.py
if errorlevel 1 (
    echo.
    echo 打包失败！请截图上方错误信息发给开发者。
    pause
    exit /b 1
)

REM 4. 完成
echo.
echo ============================================================
echo [4/4] 打包完成！
echo.
echo 请到 dist 文件夹找到：【订单文件夹工具.exe】
echo 双击即可运行，可复制到任意 Windows 电脑使用。
echo ============================================================
echo.
pause

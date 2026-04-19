# -*- coding: utf-8 -*-
"""订单文件夹自动创建工具 - 程序入口。"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow
from app.style import APP_QSS


def main():
    """启动应用。"""
    # 高 DPI 适配（必须在 QApplication 构造前设置）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("订单文件夹自动创建工具")

    # 底层样式引擎使用 Fusion，跨平台观感最一致
    try:
        app.setStyle("Fusion")
    except Exception:
        pass

    # 全局字体（同时照顾中英文）
    font = QFont("Microsoft YaHei UI", 10)
    if not font.exactMatch():
        # 非 Windows 平台没有 Microsoft YaHei UI，退化为 Microsoft YaHei
        font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 全局样式表
    app.setStyleSheet(APP_QSS)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

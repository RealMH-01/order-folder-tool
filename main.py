# -*- coding: utf-8 -*-
"""订单文件夹自动创建工具 - 程序入口"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow
from app.style import APP_QSS


def main():
    # 高 DPI 适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("订单文件夹自动创建工具")
    # 全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    # 全局样式
    app.setStyleSheet(APP_QSS)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""主窗口：用 QStackedWidget 承载 5 个页面"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from .core.storage import Storage, load_bootstrap
from .pages.home_page import HomePage
from .pages.single_page import SinglePage
from .pages.batch_page import BatchPage
from .pages.templates_page import TemplatesPage
from .pages.history_page import HistoryPage
from .pages.help_page import HelpPage


PAGE_HOME = 0
PAGE_SINGLE = 1
PAGE_BATCH = 2
PAGE_TEMPLATES = 3
PAGE_HISTORY = 4
PAGE_HELP = 5


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("订单文件夹自动创建工具")
        self.resize(1180, 760)

        # 初始化 storage（若有上次根目录，自动加载）
        bs = load_bootstrap()
        last_root = bs.get("last_root", "")
        self.storage = Storage(last_root if last_root else None)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_home = HomePage(self.storage)
        self.page_single = SinglePage(self.storage)
        self.page_batch = BatchPage(self.storage)
        self.page_templates = TemplatesPage(self.storage)
        self.page_history = HistoryPage(self.storage)
        self.page_help = HelpPage()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_single)
        self.stack.addWidget(self.page_batch)
        self.stack.addWidget(self.page_templates)
        self.stack.addWidget(self.page_history)
        self.stack.addWidget(self.page_help)

        # 事件绑定
        self.page_home.request_single.connect(lambda: self._goto(PAGE_SINGLE))
        self.page_home.request_batch.connect(lambda: self._goto(PAGE_BATCH))
        self.page_home.request_templates.connect(lambda: self._goto(PAGE_TEMPLATES))
        self.page_home.request_history.connect(lambda: self._goto(PAGE_HISTORY))
        self.page_home.request_help.connect(lambda: self._goto(PAGE_HELP))
        self.page_home.salespersons_changed.connect(self._on_salespersons_changed)
        self.page_home.root_dir_changed.connect(self._on_root_changed)

        self.page_single.request_back.connect(lambda: self._goto(PAGE_HOME))
        self.page_batch.request_back.connect(lambda: self._goto(PAGE_HOME))
        self.page_templates.request_back.connect(lambda: self._goto(PAGE_HOME))
        self.page_history.request_back.connect(lambda: self._goto(PAGE_HOME))
        self.page_help.request_back.connect(lambda: self._goto(PAGE_HOME))

        self.stack.setCurrentIndex(PAGE_HOME)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def _goto(self, idx):
        self.stack.setCurrentIndex(idx)
        w = self.stack.widget(idx)
        if hasattr(w, "refresh"):
            try:
                w.refresh()
            except Exception as e:
                self.statusBar().showMessage(f"刷新失败：{e}", 5000)
        title_map = {
            PAGE_HOME: "首页",
            PAGE_SINGLE: "单笔创建",
            PAGE_BATCH: "批量导入",
            PAGE_TEMPLATES: "模板管理",
            PAGE_HISTORY: "历史记录",
            PAGE_HELP: "使用帮助",
        }
        self.setWindowTitle(f"订单文件夹自动创建工具 - {title_map.get(idx, '')}")
        # 根目录显示
        if self.storage.root_dir:
            self.statusBar().showMessage(f"根目录：{self.storage.root_dir}")

    def _on_root_changed(self, new_root):
        # 根目录变化，storage 已经 set 过，通知各页面刷新
        for p in (self.page_single, self.page_batch, self.page_templates, self.page_history):
            if hasattr(p, "refresh"):
                try:
                    p.refresh()
                except Exception:
                    pass
        self.statusBar().showMessage(f"根目录已切换至：{new_root}", 5000)

    def _on_salespersons_changed(self):
        """业务员列表被更新（例如扫描导入），通知相关页面刷新"""
        for p in (self.page_single, self.page_batch):
            if hasattr(p, "refresh"):
                try:
                    p.refresh()
                except Exception:
                    pass
        self.statusBar().showMessage("业务员/客户列表已更新", 5000)

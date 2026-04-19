# -*- coding: utf-8 -*-
"""历史记录页"""

import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                              QMessageBox, QPushButton, QTableWidget,
                              QTableWidgetItem, QVBoxLayout, QWidget)


COLS = [
    ("time", "操作时间", 150),
    ("operator", "操作人", 100),
    ("salesperson", "业务员", 100),
    ("customer", "客户", 160),
    ("order_no", "订单号", 160),
    ("order_type", "订单类型", 80),
    ("product_category", "产品类别", 90),
    ("template_name", "模板", 200),
    ("path", "路径", 300),
    ("result", "结果", 140),
]


class HistoryPage(QWidget):
    request_back = pyqtSignal()

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._all_records = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        btn_back = QPushButton("← 返回首页")
        btn_back.setObjectName("SecondaryButton")
        btn_back.clicked.connect(self.request_back.emit)
        top.addWidget(btn_back)
        title = QLabel("历史记录")
        title.setObjectName("TitleLabel")
        top.addWidget(title)
        top.addStretch(1)
        root.addLayout(top)

        # 搜索
        sh = QHBoxLayout()
        sh.addWidget(QLabel("搜索："))
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("按订单号 / 业务员 / 客户过滤")
        self.edit_search.textChanged.connect(self._apply_filter)
        sh.addWidget(self.edit_search, 1)
        btn_open = QPushButton("打开选中订单文件夹")
        btn_open.setObjectName("SecondaryButton")
        btn_open.clicked.connect(self._open_selected)
        btn_refresh = QPushButton("刷新")
        btn_refresh.setObjectName("SecondaryButton")
        btn_refresh.clicked.connect(self.refresh)
        sh.addWidget(btn_open)
        sh.addWidget(btn_refresh)
        root.addLayout(sh)

        # 表格
        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels([c[1] for c in COLS])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        for i, (_, _, w) in enumerate(COLS):
            self.table.setColumnWidth(i, w)
        root.addWidget(self.table, 1)

    def refresh(self):
        self._all_records = self.storage.load_history()
        # 已按 insert 顺序最新在前
        self._apply_filter()

    def _apply_filter(self):
        kw = self.edit_search.text().strip().lower()
        records = self._all_records
        if kw:
            records = [r for r in records if
                       kw in str(r.get("order_no", "")).lower() or
                       kw in str(r.get("salesperson", "")).lower() or
                       kw in str(r.get("customer", "")).lower()]
        self.table.setRowCount(0)
        for rec in records:
            r = self.table.rowCount()
            self.table.insertRow(r)
            result_txt = rec.get("result", "")
            if "成功" in result_txt:
                detail = f"{result_txt}（新建 {rec.get('created_count',0)}，跳过 {rec.get('skipped_count',0)}，复制 {rec.get('copied_count',0)}）"
            else:
                detail = result_txt
            for ci, (k, _, _) in enumerate(COLS):
                v = detail if k == "result" else str(rec.get(k, ""))
                self.table.setItem(r, ci, QTableWidgetItem(v))

    def _open_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "提示", "请选择一行")
            return
        row = rows[0].row()
        path_item = self.table.item(row, 8)
        if not path_item:
            return
        path = path_item.text()
        if not os.path.isdir(path):
            QMessageBox.warning(self, "提示", "目录不存在（可能已被移动或删除）")
            return
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            elif os.name == "posix":
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

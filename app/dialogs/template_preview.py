# -*- coding: utf-8 -*-
"""模板预览对话框：以树状图展示模板的完整文件夹层级"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout)


class TemplatePreviewDialog(QDialog):
    """
    只读的模板预览。每个文件夹节点下展示 ref_files 中的参考文件名。
    """

    def __init__(self, template, title="模板预览", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 560)
        self._build_ui()
        if template:
            self._populate(template)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 说明
        tip = QLabel("📁 文件夹（蓝色）   📄 参考文件（灰色）。此预览为只读，修改请到「模板管理」页。")
        tip.setStyleSheet("color:#555;")
        layout.addWidget(tip)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "来源 / 说明"])
        self.tree.setColumnWidth(0, 380)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)

    def _populate(self, template):
        root_item = self._add_folder_item(None, template)
        self.tree.expandAll()

    def _add_folder_item(self, parent, node):
        item = QTreeWidgetItem([node.get("name", ""), ""])
        # 文件夹图标（用文字模拟）
        item.setText(0, "📁 " + node.get("name", ""))
        item.setForeground(0, QBrush(QColor("#1976D2")))
        font = QFont()
        font.setBold(True)
        item.setFont(0, font)
        if node.get("optional"):
            item.setText(1, f"可选（条件: {node.get('condition', '-')}）")
        if parent is None:
            self.tree.addTopLevelItem(item)
        else:
            parent.addChild(item)

        # 参考文件
        for rf in node.get("ref_files", []) or []:
            fname = rf.get("filename", "")
            source = rf.get("source", "")
            has_tpl = rf.get("file_template")
            label = f"📄 {fname}"
            if has_tpl:
                label += "   [有模板]"
            f_item = QTreeWidgetItem([label, source])
            f_item.setForeground(0, QBrush(QColor("#666666")))
            item.addChild(f_item)

        # 子文件夹
        for child in node.get("children", []) or []:
            self._add_folder_item(item, child)
        return item

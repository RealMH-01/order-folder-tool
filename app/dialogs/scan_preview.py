# -*- coding: utf-8 -*-
"""
扫描预览对话框：
- 展示文件夹树：绿色"已存在" / 蓝色"待创建" / 灰色"模板外"
- 允许修改目标路径
- 点击"确认创建"或"取消"
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout)

from ..core import folder_builder


COLOR_GREEN = "#4CAF50"
COLOR_BLUE = "#2196F3"
COLOR_GRAY = "#9E9E9E"


class ScanPreviewDialog(QDialog):
    """扫描预览对话框"""

    def __init__(self, base_path, template_folders, extras,
                 parent=None, display_path: str = None,
                 ctx: dict = None):
        """
        base_path: 客户目录（不含订单号），是 compare_with_existing 使用的基础。
        display_path: 用户在顶部"目标路径"输入框中看到的完整订单文件夹路径
                     （客户目录 + 订单号）。如果用户修改了该路径，
                     get_target_path() 将返回修改后的完整订单路径。
        ctx: 占位符上下文字典。传入后，预览中文件名会显示替换后的真实名字
             （例如 <订单号> → XS-TEST001NH）。为 None 时保留原始占位符。
        """
        super().__init__(parent)
        self.setWindowTitle("创建预览")
        self.resize(820, 620)

        self._base_path = base_path
        self._display_path = display_path or base_path
        self._template_folders = template_folders
        self._extras = extras
        self._ctx = ctx or {}
        self._build_ui()
        self._populate()

    # ------ UI ------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 顶部提示
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("font-weight:bold;")
        layout.addWidget(self.lbl_info)

        # 图例
        legend = QLabel(
            f'<span style="color:{COLOR_GREEN};font-weight:bold;">■</span> 已存在（跳过） &nbsp;&nbsp;'
            f'<span style="color:{COLOR_BLUE};font-weight:bold;">■</span> 待创建 &nbsp;&nbsp;'
            f'<span style="color:{COLOR_GRAY};font-weight:bold;">■</span> 模板外（不操作）'
        )
        layout.addWidget(legend)

        # 树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "状态", "说明"])
        self.tree.setColumnWidth(0, 420)
        self.tree.setColumnWidth(1, 110)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree, 1)

        # 目标路径
        h = QHBoxLayout()
        h.addWidget(QLabel("目标路径："))
        self.path_edit = QLineEdit(self._display_path)
        h.addWidget(self.path_edit, 1)
        btn_browse = QPushButton("修改…")
        btn_browse.setObjectName("SecondaryButton")
        btn_browse.clicked.connect(self._browse_path)
        h.addWidget(btn_browse)
        layout.addLayout(h)

        # 按钮
        btns = QDialogButtonBox()
        self.btn_ok = btns.addButton("确认创建", QDialogButtonBox.AcceptRole)
        self.btn_cancel = btns.addButton("取消", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _browse_path(self):
        d = QFileDialog.getExistingDirectory(self, "修改目标路径",
                                             self.path_edit.text() or "")
        if d:
            self.path_edit.setText(d)

    def _populate(self):
        # 统计
        exist_cnt = sum(1 for i in self._template_folders if i["status"] == "existing" and not i.get("is_root"))
        create_cnt = sum(1 for i in self._template_folders if i["status"] == "to_create" and not i.get("is_root"))
        root_existed = any(i["status"] == "existing" and i.get("is_root") for i in self._template_folders)
        extras_cnt = len(self._extras)
        if root_existed:
            info = f"⚠ 检测到该订单文件夹已存在。将补建 {create_cnt} 个缺失文件夹，跳过 {exist_cnt} 个已有，{extras_cnt} 个模板外目录不操作。"
        else:
            info = f"将全新创建 {create_cnt} 个文件夹。"
        self.lbl_info.setText(info)

        # 构建以 rel_path 为键的 map
        path_to_item = {}
        # 先建根
        root_node = None
        for it in self._template_folders:
            if it.get("is_root"):
                root_node = it
                break
        if root_node is None:
            return
        root_qt = QTreeWidgetItem([f"📁 {root_node['name']}",
                                   self._status_label(root_node["status"]),
                                   ""])
        self._style_item(root_qt, root_node["status"])
        self.tree.addTopLevelItem(root_qt)
        # 根节点既可能 rel_path="" 也可能为订单号
        path_to_item[""] = root_qt
        if root_node.get("rel_path"):
            path_to_item[root_node["rel_path"]] = root_qt

        # 依次插入非根节点（按 rel_path 深度排序，保证父先于子）
        non_root = [i for i in self._template_folders if not i.get("is_root")]
        non_root.sort(key=lambda x: x["rel_path"].count("/") + x["rel_path"].count("\\"))
        import os
        for it in non_root:
            rel = it["rel_path"]
            parent_rel = os.path.dirname(rel)
            # 如果父路径等于根节点的 rel_path（订单号），或者为空，都挂在根下
            parent_qt = path_to_item.get(parent_rel, root_qt)
            qt_item = QTreeWidgetItem([f"📁 {it['name']}",
                                       self._status_label(it["status"]),
                                       ""])
            self._style_item(qt_item, it["status"])
            parent_qt.addChild(qt_item)
            path_to_item[rel] = qt_item
            # 列出 ref_files
            for rf in it.get("ref_files", []):
                fname = rf.get("filename", "")
                # 功能 A：若传入 ctx，则显示替换后的真实文件名
                if self._ctx:
                    fname = folder_builder.replace_placeholders(fname, self._ctx)
                has_tpl = "（有模板）" if rf.get("file_template") else ""
                f_item = QTreeWidgetItem([f"   📄 {fname}{has_tpl}", "", rf.get("source", "")])
                f_item.setForeground(0, QBrush(QColor("#555555")))
                qt_item.addChild(f_item)

        # 根节点的 ref_files 也要展示
        for rf in root_node.get("ref_files", []):
            fname = rf.get("filename", "")
            if self._ctx:
                fname = folder_builder.replace_placeholders(fname, self._ctx)
            has_tpl = "（有模板）" if rf.get("file_template") else ""
            f_item = QTreeWidgetItem([f"   📄 {fname}{has_tpl}", "", rf.get("source", "")])
            f_item.setForeground(0, QBrush(QColor("#555555")))
            root_qt.addChild(f_item)

        # extras
        for ex in self._extras:
            rel = ex["rel_path"]
            parent_rel = os.path.dirname(rel)
            parent_qt = path_to_item.get(parent_rel, root_qt)
            qt_item = QTreeWidgetItem([f"📁 {ex['name']}", "模板外", ""])
            self._style_item(qt_item, "out_of_template")
            parent_qt.addChild(qt_item)
            path_to_item[rel] = qt_item

        self.tree.expandAll()

    def _status_label(self, s):
        return {"existing": "已存在", "to_create": "待创建",
                "out_of_template": "模板外"}.get(s, "")

    def _style_item(self, item, status):
        color = {"existing": COLOR_GREEN, "to_create": COLOR_BLUE,
                 "out_of_template": COLOR_GRAY}.get(status, "#000")
        item.setForeground(0, QBrush(QColor(color)))
        item.setForeground(1, QBrush(QColor(color)))
        f = QFont()
        f.setBold(True)
        item.setFont(1, f)

    # ------ 对外 ------
    def get_target_path(self):
        return self.path_edit.text().strip()

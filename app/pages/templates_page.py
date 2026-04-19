# -*- coding: utf-8 -*-
"""模板管理页"""

import copy
import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QInputDialog, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

from ..dialogs.template_editor import TemplateEditorDialog
from ..dialogs.template_preview import TemplatePreviewDialog


class TemplatesPage(QWidget):
    request_back = pyqtSignal()

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._build_ui()

    # ============== UI ==============
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        btn_back = QPushButton("← 返回首页")
        btn_back.setObjectName("SecondaryButton")
        btn_back.clicked.connect(self.request_back.emit)
        top.addWidget(btn_back)
        title = QLabel("模板管理")
        title.setObjectName("TitleLabel")
        top.addWidget(title)
        top.addStretch(1)
        root.addLayout(top)

        body = QHBoxLayout()
        # 左侧列表
        left = QVBoxLayout()
        left.addWidget(QLabel("模板列表"))
        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self._on_select)
        left.addWidget(self.list, 1)

        ops = QHBoxLayout()
        self.btn_new = QPushButton("新建模板")
        self.btn_new.clicked.connect(self._new_template)
        self.btn_edit = QPushButton("编辑模板")
        self.btn_edit.setObjectName("SecondaryButton")
        self.btn_edit.clicked.connect(self._edit_template)
        self.btn_del = QPushButton("删除")
        self.btn_del.setObjectName("DangerButton")
        self.btn_del.clicked.connect(self._delete_template)
        ops.addWidget(self.btn_new)
        ops.addWidget(self.btn_edit)
        ops.addWidget(self.btn_del)
        left.addLayout(ops)

        ops2 = QHBoxLayout()
        self.btn_save_personal = QPushButton("另存为个人模板")
        self.btn_save_personal.setObjectName("SecondaryButton")
        self.btn_save_personal.clicked.connect(self._save_as_personal)
        self.btn_save_customer = QPushButton("另存为客户模板")
        self.btn_save_customer.setObjectName("SecondaryButton")
        self.btn_save_customer.clicked.connect(self._save_as_customer)
        ops2.addWidget(self.btn_save_personal)
        ops2.addWidget(self.btn_save_customer)
        left.addLayout(ops2)

        body.addLayout(left, 1)

        # 右侧预览
        right = QVBoxLayout()
        right.addWidget(QLabel("模板结构预览"))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "来源"])
        self.tree.setColumnWidth(0, 360)
        right.addWidget(self.tree, 1)

        body.addLayout(right, 2)
        root.addLayout(body, 1)

    # ============== 入口 ==============
    def refresh(self):
        self._reload_list()

    # ============== 加载 ==============
    def _reload_list(self):
        self.list.clear()
        groups = self.storage.list_template_files()

        def add_header(text):
            it = QListWidgetItem(text)
            it.setFlags(Qt.NoItemFlags)
            f = QFont()
            f.setBold(True)
            it.setFont(f)
            it.setForeground(QBrush(QColor("#1976D2")))
            it.setBackground(QBrush(QColor("#E3F2FD")))
            self.list.addItem(it)

        add_header("▌ 公司标准模板（不可删除）")
        for fn in groups["standard"]:
            tpl = self.storage.load_template(fn)
            label = (tpl.get("display_name") if tpl else None) or fn.replace(".json", "")
            item = QListWidgetItem("  " + label)
            item.setData(Qt.UserRole, fn)
            self.list.addItem(item)

        add_header("▌ 业务员个人模板")
        for fn in groups["salesperson"]:
            tpl = self.storage.load_template(fn)
            label = (tpl.get("display_name") if tpl else None) or fn.replace(".json", "")
            item = QListWidgetItem("  " + label)
            item.setData(Qt.UserRole, fn)
            self.list.addItem(item)

        add_header("▌ 业务员-客户专属模板")
        for fn in groups["customer"]:
            tpl = self.storage.load_template(fn)
            label = (tpl.get("display_name") if tpl else None) or fn.replace(".json", "")
            item = QListWidgetItem("  " + label)
            item.setData(Qt.UserRole, fn)
            self.list.addItem(item)

        # 默认选第一个可选项
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.UserRole):
                self.list.setCurrentRow(i)
                break

    def _current_filename(self):
        it = self.list.currentItem()
        if not it:
            return None
        return it.data(Qt.UserRole)

    def _on_select(self):
        fn = self._current_filename()
        self.tree.clear()
        if not fn:
            return
        tpl = self.storage.load_template(fn)
        if not tpl:
            return
        self._render_tree(None, tpl)
        self.tree.expandAll()
        # 控制删除按钮
        self.btn_del.setEnabled(not fn.startswith("standard_"))

    def _render_tree(self, parent, node):
        name = node.get("name", "")
        it = QTreeWidgetItem([f"📁 {name}", "文件夹"])
        it.setForeground(0, QBrush(QColor("#1976D2")))
        f = QFont()
        f.setBold(True)
        it.setFont(0, f)
        if node.get("optional"):
            it.setText(1, f"可选: {node.get('condition','')}")
        if parent is None:
            self.tree.addTopLevelItem(it)
        else:
            parent.addChild(it)
        for rf in node.get("ref_files", []) or []:
            label = f"📄 {rf.get('filename','')}"
            if rf.get("file_template"):
                label += "   [模板: " + rf["file_template"] + "]"
            c = QTreeWidgetItem([label, rf.get("source", "")])
            c.setForeground(0, QBrush(QColor("#555555")))
            it.addChild(c)
        for child in node.get("children", []) or []:
            self._render_tree(it, child)

    # ============== 操作 ==============
    def _new_template(self):
        # 选择订单类型
        type_, ok = QInputDialog.getItem(self, "选择基于的标准模板",
                                         "订单类型：", ["外贸", "内贸"], 0, False)
        if not ok:
            return
        base_fn = self.storage.standard_template_filename(type_)
        base = self.storage.load_template(base_fn)
        if not base:
            QMessageBox.warning(self, "错误", "标准模板缺失")
            return
        # 编辑一个副本
        dlg = TemplateEditorDialog(copy.deepcopy(base), base_template=base,
                                   title=f"新建模板（基于 标准 {type_}）",
                                   parent=self)
        if dlg.exec_() != dlg.Accepted:
            return
        edited = dlg.result_template()
        # 询问保存方式
        self._ask_save_scope(edited, type_)

    def _edit_template(self):
        fn = self._current_filename()
        if not fn:
            QMessageBox.information(self, "提示", "请先选择一个模板")
            return
        tpl = self.storage.load_template(fn)
        if not tpl:
            return
        order_type = "外贸" if tpl.get("type") == "export" else "内贸"
        base = self.storage.load_template(self.storage.standard_template_filename(order_type))
        dlg = TemplateEditorDialog(copy.deepcopy(tpl), base_template=base,
                                   title=f"编辑 - {fn}", parent=self)
        if dlg.exec_() != dlg.Accepted:
            return
        edited = dlg.result_template()
        if fn.startswith("standard_"):
            r = QMessageBox.question(self, "确认修改",
                "你正在修改公司标准模板，此操作会影响所有使用该模板的订单。\n\n确定保存吗？",
                QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                self.storage.save_template(fn, edited)
                QMessageBox.information(self, "已保存", "标准模板已更新")
                self._on_select()
        else:
            self.storage.save_template(fn, edited)
            QMessageBox.information(self, "已保存", f"模板 {fn} 已保存")
            self._on_select()


    def _ask_save_scope(self, edited, order_type):
        """在新建/编辑标准模板后，询问保存范围"""
        dlg = QDialog(self)
        dlg.setWindowTitle("另存为…")
        dlg.resize(420, 220)
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel("选择保存类型："))
        cmb_scope = QComboBox()
        cmb_scope.addItems(["业务员个人模板", "业务员-客户专属模板"])
        v.addWidget(cmb_scope)
        v.addWidget(QLabel("业务员："))
        cmb_sales = QComboBox()
        cmb_sales.addItems([it["name"] for it in self.storage.load_salespersons()])
        cmb_sales.setEditable(True)
        v.addWidget(cmb_sales)
        v.addWidget(QLabel("客户（仅客户模板需要）："))
        cmb_cust = QComboBox()
        cmb_cust.setEditable(True)
        v.addWidget(cmb_cust)

        def _refresh_cust():
            cmb_cust.clear()
            cmb_cust.addItems(self.storage.get_customers(cmb_sales.currentText()))
        cmb_sales.currentTextChanged.connect(_refresh_cust)
        _refresh_cust()

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        v.addWidget(bb)
        if dlg.exec_() != dlg.Accepted:
            return
        scope = cmb_scope.currentText()
        sp = cmb_sales.currentText().strip()
        if not sp:
            QMessageBox.warning(self, "提示", "请选择/输入业务员")
            return
        if scope == "业务员个人模板":
            fn = self.storage.salesperson_template_filename(sp, order_type)
        else:
            cu = cmb_cust.currentText().strip()
            if not cu:
                QMessageBox.warning(self, "提示", "请选择/输入客户")
                return
            fn = self.storage.customer_template_filename(sp, cu, order_type)
        edited["type"] = "export" if order_type == "外贸" else "domestic"
        if scope == "业务员个人模板":
            edited["display_name"] = f"{sp} - 个人{order_type}模板"
        else:
            edited["display_name"] = f"{sp} - {cu} {order_type}模板"
        self.storage.save_template(fn, edited)
        QMessageBox.information(self, "已保存", f"已保存为：{fn}")
        self._reload_list()

    def _save_as_personal(self):
        fn = self._current_filename()
        if not fn:
            QMessageBox.information(self, "提示", "请先选择一个模板")
            return
        tpl = self.storage.load_template(fn)
        if not tpl:
            return
        order_type = "外贸" if tpl.get("type") == "export" else "内贸"
        items = [it["name"] for it in self.storage.load_salespersons()]
        if not items:
            QMessageBox.information(self, "提示", "请先到首页或单笔创建页新增业务员")
            return
        sp, ok = QInputDialog.getItem(self, "选择业务员", "业务员：", items, 0, True)
        if not ok or not sp.strip():
            return
        new_fn = self.storage.salesperson_template_filename(sp.strip(), order_type)
        tpl["display_name"] = f"{sp.strip()} - 个人{order_type}模板"
        self.storage.save_template(new_fn, tpl)
        QMessageBox.information(self, "成功", f"已另存为：{new_fn}")
        self._reload_list()

    def _save_as_customer(self):
        fn = self._current_filename()
        if not fn:
            QMessageBox.information(self, "提示", "请先选择一个模板")
            return
        tpl = self.storage.load_template(fn)
        if not tpl:
            return
        order_type = "外贸" if tpl.get("type") == "export" else "内贸"
        items = [it["name"] for it in self.storage.load_salespersons()]
        if not items:
            QMessageBox.information(self, "提示", "请先新增业务员")
            return
        sp, ok = QInputDialog.getItem(self, "选择业务员", "业务员：", items, 0, True)
        if not ok or not sp.strip():
            return
        customers = self.storage.get_customers(sp.strip())
        cu, ok = QInputDialog.getItem(self, "选择客户", "客户：",
                                      customers, 0, True)
        if not ok or not cu.strip():
            return
        new_fn = self.storage.customer_template_filename(sp.strip(), cu.strip(), order_type)
        tpl["display_name"] = f"{sp.strip()} - {cu.strip()} {order_type}模板"
        self.storage.save_template(new_fn, tpl)
        QMessageBox.information(self, "成功", f"已另存为：{new_fn}")
        self._reload_list()

    def _delete_template(self):
        fn = self._current_filename()
        if not fn:
            return
        if fn.startswith("standard_"):
            QMessageBox.information(self, "提示", "公司标准模板不可删除")
            return
        r = QMessageBox.question(self, "确认", f"确定删除模板：{fn} 吗？")
        if r != QMessageBox.Yes:
            return
        if self.storage.delete_template(fn):
            QMessageBox.information(self, "已删除", fn)
            self._reload_list()

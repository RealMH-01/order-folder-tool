# -*- coding: utf-8 -*-
"""单笔创建页"""

import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout, QWidget
)

from ..core import folder_builder
from ..dialogs.template_preview import TemplatePreviewDialog
from ..dialogs.scan_preview import ScanPreviewDialog


class SinglePage(QWidget):
    request_back = pyqtSignal()

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._current_template = None  # 当前使用的模板 dict
        self._current_template_name = ""
        self._build_ui()

    # ============== UI ==============
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        # 顶部栏
        top = QHBoxLayout()
        btn_back = QPushButton("← 返回首页")
        btn_back.setObjectName("SecondaryButton")
        btn_back.clicked.connect(self.request_back.emit)
        top.addWidget(btn_back)
        title = QLabel("单笔创建")
        title.setObjectName("TitleLabel")
        top.addWidget(title)
        top.addStretch(1)
        btn_help = QPushButton("命名变量说明")
        btn_help.setObjectName("LinkButton")
        btn_help.clicked.connect(self._show_naming_help)
        top.addWidget(btn_help)
        root.addLayout(top)

        # ----- 身份与模板选择区 -----
        id_group = QGroupBox("① 身份与模板选择")
        id_layout = QGridLayout(id_group)
        id_layout.setHorizontalSpacing(8)
        id_layout.setVerticalSpacing(8)
        # 网格列宽自适应：业务员/订单类型列、客户/模板列更宽，产品类别较窄
        id_layout.setColumnStretch(1, 2)
        id_layout.setColumnStretch(3, 2)
        id_layout.setColumnStretch(5, 1)

        # 第 0 行：业务员 / 客户
        id_layout.addWidget(QLabel("业务员："), 0, 0)
        self.cmb_sales = QComboBox()
        self.cmb_sales.setEditable(False)
        self.cmb_sales.currentIndexChanged.connect(self._on_sales_changed)
        btn_add_sales = QPushButton("+")
        btn_add_sales.setFixedWidth(28)
        btn_add_sales.clicked.connect(self._add_salesperson)
        id_layout.addWidget(self.cmb_sales, 0, 1)
        id_layout.addWidget(btn_add_sales, 0, 2)

        id_layout.addWidget(QLabel("客户："), 0, 3)
        self.cmb_customer = QComboBox()
        self.cmb_customer.currentIndexChanged.connect(self._on_customer_changed)
        btn_add_customer = QPushButton("+")
        btn_add_customer.setFixedWidth(28)
        btn_add_customer.clicked.connect(self._add_customer)
        id_layout.addWidget(self.cmb_customer, 0, 4)
        id_layout.addWidget(btn_add_customer, 0, 5)

        # 第 1 行：订单类型 | 模板 | 产品类别 | 预览模板
        # （订单类型从②移上来，放在模板左边，切换后模板自动刷新）
        id_layout.addWidget(QLabel("订单类型："), 1, 0)
        self.cmb_order_type = QComboBox()
        self.cmb_order_type.addItems(["外贸", "内贸"])
        self.cmb_order_type.currentIndexChanged.connect(self._on_order_type_changed)
        id_layout.addWidget(self.cmb_order_type, 1, 1)

        id_layout.addWidget(QLabel("模板："), 1, 2)
        self.cmb_template = QComboBox()
        self.cmb_template.currentIndexChanged.connect(self._on_template_changed)
        id_layout.addWidget(self.cmb_template, 1, 3)

        id_layout.addWidget(QLabel("产品类别："), 1, 4)
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["戊二醛", "其他产品"])
        id_layout.addWidget(self.cmb_category, 1, 5)

        btn_preview = QPushButton("预览模板")
        btn_preview.setObjectName("SecondaryButton")
        btn_preview.clicked.connect(self._preview_template)
        id_layout.addWidget(btn_preview, 2, 5)

        root.addWidget(id_group)

        # ----- 订单信息表单 -----
        order_group = QGroupBox("② 订单信息")
        form = QGridLayout(order_group)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        form.addWidget(QLabel("订单号*："), 0, 0)
        self.edit_order_no = QLineEdit()
        self.edit_order_no.setPlaceholderText("例如 XS-GAM2508056NH")
        form.addWidget(self.edit_order_no, 0, 1, 1, 3)

        form.addWidget(QLabel("客户名称*："), 1, 0)
        self.edit_customer = QLineEdit()
        self.edit_customer.setPlaceholderText("由客户下拉自动填充，可修改")
        form.addWidget(self.edit_customer, 1, 1, 1, 3)

        form.addWidget(QLabel("产品信息："), 2, 0)
        self.edit_product_info = QLineEdit()
        self.edit_product_info.setPlaceholderText("选填")
        form.addWidget(self.edit_product_info, 2, 1, 1, 3)

        form.addWidget(QLabel("客户PO号："), 3, 0)
        self.edit_po = QLineEdit()
        self.edit_po.setPlaceholderText("选填（会替换文件名中的 <客户PO号>）")
        form.addWidget(self.edit_po, 3, 1, 1, 3)

        self.chk_inspection = QCheckBox("需要商检资料（勾选后创建商检资料子文件夹）")
        form.addWidget(self.chk_inspection, 4, 1, 1, 3)

        root.addWidget(order_group)

        # ----- 操作按钮 -----
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        btn_reset = QPushButton("重置")
        btn_reset.setObjectName("SecondaryButton")
        btn_reset.clicked.connect(self._reset_form)
        self.btn_next = QPushButton("下一步：扫描并预览 →")
        self.btn_next.setStyleSheet("font-size:14px; font-weight:bold; padding:8px 24px;")
        self.btn_next.clicked.connect(self._scan_and_preview)
        bottom.addWidget(btn_reset)
        bottom.addWidget(self.btn_next)
        root.addLayout(bottom)

        root.addStretch(1)

    # ============== 外部入口 ==============
    def refresh(self):
        """切换到本页时调用"""
        self._load_salespersons()
        self._on_order_type_changed()

    # ============== 数据加载 ==============
    def _load_salespersons(self):
        cur = self.cmb_sales.currentText()
        self.cmb_sales.blockSignals(True)
        self.cmb_sales.clear()
        items = self.storage.load_salespersons()
        names = [it["name"] for it in items]
        self.cmb_sales.addItems(names)
        # 恢复上次选择
        cfg = self.storage.load_config()
        last = cfg.get("last_salesperson") or cur
        if last in names:
            self.cmb_sales.setCurrentText(last)
        self.cmb_sales.blockSignals(False)
        self._on_sales_changed()

    def _load_customers(self):
        cur = self.cmb_customer.currentText()
        sales = self.cmb_sales.currentText()
        self.cmb_customer.blockSignals(True)
        self.cmb_customer.clear()
        customers = self.storage.get_customers(sales) if sales else []
        self.cmb_customer.addItems(customers)
        cfg = self.storage.load_config()
        last = cfg.get("last_customer") or cur
        if last in customers:
            self.cmb_customer.setCurrentText(last)
        elif customers:
            self.cmb_customer.setCurrentIndex(0)
        self.cmb_customer.blockSignals(False)
        self._on_customer_changed()

    def _reload_templates(self):
        """根据当前业务员+客户+订单类型匹配可选模板"""
        sales = self.cmb_sales.currentText()
        customer = self.cmb_customer.currentText()
        order_type = self.cmb_order_type.currentText()
        self.cmb_template.blockSignals(True)
        self.cmb_template.clear()

        # 候选：客户专属 → 个人 → 标准（都列出，便于手动切换）
        options = []
        if sales and customer:
            fn = self.storage.customer_template_filename(sales, customer, order_type)
            t = self.storage.load_template(fn)
            if t:
                options.append((f"[客户专属] {sales}-{customer} · {order_type}", fn, t))
        if sales:
            fn = self.storage.salesperson_template_filename(sales, order_type)
            t = self.storage.load_template(fn)
            if t:
                options.append((f"[业务员个人] {sales} · {order_type}", fn, t))
        fn = self.storage.standard_template_filename(order_type)
        t = self.storage.load_template(fn)
        if t:
            options.append((f"[公司标准] {order_type}", fn, t))

        self._tpl_options = options
        for label, _, _ in options:
            self.cmb_template.addItem(label)
        self.cmb_template.blockSignals(False)
        if options:
            self.cmb_template.setCurrentIndex(0)
        self._on_template_changed()

    # ============== 事件 ==============
    def _on_sales_changed(self):
        self._load_customers()
        self._reload_templates()

    def _on_customer_changed(self):
        name = self.cmb_customer.currentText()
        self.edit_customer.setText(name)
        self._reload_templates()

    def _on_order_type_changed(self):
        # 外贸才显示商检（chk_inspection 可能在构造早期尚未创建，需判空）
        is_export = self.cmb_order_type.currentText() == "外贸"
        if hasattr(self, "chk_inspection") and self.chk_inspection is not None:
            self.chk_inspection.setVisible(is_export)
            if not is_export:
                self.chk_inspection.setChecked(False)
        # cmb_template 在后续代码才创建；如已存在则刷新
        if hasattr(self, "cmb_template") and self.cmb_template is not None:
            self._reload_templates()

    def _on_template_changed(self):
        idx = self.cmb_template.currentIndex()
        if idx < 0 or idx >= len(getattr(self, "_tpl_options", [])):
            self._current_template = None
            self._current_template_name = ""
            return
        _, fn, t = self._tpl_options[idx]
        self._current_template_name = fn
        self._current_template = t

    def _add_salesperson(self):
        name, ok = QInputDialog.getText(self, "新增业务员", "业务员姓名：")
        if ok and name.strip():
            if self.storage.add_salesperson(name.strip()):
                self._load_salespersons()
                self.cmb_sales.setCurrentText(name.strip())
            else:
                QMessageBox.information(self, "提示", "该业务员已存在")

    def _add_customer(self):
        sales = self.cmb_sales.currentText()
        if not sales:
            QMessageBox.warning(self, "提示", "请先选择或新增业务员")
            return
        name, ok = QInputDialog.getText(self, "新增客户",
                                        f"在业务员「{sales}」下新增客户：")
        if ok and name.strip():
            if self.storage.add_customer(sales, name.strip()):
                self._load_customers()
                self.cmb_customer.setCurrentText(name.strip())
            else:
                QMessageBox.information(self, "提示", "该客户已存在")

    def _preview_template(self):
        if not self._current_template:
            QMessageBox.information(self, "提示", "当前没有可预览的模板")
            return
        dlg = TemplatePreviewDialog(
            self._current_template,
            title=f"预览模板 - {self.cmb_template.currentText()}",
            parent=self)
        dlg.exec_()

    def _reset_form(self):
        self.edit_order_no.clear()
        self.edit_product_info.clear()
        self.edit_po.clear()
        self.chk_inspection.setChecked(False)

    # ============== 核心动作 ==============
    def _collect_order(self):
        order_type = self.cmb_order_type.currentText()
        order_no = self.edit_order_no.text().strip()
        customer = self.edit_customer.text().strip()
        if not order_no:
            QMessageBox.warning(self, "提示", "请填写订单号")
            return None
        if not customer:
            QMessageBox.warning(self, "提示", "请填写客户名称")
            return None
        return {
            "order_type": order_type,
            "order_no": order_no,
            "customer": customer,
            "product_info": self.edit_product_info.text().strip(),
            "po_no": self.edit_po.text().strip(),
            "product_category": self.cmb_category.currentText(),
            "salesperson": self.cmb_sales.currentText(),
            "needs_inspection": self.chk_inspection.isChecked() and order_type == "外贸",
        }

    def _scan_and_preview(self):
        if not self._current_template:
            QMessageBox.warning(self, "提示", "未找到可用模板，请到「模板管理」检查")
            return
        order = self._collect_order()
        if not order:
            return

        # 目标路径：<根目录>/1订单/<业务员rel_path>/[<mid_layer>/]<客户名>/
        base_path = self.storage.build_customer_dir(
            order["salesperson"], order["customer"])
        if not base_path:
            QMessageBox.warning(self, "提示", "未能构造目标路径，请先设置根目录")
            return

        # 展开
        ctx = folder_builder.build_context(order)
        template_folders = folder_builder.flatten_template_folders(
            self._current_template, base_path, ctx, order["needs_inspection"]
        )
        template_folders, extras = folder_builder.compare_with_existing(
            base_path, template_folders)

        # 预览对话框展示的是"订单号文件夹"路径（包含订单号），
        # 但允许用户修改。修改后会被视为新的"客户目录"基路径。
        order_folder_preview = os.path.join(base_path, order["order_no"])
        dlg = ScanPreviewDialog(order_folder_preview, template_folders, extras,
                                parent=self)
        if dlg.exec_() != dlg.Accepted:
            return
        final_order_folder = dlg.get_target_path() or order_folder_preview

        # 如果用户修改了路径，需重新展开&对比
        if final_order_folder != order_folder_preview:
            # 将"订单号文件夹"路径还原为"客户目录"
            base_path = os.path.dirname(final_order_folder.rstrip("/\\"))
            template_folders = folder_builder.flatten_template_folders(
                self._current_template, base_path, ctx, order["needs_inspection"]
            )
            template_folders, extras = folder_builder.compare_with_existing(
                base_path, template_folders)

        # 执行
        cfg = self.storage.load_config()
        result = folder_builder.execute_build(
            order=order,
            template=self._current_template,
            base_path=base_path,
            template_files_dir=cfg.get("template_files_dir") or None,
        )

        # 保存"上次选择"
        self.storage.update_config(
            last_salesperson=order["salesperson"],
            last_customer=order["customer"],
            last_order_type=order["order_type"],
            last_product_category=order["product_category"],
        )

        # 写历史
        self._append_history(order, result)

        # 展示结果（使用订单号文件夹路径作为"打开"入口）
        self._show_result(order, result["base_path"], result)

    def _append_history(self, order, result):
        cfg = self.storage.load_config()
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": cfg.get("operator", ""),
            "salesperson": order["salesperson"],
            "customer": order["customer"],
            "order_no": order["order_no"],
            "order_type": order["order_type"],
            "product_category": order["product_category"],
            "template_name": self._current_template_name,
            "path": result["base_path"],
            "result": "成功" if result["created"] or result["skipped"] else "无变化",
            "created_count": len(result["created"]),
            "skipped_count": len(result["skipped"]),
            "copied_count": sum(1 for r in result["copy_results"] if r.get("copied")),
        }
        self.storage.append_history(record)

    def _show_result(self, order, base_path, result):
        from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QPushButton, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("创建完成")
        dlg.resize(720, 540)
        v = QVBoxLayout(dlg)

        lbl = QLabel(f"<b>订单号：</b>{order['order_no']} &nbsp; <b>路径：</b>{base_path}")
        v.addWidget(lbl)

        text = QPlainTextEdit()
        text.setReadOnly(True)
        lines = []
        lines.append(f"✅ 新建文件夹 {len(result['created'])} 个：")
        for p in result["created"]:
            lines.append(f"   + {p}")
        if result["skipped"]:
            lines.append(f"\n⏩ 跳过已存在文件夹 {len(result['skipped'])} 个：")
            for p in result["skipped"]:
                lines.append(f"   · {p}")
        lines.append("")
        copied = [r for r in result["copy_results"] if r.get("copied")]
        failed = [r for r in result["copy_results"] if not r.get("copied")]
        lines.append(f"📄 复制模板文件 {len(copied)} 个：")
        for r in copied:
            lines.append(f"   + {os.path.basename(r['dst'])}  ← {r['src']}")
        if failed:
            lines.append(f"\n⚠ 未复制的模板文件 {len(failed)} 个：")
            for r in failed:
                lines.append(f"   · {r['src']}   原因：{r['reason']}")
        lines.append("")
        lines.append(f"📊 已生成文件清单：{result['checklist_path']}")
        text.setPlainText("\n".join(lines))
        v.addWidget(text)

        h = QHBoxLayout()
        btn_open = QPushButton("打开订单文件夹")
        btn_open.clicked.connect(lambda: self._open_path(base_path))
        btn_close = QPushButton("关闭")
        btn_close.setObjectName("SecondaryButton")
        btn_close.clicked.connect(dlg.accept)
        h.addStretch(1)
        h.addWidget(btn_open)
        h.addWidget(btn_close)
        v.addLayout(h)
        dlg.exec_()

    def _open_path(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            elif os.name == "posix":
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "提示", f"无法打开文件夹：{e}")

    def _show_naming_help(self):
        msg = (
            "可用的命名占位符：\n"
            "  <订单号>    —— 表单中填写的订单号\n"
            "  <客户名称>  —— 表单中填写的客户名称\n"
            "  <客户PO号>  —— 客户PO号（如有）\n"
            "  <产品信息>  —— 产品信息（如有）\n"
            "  <业务员>    —— 当前选择的业务员姓名\n"
            "  <日期>      —— 创建当天日期 YYYYMMDD\n"
            "  <SHXY编号>  —— 自动占位，需要时手动修改\n\n"
            "在【模板管理】中可以自由编辑每个文件的 filename 字段，\n"
            "例如：CI-<订单号>-<客户名称>.xlsx\n\n"
            "file_template 中的 [产地] 标记会根据「产品类别」自动替换：\n"
            "  • 戊二醛   → 宁夏\n"
            "  • 其他产品 → 湖北天鹅"
        )
        QMessageBox.information(self, "命名变量说明", msg)

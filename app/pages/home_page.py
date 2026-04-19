# -*- coding: utf-8 -*-
"""启动页（首页）"""

import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
)


class HomePage(QWidget):
    """启动页：设置根目录、模板目录、选择功能"""

    # 信号
    request_single = pyqtSignal()
    request_batch = pyqtSignal()
    request_templates = pyqtSignal()
    request_history = pyqtSignal()
    request_help = pyqtSignal()
    salespersons_changed = pyqtSignal()
    root_dir_changed = pyqtSignal(str)
    template_dir_changed = pyqtSignal(str)

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._build_ui()
        self._load_initial()

    # -------- UI 构建 --------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        # 标题
        title = QLabel("订单文件夹自动创建工具")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("一键生成标准订单目录结构 · 自动复制模板文件 · 生成文件清单")
        subtitle.setObjectName("SubTitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 配置区
        config_frame = QFrame()
        config_frame.setStyleSheet(
            "QFrame{background:#FFFFFF;border:1px solid #D0D7DE;border-radius:10px;}"
        )
        cfg_layout = QGridLayout(config_frame)
        cfg_layout.setContentsMargins(20, 20, 20, 20)
        cfg_layout.setHorizontalSpacing(10)
        cfg_layout.setVerticalSpacing(12)

        # 根目录
        lbl1 = QLabel("公司资料根目录：")
        lbl1.setObjectName("SectionLabel")
        self.root_edit = QLineEdit()
        self.root_edit.setPlaceholderText("请设置公司资料存放的根目录（必填）")
        self.root_edit.setReadOnly(False)
        btn_browse_root = QPushButton("浏览…")
        btn_browse_root.clicked.connect(self._browse_root)
        btn_save_root = QPushButton("保存")
        btn_save_root.setObjectName("SecondaryButton")
        btn_save_root.clicked.connect(self._save_root)

        cfg_layout.addWidget(lbl1, 0, 0)
        cfg_layout.addWidget(self.root_edit, 0, 1)
        cfg_layout.addWidget(btn_browse_root, 0, 2)
        cfg_layout.addWidget(btn_save_root, 0, 3)

        # 模板目录
        lbl2 = QLabel("模板文件目录：")
        lbl2.setObjectName("SectionLabel")
        self.tpl_edit = QLineEdit()
        self.tpl_edit.setPlaceholderText("存放通用 / 外贸通用 / 宁夏 / 湖北天鹅 模板文件的目录（可选）")
        btn_browse_tpl = QPushButton("浏览…")
        btn_browse_tpl.clicked.connect(self._browse_tpl)
        btn_save_tpl = QPushButton("保存")
        btn_save_tpl.setObjectName("SecondaryButton")
        btn_save_tpl.clicked.connect(self._save_tpl)

        cfg_layout.addWidget(lbl2, 1, 0)
        cfg_layout.addWidget(self.tpl_edit, 1, 1)
        cfg_layout.addWidget(btn_browse_tpl, 1, 2)
        cfg_layout.addWidget(btn_save_tpl, 1, 3)

        tip = QLabel("提示：模板目录结构请参考 README，如：\n  通用/CG.xlsx   外贸通用/CI.xlsx   宁夏/宁夏外贸生产.doc   湖北天鹅/湖北天鹅外贸生产.xlsx")
        tip.setStyleSheet("color:#666666;")
        cfg_layout.addWidget(tip, 2, 1, 1, 3)

        layout.addWidget(config_frame)

        # 模式选择区
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(30)
        mode_layout.setAlignment(Qt.AlignCenter)

        self.btn_single = QPushButton("📝 单笔创建")
        self.btn_single.setObjectName("BigButton")
        self.btn_single.clicked.connect(self._click_single)

        self.btn_batch = QPushButton("📦 批量导入")
        self.btn_batch.setObjectName("BigButton")
        self.btn_batch.clicked.connect(self._click_batch)

        mode_layout.addStretch(1)
        mode_layout.addWidget(self.btn_single)
        mode_layout.addWidget(self.btn_batch)
        mode_layout.addStretch(1)
        layout.addLayout(mode_layout)

        # 分隔线：大按钮 ↑ 小按钮 ↓
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color:#D0D7DE;")
        layout.addWidget(divider)
        layout.addSpacing(4)

        # 底部小按钮
        bottom = QHBoxLayout()
        bottom.setAlignment(Qt.AlignCenter)

        self.btn_scan = QPushButton("🧭 扫描导入业务员")
        self.btn_scan.setObjectName("SecondaryButton")
        self.btn_scan.clicked.connect(self._click_scan_import)

        self.btn_cleanup = QPushButton("🧹 整理已有订单文件夹")
        self.btn_cleanup.setObjectName("SecondaryButton")
        self.btn_cleanup.clicked.connect(self._click_cleanup)

        self.btn_templates = QPushButton("🗂 模板管理")
        self.btn_templates.setObjectName("SecondaryButton")
        self.btn_templates.clicked.connect(self.request_templates.emit)

        self.btn_history = QPushButton("🕘 历史记录")
        self.btn_history.setObjectName("SecondaryButton")
        self.btn_history.clicked.connect(self.request_history.emit)

        self.btn_help = QPushButton("❓ 使用帮助")
        self.btn_help.setObjectName("SecondaryButton")
        self.btn_help.clicked.connect(self.request_help.emit)

        # 底部按钮等宽整齐
        for _b in (self.btn_scan, self.btn_cleanup, self.btn_templates,
                   self.btn_history, self.btn_help):
            _b.setMinimumWidth(140)
            _b.setFixedHeight(36)

        bottom.addStretch(1)
        bottom.addWidget(self.btn_scan)
        bottom.addSpacing(12)
        bottom.addWidget(self.btn_cleanup)
        bottom.addSpacing(12)
        bottom.addWidget(self.btn_templates)
        bottom.addSpacing(12)
        bottom.addWidget(self.btn_history)
        bottom.addSpacing(12)
        bottom.addWidget(self.btn_help)
        bottom.addStretch(1)
        layout.addLayout(bottom)

        layout.addStretch(1)

    # -------- 数据加载 --------
    def _load_initial(self):
        if self.storage.root_dir:
            self.root_edit.setText(self.storage.root_dir)
            cfg = self.storage.load_config()
            self.tpl_edit.setText(cfg.get("template_files_dir", ""))
        self._refresh_mode_buttons_enabled()

    def refresh(self):
        """外部切换回本页时调用"""
        self._load_initial()

    # -------- 事件 --------
    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "选择公司资料根目录",
                                             self.root_edit.text() or "")
        if d:
            self.root_edit.setText(d)

    def _browse_tpl(self):
        d = QFileDialog.getExistingDirectory(self, "选择模板文件目录",
                                             self.tpl_edit.text() or "")
        if d:
            self.tpl_edit.setText(d)

    def _save_root(self):
        root = self.root_edit.text().strip()
        if not root:
            QMessageBox.warning(self, "提示", "请先选择根目录")
            return
        import os
        if not os.path.isdir(root):
            try:
                os.makedirs(root, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "提示", f"目录不存在且创建失败：{e}")
                return
        self.storage.set_root_dir(root)
        # 同步保存到 bootstrap
        from ..core.storage import save_bootstrap, load_bootstrap
        bs = load_bootstrap()
        bs["last_root"] = root
        save_bootstrap(bs)
        self.root_dir_changed.emit(root)
        # 如果之前有模板目录设置，保持
        cfg = self.storage.load_config()
        if self.tpl_edit.text().strip():
            cfg["template_files_dir"] = self.tpl_edit.text().strip()
            self.storage.save_config(cfg)
        else:
            self.tpl_edit.setText(cfg.get("template_files_dir", ""))
        self._refresh_mode_buttons_enabled()
        QMessageBox.information(self, "成功", "根目录已保存。")

    def _save_tpl(self):
        if not self.storage.root_dir:
            QMessageBox.warning(self, "提示", "请先设置根目录")
            return
        tpl = self.tpl_edit.text().strip()
        self.storage.update_config(template_files_dir=tpl)
        self.template_dir_changed.emit(tpl)
        QMessageBox.information(self, "成功",
                                "模板文件目录已保存。" if tpl else "已清空模板文件目录（将跳过模板文件复制）。")

    def _click_single(self):
        if not self._check_root():
            return
        self._auto_save_root_if_needed()
        self.request_single.emit()

    def _click_batch(self):
        if not self._check_root():
            return
        self._auto_save_root_if_needed()
        self.request_batch.emit()

    def _click_scan_import(self):
        if not self._check_root():
            return
        self._auto_save_root_if_needed()
        from ..dialogs.scan_import import ScanImportDialog
        dlg = ScanImportDialog(self.storage, parent=self)
        if dlg.exec_() != dlg.Accepted:
            return
        rel_paths = dlg.get_selected_rel_paths()
        if not rel_paths:
            return
        # 询问是否覆盖已有同名业务员
        overwrite = False
        existing_names = {it["name"] for it in self.storage.load_salespersons()}
        about_to_overlap = [p.split("/")[-1] for p in rel_paths
                            if p.split("/")[-1] in existing_names]
        if about_to_overlap:
            ret = QMessageBox.question(
                self, "已存在的业务员",
                "以下业务员已存在，是否用扫描结果<b>合并/更新</b>它们的"
                "路径和客户列表？<br/><br/>"
                + "、".join(about_to_overlap[:10])
                + ("…" if len(about_to_overlap) > 10 else ""),
                QMessageBox.Yes | QMessageBox.No,
            )
            overwrite = (ret == QMessageBox.Yes)
        summary = self.storage.import_scanned_salespersons(
            rel_paths, overwrite=overwrite
        )
        self.salespersons_changed.emit()
        QMessageBox.information(
            self, "导入完成",
            f"新增业务员：{len(summary['added'])} 名\n"
            f"更新业务员：{len(summary['updated'])} 名\n"
            f"跳过（已存在且未覆盖）：{len(summary['skipped'])} 名"
        )

    def _check_root(self) -> bool:
        if not self.storage.root_dir:
            QMessageBox.warning(self, "提示", "请先设置并保存根目录")
            return False
        return True

    def _auto_save_root_if_needed(self):
        """如果输入框中根目录和当前不一致，自动保存"""
        cur = self.root_edit.text().strip()
        if cur and cur != self.storage.root_dir:
            self._save_root()

    def _refresh_mode_buttons_enabled(self):
        ok = bool(self.storage.root_dir)
        self.btn_single.setEnabled(ok)
        self.btn_batch.setEnabled(ok)
        self.btn_scan.setEnabled(ok)
        self.btn_cleanup.setEnabled(ok)
        self.btn_templates.setEnabled(ok)
        self.btn_history.setEnabled(ok)
        # 帮助页面不需要根目录，始终可点
        self.btn_help.setEnabled(True)

    # -------- 整理已有订单文件夹（功能 D） --------
    def _click_cleanup(self):
        if not self._check_root():
            return
        self._auto_save_root_if_needed()

        from PyQt5.QtWidgets import (
            QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
            QPushButton
        )
        from ..core import folder_builder
        from ..dialogs.folder_cleanup import FolderCleanupDialog

        dlg = QDialog(self)
        dlg.setWindowTitle("整理已有订单文件夹")
        dlg.resize(560, 320)
        form = QFormLayout(dlg)

        # 订单文件夹路径
        h_path = QHBoxLayout()
        edit_folder = QLineEdit()
        edit_folder.setPlaceholderText("选择要整理的订单文件夹…")
        btn_pick = QPushButton("浏览…")

        def _pick():
            d = QFileDialog.getExistingDirectory(
                dlg, "选择订单文件夹", edit_folder.text() or self.storage.root_dir or ""
            )
            if d:
                edit_folder.setText(d)
                # 自动根据文件夹名填订单号
                base = d.rstrip("/\\").split("/")[-1].split("\\")[-1]
                if base and not edit_order_no.text().strip():
                    edit_order_no.setText(base)
        btn_pick.clicked.connect(_pick)
        h_path.addWidget(edit_folder, 1)
        h_path.addWidget(btn_pick)
        w_path = QWidget()
        w_path.setLayout(h_path)
        form.addRow("订单文件夹：", w_path)

        # 订单号
        edit_order_no = QLineEdit()
        edit_order_no.setPlaceholderText("例如 XS-NEW001NH")
        form.addRow("订单号：", edit_order_no)

        # 客户名称
        edit_customer = QLineEdit()
        edit_customer.setPlaceholderText("用于替换 <客户名称> 占位符")
        form.addRow("客户名称：", edit_customer)

        # 模板选择
        cmb_template = QComboBox()
        tpl_list = self.storage.list_template_files()
        tpl_entries = []
        for fn in tpl_list.get("standard", []):
            tpl = self.storage.load_template(fn)
            if tpl:
                tpl_entries.append((f"[标准] {tpl.get('display_name', fn)}", fn))
        for fn in tpl_list.get("salesperson", []):
            tpl = self.storage.load_template(fn)
            if tpl:
                tpl_entries.append((f"[业务员] {tpl.get('display_name', fn)}", fn))
        for fn in tpl_list.get("customer", []):
            tpl = self.storage.load_template(fn)
            if tpl:
                tpl_entries.append((f"[客户] {tpl.get('display_name', fn)}", fn))
        for label, _ in tpl_entries:
            cmb_template.addItem(label)
        form.addRow("使用模板：", cmb_template)

        # 产品类别
        cmb_cat = QComboBox()
        cmb_cat.addItems(["戊二醛", "其他产品"])
        form.addRow("产品类别：", cmb_cat)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        form.addRow(btns)

        if dlg.exec_() != dlg.Accepted:
            return

        order_folder = edit_folder.text().strip()
        order_no = edit_order_no.text().strip()
        customer = edit_customer.text().strip()
        idx = cmb_template.currentIndex()

        if not order_folder or not os.path.isdir(order_folder):
            QMessageBox.warning(self, "提示", "请选择一个存在的订单文件夹")
            return
        if not order_no:
            QMessageBox.warning(self, "提示", "请填写订单号")
            return
        if idx < 0 or idx >= len(tpl_entries):
            QMessageBox.warning(self, "提示", "请选择一个模板")
            return

        tpl_fn = tpl_entries[idx][1]
        template = self.storage.load_template(tpl_fn)
        if not template:
            QMessageBox.warning(self, "提示", f"模板 {tpl_fn} 读取失败")
            return

        order = {
            "order_no": order_no,
            "customer": customer,
            "product_info": "",
            "po_no": "",
            "product_category": cmb_cat.currentText(),
            "salesperson": "",
            "needs_inspection": False,
            "order_type": "外贸" if template.get("type") == "export" else "内贸",
        }
        ctx = folder_builder.build_context(order)

        FolderCleanupDialog(
            order_folder_path=order_folder,
            order_no=order_no,
            template=template,
            ctx=ctx,
            parent=self,
            product_category=order["product_category"],
            needs_inspection=False,
        ).exec_()

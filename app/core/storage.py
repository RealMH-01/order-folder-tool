# -*- coding: utf-8 -*-
"""
数据持久化层。

所有数据以 JSON 保存在 <根目录>/.order_tool/ 下：
- config.json          ：根目录、模板文件目录、上次选择
- salespersons.json    ：业务员及客户列表
- history.json         ：操作历史
- templates/*.json     ：模板文件（公司标准/业务员个人/业务员-客户）

特殊情况：在设置「根目录」之前，程序还没有地方放 .order_tool，这时
配置使用用户主目录下的 ~/.order_tool_bootstrap.json 作为引导，
里面只存「上次使用过的根目录」，设置好根目录后再把完整配置写到
<根目录>/.order_tool/config.json。
"""

import json
import os
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import default_templates

# ------------------------------------------------------------------
# 路径常量
# ------------------------------------------------------------------
BOOTSTRAP_FILE = Path.home() / ".order_tool_bootstrap.json"
DATA_DIR_NAME = ".order_tool"
TEMPLATES_DIR_NAME = "templates"

STANDARD_EXPORT_FILE = "standard_export.json"
STANDARD_DOMESTIC_FILE = "standard_domestic.json"


# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------
def _safe_read_json(path: Path, default: Any) -> Any:
    """读取 JSON 文件，读取失败返回 default"""
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return copy.deepcopy(default)


def _safe_write_json(path: Path, data: Any) -> None:
    """写入 JSON 文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------
# Bootstrap（仅记录"上次用过的根目录"）
# ------------------------------------------------------------------
def load_bootstrap() -> Dict[str, Any]:
    return _safe_read_json(BOOTSTRAP_FILE, {"last_root": ""})


def save_bootstrap(data: Dict[str, Any]) -> None:
    _safe_write_json(BOOTSTRAP_FILE, data)


# ------------------------------------------------------------------
# Storage 主类
# ------------------------------------------------------------------
class Storage:
    """统一封装所有数据的读写"""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir: str = root_dir or ""
        # 以下属性在 set_root_dir 后才可用
        self.data_dir: Optional[Path] = None
        self.templates_dir: Optional[Path] = None
        self.config_file: Optional[Path] = None
        self.salespersons_file: Optional[Path] = None
        self.history_file: Optional[Path] = None
        if root_dir:
            self.set_root_dir(root_dir)

    # -------- 根目录 --------
    def set_root_dir(self, root_dir: str) -> None:
        """设置根目录并初始化相关目录结构"""
        self.root_dir = root_dir
        root_path = Path(root_dir)
        self.data_dir = root_path / DATA_DIR_NAME
        self.templates_dir = self.data_dir / TEMPLATES_DIR_NAME
        self.config_file = self.data_dir / "config.json"
        self.salespersons_file = self.data_dir / "salespersons.json"
        self.history_file = self.data_dir / "history.json"

        # 创建目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # 如果标准模板不存在，写入默认模板
        export_path = self.templates_dir / STANDARD_EXPORT_FILE
        domestic_path = self.templates_dir / STANDARD_DOMESTIC_FILE
        if not export_path.exists():
            _safe_write_json(export_path, default_templates.STANDARD_EXPORT)
        if not domestic_path.exists():
            _safe_write_json(domestic_path, default_templates.STANDARD_DOMESTIC)

        # 其它文件初始化
        if not self.config_file.exists():
            _safe_write_json(self.config_file, {
                "root_dir": root_dir,
                "template_files_dir": "",
                "last_salesperson": "",
                "last_customer": "",
                "last_order_type": "外贸",
                "last_product_category": "戊二醛",
                "operator": os.environ.get("USERNAME") or os.environ.get("USER") or "",
            })
        else:
            # 更新 root_dir
            cfg = self.load_config()
            cfg["root_dir"] = root_dir
            self.save_config(cfg)

        if not self.salespersons_file.exists():
            _safe_write_json(self.salespersons_file, {"list": []})

        if not self.history_file.exists():
            _safe_write_json(self.history_file, {"records": []})

    # -------- config --------
    def load_config(self) -> Dict[str, Any]:
        if not self.config_file:
            return {}
        return _safe_read_json(self.config_file, {})

    def save_config(self, data: Dict[str, Any]) -> None:
        if not self.config_file:
            return
        _safe_write_json(self.config_file, data)

    def update_config(self, **kwargs) -> None:
        cfg = self.load_config()
        cfg.update(kwargs)
        self.save_config(cfg)

    # -------- 业务员 / 客户 --------
    def load_salespersons(self) -> List[Dict[str, Any]]:
        """返回 [{"name": "...", "rel_path": "...", "mid_layer": "...",
                  "customers": ["...", ...]}, ...]

        兼容旧格式（仅有 name 和 customers 的记录自动补全空字段）。
        """
        data = _safe_read_json(self.salespersons_file, {"list": []})
        items = data.get("list", [])
        changed = False
        for it in items:
            if "rel_path" not in it:
                it["rel_path"] = it.get("name", "")
                changed = True
            if "mid_layer" not in it:
                it["mid_layer"] = ""
                changed = True
            if "customers" not in it:
                it["customers"] = []
                changed = True
        if changed and self.salespersons_file:
            _safe_write_json(self.salespersons_file, {"list": items})
        return items

    def save_salespersons(self, items: List[Dict[str, Any]]) -> None:
        _safe_write_json(self.salespersons_file, {"list": items})

    def get_salesperson(self, name: str) -> Optional[Dict[str, Any]]:
        for it in self.load_salespersons():
            if it["name"] == name:
                return it
        return None

    def add_salesperson(self, name: str, rel_path: str = "",
                        mid_layer: str = "") -> bool:
        name = (name or "").strip()
        if not name:
            return False
        items = self.load_salespersons()
        for it in items:
            if it["name"] == name:
                return False
        items.append({
            "name": name,
            "rel_path": rel_path.strip() or name,
            "mid_layer": mid_layer.strip(),
            "customers": [],
        })
        self.save_salespersons(items)
        return True

    def update_salesperson(self, name: str, rel_path: Optional[str] = None,
                           mid_layer: Optional[str] = None,
                           customers: Optional[List[str]] = None) -> bool:
        items = self.load_salespersons()
        for it in items:
            if it["name"] == name:
                if rel_path is not None:
                    it["rel_path"] = rel_path
                if mid_layer is not None:
                    it["mid_layer"] = mid_layer
                if customers is not None:
                    it["customers"] = list(customers)
                self.save_salespersons(items)
                return True
        return False

    def add_customer(self, salesperson: str, customer: str) -> bool:
        customer = (customer or "").strip()
        if not salesperson or not customer:
            return False
        items = self.load_salespersons()
        for it in items:
            if it["name"] == salesperson:
                if customer in it["customers"]:
                    return False
                it["customers"].append(customer)
                self.save_salespersons(items)
                return True
        # 业务员不存在则同时创建
        items.append({
            "name": salesperson,
            "rel_path": salesperson,
            "mid_layer": "",
            "customers": [customer],
        })
        self.save_salespersons(items)
        return True

    def get_customers(self, salesperson: str) -> List[str]:
        for it in self.load_salespersons():
            if it["name"] == salesperson:
                return list(it["customers"])
        return []

    # -------- 订单路径拼接 --------
    ORDER_ROOT_FOLDER = "1订单"

    def build_customer_dir(self, salesperson: str, customer: str) -> str:
        """
        根据业务员+客户，计算客户目录绝对路径：
            <根目录>/1订单/<业务员rel_path>/[<mid_layer>/]<客户名>/
        订单号文件夹由 folder_builder 创建在此目录下。
        """
        if not self.root_dir:
            return ""
        parts = [self.root_dir, self.ORDER_ROOT_FOLDER]
        sp = self.get_salesperson(salesperson)
        if sp:
            rel = (sp.get("rel_path") or sp["name"]).strip()
            if rel:
                # 支持 rel_path 里含有 "/" 或 "\\"
                parts.append(rel.replace("\\", "/"))
            mid = (sp.get("mid_layer") or "").strip()
            if mid:
                parts.append(mid)
        else:
            # 未知业务员：直接用名字
            if salesperson:
                parts.append(salesperson)
        if customer:
            parts.append(customer)
        # 规整拼接：用 os.path.join
        path = parts[0]
        for p in parts[1:]:
            # 切分可能含有 "/" 的 rel_path
            for seg in p.split("/"):
                seg = seg.strip()
                if seg:
                    path = os.path.join(path, seg)
        return path

    # -------- 扫描导入 --------
    @staticmethod
    def _is_mid_layer_name(name: str) -> bool:
        """判断是否为"进行中的订单"中间层文件夹（同时含"进行"和"订单"）"""
        return "进行" in name and "订单" in name

    def scan_order_root(self) -> List[str]:
        """
        扫描 <根目录>/1订单/ 下的第一层文件夹（忽略文件、隐藏目录）。
        返回文件夹名列表。若 1订单 不存在，返回 []。
        """
        if not self.root_dir:
            return []
        order_root = Path(self.root_dir) / self.ORDER_ROOT_FOLDER
        if not order_root.exists() or not order_root.is_dir():
            return []
        return sorted([p.name for p in order_root.iterdir()
                       if p.is_dir() and not p.name.startswith(".")])

    def scan_subfolders(self, rel_under_order_root: str) -> List[str]:
        """
        扫描 <根目录>/1订单/<rel>/ 下的第一层子文件夹。
        """
        if not self.root_dir:
            return []
        p = Path(self.root_dir) / self.ORDER_ROOT_FOLDER
        if rel_under_order_root:
            for seg in rel_under_order_root.split("/"):
                if seg:
                    p = p / seg
        if not p.exists() or not p.is_dir():
            return []
        return sorted([x.name for x in p.iterdir()
                       if x.is_dir() and not x.name.startswith(".")])

    def scan_customers_for(self, rel_under_order_root: str) -> (str, List[str]):
        """
        扫描业务员文件夹下的客户。
        规则：
          1. 先看该业务员文件夹的第一层子文件夹；
          2. 如果其中有"同时包含'进行'和'订单'"的文件夹，则把它当作中间层，
             进入它，把它下面的第一层子文件夹作为客户；
          3. 否则第一层子文件夹本身就是客户。
        返回 (mid_layer, customers)
        """
        subs = self.scan_subfolders(rel_under_order_root)
        mid = ""
        for s in subs:
            if self._is_mid_layer_name(s):
                mid = s
                break
        if mid:
            customers = self.scan_subfolders(rel_under_order_root + "/" + mid)
        else:
            customers = subs
        return mid, customers

    def import_scanned_salespersons(self, rel_paths: List[str],
                                    overwrite: bool = False) -> Dict[str, Any]:
        """
        根据扫描勾选结果，导入业务员及其客户。

        rel_paths: 每个元素是相对 1订单/ 的路径，如 "张莹莹"、"湖北/文天堂"。
        业务员名取路径最后一段。
        overwrite: True 则覆盖已有同名业务员的 customers / rel_path / mid_layer。

        返回 {"added": [...], "updated": [...], "skipped": [...]}
        """
        items = self.load_salespersons()
        name_to_item = {it["name"]: it for it in items}

        added, updated, skipped = [], [], []
        for rel in rel_paths:
            rel = rel.strip().strip("/")
            if not rel:
                continue
            name = rel.split("/")[-1]
            mid, customers = self.scan_customers_for(rel)
            if name in name_to_item:
                if overwrite:
                    it = name_to_item[name]
                    it["rel_path"] = rel
                    it["mid_layer"] = mid
                    # 合并：保留已有 + 新增
                    existing = set(it.get("customers", []))
                    new_list = list(it.get("customers", []))
                    for c in customers:
                        if c not in existing:
                            new_list.append(c)
                            existing.add(c)
                    it["customers"] = new_list
                    updated.append(name)
                else:
                    skipped.append(name)
            else:
                items.append({
                    "name": name,
                    "rel_path": rel,
                    "mid_layer": mid,
                    "customers": list(customers),
                })
                name_to_item[name] = items[-1]
                added.append(name)

        self.save_salespersons(items)
        return {"added": added, "updated": updated, "skipped": skipped}

    # -------- 历史记录 --------
    def load_history(self) -> List[Dict[str, Any]]:
        data = _safe_read_json(self.history_file, {"records": []})
        return data.get("records", [])

    def save_history(self, records: List[Dict[str, Any]]) -> None:
        _safe_write_json(self.history_file, {"records": records})

    def append_history(self, record: Dict[str, Any]) -> None:
        records = self.load_history()
        records.insert(0, record)  # 最新的放前面
        # 最多保留 5000 条
        records = records[:5000]
        self.save_history(records)

    # -------- 模板 --------
    def list_template_files(self) -> Dict[str, List[str]]:
        """
        返回分组的模板文件名列表：
        {
            "standard": ["standard_export.json", "standard_domestic.json"],
            "salesperson": ["张三_default_export.json", ...],
            "customer": ["张三_ACME_export.json", ...],
        }
        """
        result = {"standard": [], "salesperson": [], "customer": []}
        if not self.templates_dir or not self.templates_dir.exists():
            return result
        for f in sorted(self.templates_dir.glob("*.json")):
            name = f.name
            if name.startswith("standard_"):
                result["standard"].append(name)
            else:
                base = name[:-5]  # 去掉 .json
                parts = base.split("_")
                # 业务员个人模板：<业务员>_default_<type>
                # 客户专属模板：<业务员>_<客户>_<type>
                if len(parts) >= 3 and parts[-2] == "default":
                    result["salesperson"].append(name)
                elif len(parts) >= 3:
                    result["customer"].append(name)
                else:
                    result["salesperson"].append(name)
        return result

    def load_template(self, filename: str) -> Optional[Dict[str, Any]]:
        if not self.templates_dir:
            return None
        p = self.templates_dir / filename
        if not p.exists():
            return None
        return _safe_read_json(p, None)

    def save_template(self, filename: str, data: Dict[str, Any]) -> None:
        if not self.templates_dir:
            return
        _safe_write_json(self.templates_dir / filename, data)

    def delete_template(self, filename: str) -> bool:
        if filename.startswith("standard_"):
            return False
        p = self.templates_dir / filename
        if p.exists():
            p.unlink()
            return True
        return False

    @staticmethod
    def standard_template_filename(order_type: str) -> str:
        return STANDARD_EXPORT_FILE if order_type == "外贸" else STANDARD_DOMESTIC_FILE

    @staticmethod
    def salesperson_template_filename(salesperson: str, order_type: str) -> str:
        t = "export" if order_type == "外贸" else "domestic"
        return f"{salesperson}_default_{t}.json"

    @staticmethod
    def customer_template_filename(salesperson: str, customer: str, order_type: str) -> str:
        t = "export" if order_type == "外贸" else "domestic"
        # 避免文件名中的非法字符
        safe_sp = _safe_filename(salesperson)
        safe_cu = _safe_filename(customer)
        return f"{safe_sp}_{safe_cu}_{t}.json"

    def match_template(self, salesperson: str, customer: str,
                       order_type: str) -> (str, Dict[str, Any]):
        """按优先级匹配模板，返回 (filename, template_dict)

        优先级：业务员-客户 > 业务员个人 > 标准
        """
        # 客户专属
        if salesperson and customer:
            fn = self.customer_template_filename(salesperson, customer, order_type)
            t = self.load_template(fn)
            if t:
                return fn, t
        # 业务员个人
        if salesperson:
            fn = self.salesperson_template_filename(salesperson, order_type)
            t = self.load_template(fn)
            if t:
                return fn, t
        # 标准
        fn = self.standard_template_filename(order_type)
        t = self.load_template(fn)
        return fn, t


def _safe_filename(s: str) -> str:
    """把文件名中的非法字符替换为下划线"""
    bad = '<>:"/\\|?*'
    out = []
    for ch in s:
        if ch in bad:
            out.append("_")
        else:
            out.append(ch)
    return "".join(out).strip() or "_"

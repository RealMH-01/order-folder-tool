# -*- coding: utf-8 -*-
"""
默认的标准外贸、内贸模板 JSON 定义。
程序首次启动时，若 .order_tool/templates/ 下缺少 standard_export.json /
standard_domestic.json，则使用本模块中的默认值生成。
"""

# 标准外贸模板
STANDARD_EXPORT = {
    "name": "<订单号>",
    "type": "export",
    "display_name": "公司标准模板 - 外贸",
    "children": [
        {
            "name": "SD",
            "children": [],
            "ref_files": [
                {"filename": "CI-<订单号>.xlsx", "source": "自制", "file_template": "外贸通用/CI.xlsx"},
                {"filename": "PL-<订单号>.xls", "source": "自制", "file_template": "外贸通用/PL.xls"},
                {"filename": "BL-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "COA-<订单号>.pdf", "source": "供应商提供或自制", "file_template": None},
                {"filename": "INS-<订单号>.pdf", "source": "保险公司", "file_template": None},
                {"filename": "FTA-<订单号>.pdf", "source": "商检局", "file_template": None},
                {"filename": "ETA-<订单号>.jpeg", "source": "船公司网站截图", "file_template": None},
                {"filename": "EXPORT DECLARATION.pdf", "source": "海关", "file_template": None},
                {"filename": "SD-<订单号>.zip", "source": "全部齐后打包", "file_template": None}
            ]
        },
        {
            "name": "报关资料",
            "children": [],
            "ref_files": [
                {"filename": "出口报关单录入底稿.xlsx", "source": "自制", "file_template": None},
                {"filename": "报关用CI.xlsx", "source": "自制", "file_template": None},
                {"filename": "报关用PL.xls", "source": "自制", "file_template": None},
                {"filename": "报关单校验单.jpg", "source": "报关行提供", "file_template": None}
            ]
        },
        {
            "name": "货代资料",
            "children": [
                {
                    "name": "唛头",
                    "children": [],
                    "ref_files": [
                        {"filename": "贴唛图.jpg", "source": "货代/自制", "file_template": None},
                        {"filename": "GHS Label.pdf", "source": "自制/客户提供", "file_template": None}
                    ]
                }
            ],
            "ref_files": [
                {"filename": "订舱托书-<订单号>.doc", "source": "自制", "file_template": "外贸通用/托书.doc"},
                {"filename": "配舱通知.doc", "source": "货代提供", "file_template": None},
                {"filename": "进仓通知.doc", "source": "货代提供", "file_template": None},
                {"filename": "提单确认.doc", "source": "货代提供", "file_template": None},
                {"filename": "电放保函.pdf", "source": "货代提供格式签字", "file_template": None},
                {"filename": "收款明细单.pdf", "source": "货代提供", "file_template": None},
                {"filename": "投保预览件.pdf", "source": "保险公司", "file_template": None},
                {"filename": "装箱单(码头联).doc", "source": "货代提供", "file_template": None},
                {"filename": "<SHXY编号>资料.rar", "source": "货代提供", "file_template": None}
            ]
        },
        {
            "name": "商检资料",
            "optional": True,
            "condition": "needs_inspection",
            "children": [],
            "ref_files": [
                {"filename": "采购合同(单章).pdf", "source": "自制", "file_template": None},
                {"filename": "销售合同.pdf", "source": "业务提供", "file_template": None},
                {"filename": "代理报检委托书.pdf", "source": "自制", "file_template": None},
                {"filename": "商检用商业发票.pdf", "source": "自制", "file_template": None},
                {"filename": "商检用装箱单.pdf", "source": "自制", "file_template": None},
                {"filename": "质量合格保证书.pdf", "source": "供应商提供", "file_template": None},
                {"filename": "危包证.pdf", "source": "工厂提供", "file_template": None},
                {"filename": "包装性能报告.pdf", "source": "工厂提供", "file_template": None},
                {"filename": "商检资料.zip", "source": "全部齐后打包", "file_template": None}
            ]
        },
        {
            "name": "生产发货",
            "children": [],
            "ref_files": [
                {"filename": "生产通知单-<订单号>", "source": "自制", "file_template": "[产地]外贸生产"},
                {"filename": "发货通知单-<订单号>", "source": "自制", "file_template": "[产地]外贸发货"},
                {"filename": "包装要求备忘.txt", "source": "自制", "file_template": None},
                {"filename": "已发货截图.png", "source": "物流截图", "file_template": None}
            ]
        },
        {
            "name": "装箱",
            "children": [],
            "ref_files": []
        },
        {
            "name": "船期",
            "children": [],
            "ref_files": [
                {"filename": "船期截图.jpeg", "source": "船公司网站截图", "file_template": None}
            ]
        },
        {
            "name": "证据链",
            "children": [],
            "ref_files": [
                {"filename": "1.销售合同-<订单号>.pdf", "source": "业务提供", "file_template": None},
                {"filename": "2.报关单(退税联)-<订单号>.pdf", "source": "海关", "file_template": None},
                {"filename": "3.CI-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "4.收费明细-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "5.海运费发票-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "6.港杂费发票-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "7.BL-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "8.PL-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "9.进仓通知-<订单号>.pdf", "source": "货代提供", "file_template": None},
                {"filename": "10.保单-<订单号>.pdf", "source": "保险公司", "file_template": None},
                {"filename": "11.到港截图-<订单号>.jpeg", "source": "船公司网站", "file_template": None},
                {"filename": "12.采购合同-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "13.采购发票-<订单号>.pdf", "source": "供应商提供", "file_template": None},
                {"filename": "14.收货回执-<订单号>.png", "source": "客户签收回传", "file_template": None},
                {"filename": "15.收款凭证-<订单号>.pdf", "source": "银行水单", "file_template": None}
            ]
        }
    ],
    "ref_files": [
        {"filename": "PI-<订单号>.pdf", "source": "业务提供", "file_template": None},
        {"filename": "SC-<订单号>.pdf", "source": "业务提供", "file_template": None},
        {"filename": "PO-<客户PO号>.pdf", "source": "客户提供", "file_template": None},
        {"filename": "CG-<订单号>.xlsx", "source": "自制", "file_template": "通用/CG.xlsx"},
        {"filename": "COA-<订单号>.doc", "source": "供应商提供或自制", "file_template": None},
        {"filename": "退税联-<订单号>.pdf", "source": "海关", "file_template": None}
    ]
}

# 标准内贸模板
STANDARD_DOMESTIC = {
    "name": "<订单号>",
    "type": "domestic",
    "display_name": "公司标准模板 - 内贸",
    "children": [
        {
            "name": "SD",
            "children": [],
            "ref_files": [
                {"filename": "送货单-<订单号>.pdf", "source": "系统导出", "file_template": None},
                {"filename": "COA-<订单号>.pdf", "source": "供应商提供或自制", "file_template": None},
                {"filename": "电子发票-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "收货回执.jpg", "source": "客户签收回传", "file_template": None}
            ]
        },
        {
            "name": "生产、采购、发货",
            "children": [
                {
                    "name": "唛头",
                    "children": [],
                    "ref_files": [
                        {"filename": "不干胶标签.docx", "source": "自制", "file_template": None}
                    ]
                }
            ],
            "ref_files": [
                {"filename": "生产通知单-<订单号>", "source": "自制", "file_template": "[产地]内贸生产"},
                {"filename": "发货通知单-<订单号>", "source": "自制", "file_template": "[产地]内贸发货"},
                {"filename": "采购合同-<订单号>.xlsx", "source": "自制", "file_template": "通用/CG.xlsx"},
                {"filename": "发货申请单.xlsx", "source": "自制", "file_template": None},
                {"filename": "已发货截图.png", "source": "物流截图", "file_template": None},
                {"filename": "到货截图.png", "source": "物流截图", "file_template": None}
            ]
        },
        {
            "name": "物流",
            "children": [
                {
                    "name": "物流点寄送文件",
                    "children": [],
                    "ref_files": []
                }
            ],
            "ref_files": [
                {"filename": "物流费用申请单.pdf", "source": "物流公司", "file_template": None},
                {"filename": "物流发票.pdf", "source": "物流公司", "file_template": None}
            ]
        },
        {
            "name": "证据链(ERP)",
            "children": [],
            "ref_files": [
                {"filename": "1.销售合同-<订单号>.pdf", "source": "业务提供", "file_template": None},
                {"filename": "2.销售发票-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "3.采购合同-<订单号>.pdf", "source": "自制", "file_template": None},
                {"filename": "4.采购发票-<订单号>.pdf", "source": "供应商提供", "file_template": None},
                {"filename": "5.收货回执-<订单号>.pdf", "source": "客户签收回传", "file_template": None},
                {"filename": "6.收款凭证-<订单号>.pdf", "source": "银行水单", "file_template": None}
            ]
        }
    ],
    "ref_files": [
        {"filename": "内销合同预审表-<订单号>.pdf", "source": "业务提供", "file_template": None},
        {"filename": "内销合同预审表-<订单号>.xlsx", "source": "业务提供", "file_template": None},
        {"filename": "PO-<客户PO号>.pdf", "source": "客户提供", "file_template": None},
        {"filename": "COA-<订单号>.doc", "source": "供应商提供或自制", "file_template": None},
        {"filename": "注意事项-<订单号>.docx", "source": "自制", "file_template": None}
    ]
}

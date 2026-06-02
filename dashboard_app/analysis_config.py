"""Reusable business semantics for the logistics franchisee dashboard.

The values here are intentionally generic keyword rules rather than row-level
data. Replacing the Excel source with the same structure should not require a
code change.
"""

DEFAULT_EXCEL_NAME = "辽宁区域_加盟商贡献表_202604（测试）.xlsx"

PAGE_PRIORITY = [
    "总表-加盟商",
    "总表-网点",
    "出港考核、派费补贴",
    "派费分析报表",
    "一口价明细_达量一口价导出",
    "总表-一口价",
    "辽宁区域贡献",
    "加盟商贡献",
    "包仓费明细",
    "中心代建包费明细",
    "运营管理类汇总表",
    "匹配表",
    "网点资料",
    "Sheet2",
    "Sheet3",
]

DIMENSION_KEYWORDS = {
    "月份": ["月份", "揽件月份", "产生月份", "业务发生月份", "件量统计月份", "政策期间", "账单产生日期"],
    "加盟商": ["加盟商", "所属加盟商", "寄件加盟商", "结算对象"],
    "网点": ["网点", "所属网点", "结算网点", "操作网点", "寄件网点", "网点名称"],
    "区域": ["所属代理区", "寄件代理区", "所属大区", "管理大区", "行政大区", "目的省份", "所属省", "所属城市", "财务中心", "区域", "代理区", "大区", "省", "城市"],
    "公斤段": ["公斤段", "重量段"],
    "状态": ["是否在网", "启用状态", "是否测试运行", "集散状态", "暂停网点"],
    "产品/业务": ["产品", "业务", "政策名称", "费用主类型", "费用类型", "类型", "报价名称", "返利流向", "功能类型", "网点类型"],
    "客户": ["客户名称", "客户编码", "统计对象"],
    "目的地": ["目的区域", "目的省份", "目的城市", "目的区县", "结算目的地"],
    "财务中心": ["财务中心", "所属财务中心", "结算财务中心"],
}

METRIC_PRIORITY = [
    "贡献总额",
    "经营贡献",
    "净贡献",
    "进、出港贡献",
    "贡献",
    "单量",
    "票数",
    "寄件签收量",
    "发件票数",
    "派件量",
    "出港",
    "进港",
    "重量",
    "计费重量",
    "面单费",
    "派件费",
    "派费",
    "补贴",
    "扣款",
    "发生金额",
    "收入",
    "成本",
    "四费",
]

SUM_METRIC_KEYWORDS = [
    "量",
    "票数",
    "重量",
    "费",
    "收入",
    "成本",
    "补贴",
    "扣款",
    "金额",
    "贡献",
    "总额",
    "总包数",
]

AVG_METRIC_KEYWORDS = ["均", "单票", "单公斤", "占比", "率", "达成"]

FINANCIAL_BUCKETS = {
    "收入": ["收入", "结算价", "面单费", "应收", "四费"],
    "派费/成本": ["派件费", "派费", "中转费", "操作费", "建包费", "包仓费", "成本"],
    "补贴": ["补贴", "返利", "加收"],
    "扣款/考核": ["扣款", "考核", "罚", "负"],
    "贡献": ["贡献"],
}

PAGE_MODULES = {
    "总表-加盟商": ["franchise_rank", "metric_distribution", "financial_structure", "scale_segment"],
    "总表-网点": ["outlet_rank", "franchise_distribution", "status_analysis", "region_distribution"],
    "派费分析报表": ["fee_structure", "unit_cost_distribution", "fee_rank", "abnormal_list"],
    "总表-一口价": ["target_overview", "kg_segment", "franchise_rank", "detail_drill"],
    "辽宁区域贡献": ["regional_overview", "trend", "share", "financial_structure"],
    "加盟商贡献": ["franchise_rank", "kg_segment", "share", "financial_structure"],
}

BASE_DATA_SHEETS = ["匹配表", "网点资料", "Sheet2", "Sheet3"]

ABNORMAL_KEYWORDS = ["异常", "超", "零", "负", "扣款", "考核", "费用为0", "金额"]

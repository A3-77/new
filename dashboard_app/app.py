from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from analysis_config import DEFAULT_EXCEL_NAME
from data_model import (
    abnormal_rows,
    aggregate_metric,
    apply_filters,
    build_profile,
    distribution_table,
    financial_structure,
    kpi_rows,
    list_excel_sheets,
    load_sheet,
    metric_aggregation,
    numeric_columns,
    page_period,
    quality_report,
    rank_table,
    read_source_bytes,
)

try:
    import plotly.express as px
except Exception:  # pragma: no cover - Streamlit can still run without Plotly.
    px = None


ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
DEFAULT_EXCEL_PATH = next(
    (path for path in [APP_DIR / DEFAULT_EXCEL_NAME, ROOT / DEFAULT_EXCEL_NAME] if path.exists()),
    ROOT / DEFAULT_EXCEL_NAME,
)


st.set_page_config(page_title="辽宁区域加盟商运营看板", layout="wide")

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1420px;
        padding: 2rem 2.4rem 3rem;
        margin: 0 auto;
    }
    div[data-testid="stVerticalBlock"] { gap: .85rem; }
    [data-testid="stMetric"] {
        background: #0b1220;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.16);
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #f9fafb !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
        fill: #d1fae5 !important;
    }
    .section-title {
        font-size: 1.12rem;
        font-weight: 700;
        margin: 1.8rem 0 .8rem;
        color: #f8fafc;
    }
    .small-note {color: #cbd5e1; font-size: .85rem;}
    .dashboard-panel {
        background: rgba(15, 23, 42, .74);
        border: 1px solid #243244;
        border-radius: 12px;
        padding: 16px 18px;
        margin: 12px 0 20px;
        box-shadow: 0 10px 28px rgba(2, 6, 23, .18);
    }
    .panel-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .panel-muted {
        color: #94a3b8;
        font-size: .86rem;
        line-height: 1.6;
    }
    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }
    .dimension-chip {
        display: inline-flex;
        align-items: center;
        min-height: 28px;
        padding: 5px 10px;
        border-radius: 999px;
        border: 1px solid #334155;
        background: #0b1220;
        color: #dbeafe;
        font-size: .84rem;
        max-width: 100%;
    }
    .kpi-card {
        min-height: 148px;
        padding: 16px 16px 14px;
        border-radius: 12px;
        background: linear-gradient(145deg, #07111f 0%, #0f172a 58%, #111827 100%);
        border: 1px solid #243244;
        box-shadow: 0 14px 30px rgba(2, 6, 23, .28);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }
    .kpi-label {
        color: #cbd5e1;
        font-size: .86rem;
        line-height: 1.45;
        min-height: 2.4em;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.05;
        margin: 10px 0;
        letter-spacing: 0;
    }
    .kpi-footer {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .kpi-badge {
        border-radius: 999px;
        padding: 4px 8px;
        background: rgba(14, 165, 233, .14);
        color: #bae6fd;
        border: 1px solid rgba(56, 189, 248, .28);
        font-size: .78rem;
    }
    .kpi-badge.green {
        background: rgba(16, 185, 129, .14);
        color: #bbf7d0;
        border-color: rgba(52, 211, 153, .28);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(2, 6, 23, .18);
        background: #0f172a;
    }
    div[data-testid="stDataFrame"] canvas {
        border-radius: 12px;
    }
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"],
    div[data-testid="stNumberInput"] {
        margin-bottom: .35rem;
    }
    div[data-testid="stTabs"] button {
        font-weight: 700;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #243244;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 14px;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        width: 100%;
        justify-content: flex-start;
        min-height: 34px;
        border-radius: 8px;
        border: 1px solid #1f2937;
        background: #111827;
        color: #e5e7eb;
        font-size: .9rem;
        line-height: 1.25;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        border-color: #38bdf8;
        background: #0f172a;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background: #020617;
        border-color: #38bdf8;
        color: #ffffff;
        font-weight: 700;
        box-shadow: inset 3px 0 0 #38bdf8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_sheets(excel_bytes: bytes) -> list[str]:
    return list_excel_sheets(excel_bytes)


@st.cache_data(show_spinner="正在加载 Sheet 数据...")
def cached_sheet(excel_bytes: bytes, sheet_name: str):
    return load_sheet(excel_bytes, sheet_name)


def fmt_number(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 100_000_000:
        return f"{value / 100_000_000:.2f}亿"
    if abs_value >= 10_000:
        return f"{value / 10_000:.2f}万"
    if abs_value >= 100:
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def render_kpi_card(label: str, value: str, meta: str, delta: str | None = None) -> None:
    delta_html = f'<span class="kpi-badge green">{escape(delta)}</span>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(label)}</div>
            <div class="kpi-value">{escape(value)}</div>
            <div class="kpi-footer">
                <span class="kpi-badge">{escape(meta)}</span>
                {delta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f"#### {text}")


def force_scroll_to_top() -> None:
    components.html(
        """
        <script>
        const scrollTop = () => {
          const doc = window.parent.document;
          const candidates = [
            window.parent,
            doc.scrollingElement,
            doc.documentElement,
            doc.body,
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('[data-testid="stMain"]'),
            doc.querySelector('section.main')
          ].filter(Boolean);
          for (const target of candidates) {
            try {
              if (target.scrollTo) target.scrollTo(0, 0);
              target.scrollTop = 0;
            } catch (e) {}
          }
        };
        scrollTop();
        setTimeout(scrollTop, 120);
        setTimeout(scrollTop, 450);
        setTimeout(scrollTop, 900);
        </script>
        """,
        height=0,
    )


def draw_bar(df: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False) -> None:
    if df.empty:
        st.info("当前筛选条件下暂无可绘制数据。")
        return
    if px:
        fig = px.bar(df, x=y if horizontal else x, y=x if horizontal else y, orientation="h" if horizontal else "v", title=title)
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(df.set_index(x)[y])


def draw_donut(df: pd.DataFrame, names: str, values: str, title: str) -> None:
    df = df[df[values] != 0]
    if df.empty:
        st.info("当前筛选条件下暂无结构数据。")
        return
    if px:
        fig = px.pie(df, names=names, values=values, hole=0.58, title=title)
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def draw_line(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty:
        st.info("当前筛选条件下暂无趋势数据。")
        return
    if px:
        fig = px.line(df, x=x, y=y, markers=True, title=title)
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df.set_index(x)[y])


def draw_histogram(df: pd.DataFrame, metric: str, title: str) -> None:
    series = pd.to_numeric(df[metric], errors="coerce").dropna() if metric in df.columns else pd.Series(dtype=float)
    if series.empty:
        st.info("当前筛选条件下暂无分布数据。")
        return
    if px:
        fig = px.histogram(series.to_frame(metric), x=metric, nbins=24, title=title)
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        dist = distribution_table(df, metric)
        if not dist.empty:
            dist["区间"] = dist["区间"].astype(str)
        draw_bar(dist, "区间", "数量", title)


def draw_scatter(df: pd.DataFrame, x: str, y: str, color: str | None, title: str) -> None:
    if x not in df.columns or y not in df.columns:
        return
    plot_df = df[[c for c in [x, y, color] if c and c in df.columns]].copy()
    plot_df[x] = pd.to_numeric(plot_df[x], errors="coerce")
    plot_df[y] = pd.to_numeric(plot_df[y], errors="coerce")
    plot_df = plot_df.dropna(subset=[x, y])
    if plot_df.empty:
        st.info("当前筛选条件下暂无关系分析数据。")
        return
    if len(plot_df) > 5000:
        plot_df = plot_df.sample(5000, random_state=42)
    if px:
        fig = px.scatter(plot_df, x=x, y=y, color=color if color in plot_df.columns else None, title=title)
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.scatter_chart(plot_df, x=x, y=y)


def draw_box(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if x not in df.columns or y not in df.columns:
        return
    plot_df = df[[x, y]].copy()
    plot_df[y] = pd.to_numeric(plot_df[y], errors="coerce")
    plot_df = plot_df.dropna(subset=[x, y])
    if plot_df.empty:
        return
    if len(plot_df) > 8000:
        plot_df = plot_df.sample(8000, random_state=42)
    if px:
        fig = px.box(plot_df, x=x, y=y, title=title)
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(plot_df.head(200), use_container_width=True, hide_index=True)


def draw_treemap(df: pd.DataFrame, names: str, values: str, title: str) -> None:
    if df.empty or names not in df.columns or values not in df.columns:
        return
    plot_df = df.copy()
    plot_df[values] = pd.to_numeric(plot_df[values], errors="coerce")
    plot_df = plot_df.dropna(subset=[names, values])
    plot_df = plot_df[plot_df[values] > 0]
    if plot_df.empty:
        return
    if px:
        fig = px.treemap(plot_df, path=[names], values=values, title=title)
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=48, b=20), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        draw_bar(plot_df.head(20), names, values, title, horizontal=True)


HEADER_GROUP_RULES = [
    ("出港业务", ["出港", "寄件", "发件", "签收量", "面单"]),
    ("进港/派件业务", ["进港", "派件", "派费", "派件量"]),
    ("一口价业务", ["一口价", "返利", "达量"]),
    ("贡献利润", ["贡献", "利润", "净贡献"]),
    ("费用收入", ["收入", "费用", "费", "金额", "结算价", "成本"]),
    ("补贴扣款考核", ["补贴", "扣款", "考核", "罚", "加收"]),
    ("重量公斤段", ["重量", "均重", "计费重量", "公斤段", "重量段"]),
    ("基础状态", ["是否", "状态", "启用", "测试运行", "在网"]),
]


def classify_header_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    columns = [str(c) for c in df.columns]
    for group, keywords in HEADER_GROUP_RULES:
        matched = [c for c in columns if any(keyword in c for keyword in keywords)]
        if matched:
            groups[group] = matched
    return groups


def classify_numeric_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    nums = numeric_columns(df)
    groups: dict[str, list[str]] = {}
    for group, keywords in HEADER_GROUP_RULES:
        matched = [c for c in nums if any(keyword in str(c) for keyword in keywords)]
        if matched:
            groups[group] = matched
    return groups


def usable_dimension_columns(df: pd.DataFrame, profile) -> list[str]:
    preferred = [
        "月份",
        "加盟商",
        "网点",
        "区域",
        "目的地",
        "产品/业务",
        "状态",
        "公斤段",
        "客户",
        "财务中心",
    ]
    columns: list[str] = []
    for dim in preferred:
        column = profile.dimensions.get(dim)
        if column and column in df.columns and column not in columns:
            columns.append(column)

    for column in df.columns:
        if column in columns or pd.api.types.is_numeric_dtype(df[column]):
            continue
        nunique = df[column].dropna().astype(str).nunique()
        if 2 <= nunique <= 80:
            columns.append(column)
    return columns


def choose_rank_dimension(df: pd.DataFrame, profile) -> str | None:
    for dim in ["加盟商", "网点", "区域", "目的地", "产品/业务", "状态", "公斤段", "财务中心", "月份"]:
        column = profile.dimensions.get(dim)
        if column and column in df.columns:
            nunique = df[column].dropna().astype(str).nunique()
            if 2 <= nunique <= 500:
                return column
    candidates = usable_dimension_columns(df, profile)
    return candidates[0] if candidates else None


def pick_metric_by_keywords(metrics: list[str], keywords: list[str]) -> str | None:
    for keyword in keywords:
        for metric in metrics:
            if keyword in str(metric):
                return metric
    return metrics[0] if metrics else None


def select_core_metric(df: pd.DataFrame, profile) -> str | None:
    metrics = profile.metrics or numeric_columns(df)
    priorities = [
        "贡献总额",
        "经营贡献",
        "净贡献",
        "贡献",
        "发生金额",
        "收入",
        "结算价",
        "派费",
        "派件费",
        "包仓费",
        "中心代建包费",
        "单量",
        "票数",
        "总票数",
        "重量",
        "计费重量",
    ]
    return pick_metric_by_keywords(metrics, priorities)


def select_core_dimension(df: pd.DataFrame, profile) -> str | None:
    sheet = profile.sheet_name
    if "网点" in sheet and profile.dimensions.get("网点"):
        return profile.dimensions["网点"]
    if "加盟商" in sheet and profile.dimensions.get("加盟商"):
        return profile.dimensions["加盟商"]
    if "区域" in sheet and (profile.dimensions.get("区域") or profile.dimensions.get("目的地")):
        return profile.dimensions.get("区域") or profile.dimensions.get("目的地")

    for dim in ["加盟商", "网点", "产品/业务", "区域", "目的地", "财务中心", "状态", "公斤段", "月份"]:
        column = profile.dimensions.get(dim)
        if column and column in df.columns:
            nunique = df[column].dropna().astype(str).nunique()
            if 2 <= nunique <= 500:
                return column
    return choose_rank_dimension(df, profile)


def select_breakdown_dimension(df: pd.DataFrame, profile, primary_dim: str | None) -> str | None:
    for dim in ["公斤段", "产品/业务", "状态", "区域", "目的地", "财务中心", "月份"]:
        column = profile.dimensions.get(dim)
        if not column or column == primary_dim or column not in df.columns:
            continue
        nunique = df[column].dropna().astype(str).nunique()
        if 2 <= nunique <= 30:
            return column
    return None


def can_show_share_chart(table: pd.DataFrame) -> bool:
    if table.empty or "指标值" not in table.columns:
        return False
    values = pd.to_numeric(table["指标值"], errors="coerce")
    return values.notna().any() and values.ge(0).all() and values.sum() > 0


def find_col(df: pd.DataFrame, keywords: list[str], numeric: bool | None = None) -> str | None:
    columns = list(df.columns)
    for keyword in keywords:
        for column in columns:
            if keyword in str(column):
                if numeric is True and not pd.api.types.is_numeric_dtype(df[column]):
                    continue
                if numeric is False and pd.api.types.is_numeric_dtype(df[column]):
                    continue
                return column
    return None


def first_existing(*columns: str | None) -> str | None:
    for column in columns:
        if column:
            return column
    return None


def grouped_metric(df: pd.DataFrame, dim: str, metric: str, n: int = 12, positive_only: bool = False) -> pd.DataFrame:
    table = rank_table(df, dim, metric, n=n, ascending=False)
    if positive_only and not table.empty:
        table = table[pd.to_numeric(table["指标值"], errors="coerce") > 0]
    return table


def draw_rank_if_possible(df: pd.DataFrame, dim: str | None, metric: str | None, title: str) -> bool:
    if not dim or not metric or dim not in df.columns or metric not in df.columns:
        return False
    table = grouped_metric(df, dim, metric, n=10)
    if table.empty:
        return False
    draw_bar(table, dim, "指标值", title, horizontal=True)
    return True


def draw_share_or_bar(df: pd.DataFrame, dim: str | None, metric: str | None, title: str) -> bool:
    if not dim or not metric or dim not in df.columns or metric not in df.columns:
        return False
    table = grouped_metric(df, dim, metric, n=12)
    if table.empty:
        return False
    if can_show_share_chart(table):
        draw_donut(table, dim, "指标值", title)
    else:
        draw_bar(table, dim, "指标值", title, horizontal=False)
    return True


def is_time_dimension(column: str | None) -> bool:
    return bool(column and any(keyword in str(column) for keyword in ["月份", "日期", "时间", "周期"]))


def metric_breakdown_table(df: pd.DataFrame, dim: str, metric: str, n: int = 12) -> pd.DataFrame:
    if dim not in df.columns or metric not in df.columns:
        return pd.DataFrame()
    work = df[[dim, metric]].copy()
    work[dim] = work[dim].astype(str).str.strip()
    work = work[(work[dim] != "") & (work[dim].str.lower() != "nan")]
    work[metric] = pd.to_numeric(work[metric], errors="coerce")
    work = work.dropna(subset=[metric])
    if work.empty:
        return pd.DataFrame()
    agg = "mean" if metric_aggregation(metric) == "mean" else "sum"
    grouped = work.groupby(dim, dropna=False)[metric].agg(agg).reset_index()
    grouped = grouped.rename(columns={metric: "指标值"})
    if is_time_dimension(dim):
        return grouped.sort_values(dim).head(n)
    return grouped.sort_values("指标值", ascending=False).head(n)


def compact_bar(table: pd.DataFrame, dim: str, title: str, height: int = 280) -> None:
    if table.empty or dim not in table.columns or "指标值" not in table.columns:
        return
    if px:
        fig = px.bar(table, x="指标值", y=dim, orientation="h", title=title, text_auto=".2s")
        fig.update_layout(
            height=height,
            margin=dict(l=10, r=10, t=42, b=12),
            template="plotly_white",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(table.set_index(dim)["指标值"])


def compact_line(table: pd.DataFrame, dim: str, title: str, height: int = 280) -> None:
    if table.empty or dim not in table.columns or "指标值" not in table.columns:
        return
    if px:
        fig = px.line(table, x=dim, y="指标值", markers=True, title=title)
        fig.update_layout(height=height, margin=dict(l=10, r=10, t=42, b=12), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(table.set_index(dim)["指标值"])


def numeric_field_summary(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    rows = []
    for metric in metrics:
        series = pd.to_numeric(df[metric], errors="coerce")
        rows.append(
            {
                "字段": metric,
                "指标值": aggregate_metric(df, metric),
                "计算口径": "平均" if metric_aggregation(metric) == "mean" else "求和",
                "非空行数": int(series.notna().sum()),
            }
        )
    return pd.DataFrame(rows)


def dimension_field_summary(df: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    rows = []
    for dim in dims:
        series = df[dim].dropna().astype(str).str.strip()
        series = series[series != ""]
        rows.append(
            {
                "字段": dim,
                "分类数量": int(series.nunique()),
                "有效行数": int(series.count()),
            }
        )
    return pd.DataFrame(rows)


def ordered_metrics(df: pd.DataFrame, profile) -> list[str]:
    metrics: list[str] = []
    for metric in list(profile.metrics or []) + numeric_columns(df):
        if metric in df.columns and metric not in metrics:
            series = pd.to_numeric(df[metric], errors="coerce")
            if series.notna().any():
                metrics.append(metric)
    return metrics


def visual_metric_list(df: pd.DataFrame, profile, limit: int) -> list[str]:
    metrics = ordered_metrics(df, profile)
    if len(metrics) <= limit:
        return metrics
    core = []
    for metric in [select_core_metric(df, profile)] + list(profile.kpi_metrics or []):
        if metric and metric in metrics and metric not in core:
            core.append(metric)
    for metric in metrics:
        if metric not in core:
            core.append(metric)
        if len(core) >= limit:
            break
    return core


def draw_dimension_value_counts(df: pd.DataFrame, dim: str, title: str, n: int = 12) -> None:
    if dim not in df.columns:
        return
    counts = (
        df[dim]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: (s != "") & (s.str.lower() != "nan")]
        .value_counts()
        .head(n)
        .reset_index()
    )
    if counts.empty:
        return
    counts.columns = [dim, "记录数"]
    if px:
        fig = px.bar(counts, x="记录数", y=dim, orientation="h", title=title, text_auto=True)
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=42, b=12),
            template="plotly_white",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(counts.set_index(dim)["记录数"])


def render_field_visualizer(df: pd.DataFrame, profile, *, compact: bool = False) -> None:
    metrics = ordered_metrics(df, profile)
    dims = usable_dimension_columns(df, profile)
    primary_dim = select_core_dimension(df, profile)
    if primary_dim not in dims:
        primary_dim = dims[0] if dims else None

    if not metrics and not dims:
        st.info("当前 Sheet 没有可图表化的数值字段或维度字段。")
        return

    section_title("按当前 Sheet 表头生成的图表")
    st.caption("下面的图只使用当前 Sheet 的表头和数据自动生成；有这个字段才展示，没有这个字段就不展示。")

    if dims:
        dim_summary = dimension_field_summary(df, dims)
        if not dim_summary.empty:
            with st.container(border=True):
                st.markdown("**维度字段画像**")
                if px:
                    fig = px.bar(dim_summary, x="分类数量", y="字段", orientation="h", title="维度字段可分析颗粒度", text_auto=True)
                    fig.update_layout(
                        height=min(420, 170 + 28 * len(dim_summary)),
                        margin=dict(l=10, r=10, t=42, b=12),
                        template="plotly_white",
                        yaxis=dict(autorange="reversed"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(dim_summary.set_index("字段")["分类数量"])

    if metrics:
        summary = numeric_field_summary(df, metrics)
        with st.container(border=True):
            st.markdown("**数值表头总览**")
            max_fields = 30 if len(summary) > 30 else len(summary)
            shown = summary.reindex(summary["指标值"].abs().sort_values(ascending=False).index).head(max_fields)
            if px:
                fig = px.bar(shown, x="指标值", y="字段", color="计算口径", orientation="h", title="所有数值表头汇总/均值概览", text_auto=".2s")
                fig.update_layout(
                    height=min(720, 190 + 22 * len(shown)),
                    margin=dict(l=10, r=10, t=42, b=12),
                    template="plotly_white",
                    yaxis=dict(autorange="reversed"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(shown.set_index("字段")["指标值"])
            if len(summary) > max_fields:
                st.caption(f"当前 Sheet 共有 {len(summary)} 个数值表头，图中展示量级最大的 {max_fields} 个；完整字段仍可在下方单字段钻取中选择。")

    if primary_dim and metrics:
        auto_limit = 12 if len(metrics) <= 16 else 8
        if compact:
            auto_limit = min(auto_limit, 6)
        auto_metrics = visual_metric_list(df, profile, auto_limit)
        section_title(f"按「{primary_dim}」拆解关键表头")
        cols = st.columns(2)
        for idx, metric in enumerate(auto_metrics):
            with cols[idx % 2]:
                with st.container(border=True):
                    agg_name = "平均" if metric_aggregation(metric) == "mean" else "求和"
                    table = metric_breakdown_table(df, primary_dim, metric, n=10)
                    title = f"{metric} 按 {primary_dim} {agg_name}对比"
                    st.markdown(f"**{metric}**")
                    st.caption(f"按「{primary_dim}」{agg_name}对比")
                    if is_time_dimension(primary_dim):
                        compact_line(table, primary_dim, title)
                    else:
                        compact_bar(table, primary_dim, title)
        if len(metrics) > len(auto_metrics):
            st.caption(f"为避免页面过载，已自动展开最核心的 {len(auto_metrics)} 个数值表头；其余表头可在下面继续钻取。")
    elif dims and not metrics:
        section_title("维度字段分布")
        cols = st.columns(2)
        for idx, dim in enumerate(dims[:6]):
            with cols[idx % 2]:
                with st.container(border=True):
                    draw_dimension_value_counts(df, dim, f"{dim} 记录数分布")

    if metrics:
        with st.container(border=True):
            st.markdown("**单字段钻取**")
            core_metric = select_core_metric(df, profile)
            metric_index = metrics.index(core_metric) if core_metric in metrics else 0
            metric = st.selectbox("选择要分析的数值表头", metrics, index=metric_index, key=f"metric_drill_{profile.sheet_name}")

            if dims:
                dim_index = dims.index(primary_dim) if primary_dim in dims else 0
                dim = st.selectbox("选择分组维度表头", dims, index=dim_index, key=f"dim_drill_{profile.sheet_name}")
                table = metric_breakdown_table(df, dim, metric, n=15)
                left, right = st.columns(2)
                with left:
                    if is_time_dimension(dim):
                        compact_line(table, dim, f"{metric} 按 {dim} 趋势")
                    else:
                        compact_bar(table, dim, f"{metric} 按 {dim} 排名")
                with right:
                    if can_show_share_chart(table):
                        draw_donut(table, dim, "指标值", f"{metric} 按 {dim} 占比")
                    else:
                        draw_box(df, dim, metric, f"{metric} 按 {dim} 分布")

            left, right = st.columns(2)
            with left:
                draw_histogram(df, metric, f"{metric} 数值分布")
            other_metrics = [m for m in metrics if m != metric]
            if other_metrics:
                relation_default = 0
                for idx, candidate in enumerate(other_metrics):
                    if any(keyword in str(candidate) for keyword in ["贡献", "利润", "收入", "费用", "重量", "单量", "票数"]):
                        relation_default = idx
                        break
                relation_metric = st.selectbox("选择关联数值表头", other_metrics, index=relation_default, key=f"relation_metric_{profile.sheet_name}")
                with right:
                    draw_scatter(df, metric, relation_metric, primary_dim, f"{metric} vs {relation_metric}")


def render_header_profile(df: pd.DataFrame) -> None:
    groups = classify_header_groups(df)
    with st.container(border=True):
        st.markdown("**表头字段画像**")
        if not groups:
            st.caption("当前 Sheet 表头没有匹配到明确的物流业务字段，页面会以明细表和数据质量校验为主。")
            return
        cols = st.columns(min(4, len(groups)))
        for idx, (group, fields) in enumerate(groups.items()):
            with cols[idx % len(cols)]:
                render_kpi_card(group, f"{len(fields)}", "匹配字段数", None)


def render_metric_group_summary(df: pd.DataFrame, group_name: str, columns: list[str]) -> None:
    rows = []
    for column in columns[:10]:
        series = pd.to_numeric(df[column], errors="coerce")
        rows.append(
            {
                "指标字段": column,
                "计算口径": "平均" if metric_aggregation(column) == "mean" else "求和",
                "汇总值": aggregate_metric(df, column),
                "均值": float(series.mean()) if series.notna().any() else 0.0,
                "非空行数": int(series.notna().sum()),
            }
        )
    with st.container(border=True):
        st.markdown(f"**{group_name}字段汇总**")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_total_franchise_dashboard(df: pd.DataFrame, profile) -> None:
    entity = profile.dimensions.get("加盟商")
    contribution = find_col(df, ["总贡献", "贡献总额", "进、出港贡献", "贡献"], numeric=True)
    volume = find_col(df, ["寄件签收量", "单量", "票数", "出港"], numeric=True)
    fee = find_col(df, ["派件费", "面单费", "收入", "四费"], numeric=True)
    section_title("加盟商经营贡献核心排名")
    draw_rank_if_possible(df, entity, contribution or fee or volume, "加盟商贡献 TOP10")
    if contribution and volume:
        section_title("规模与贡献关系")
        draw_scatter(df, volume, contribution, entity, f"{volume} vs {contribution}")
    if contribution or fee:
        section_title("经营收支结构")
        draw_donut(financial_structure(df), "类别", "金额", "收入/成本/补贴/贡献结构")


def render_total_outlet_dashboard(df: pd.DataFrame, profile) -> None:
    outlet = profile.dimensions.get("网点")
    franchise = profile.dimensions.get("加盟商")
    status = profile.dimensions.get("状态")
    contribution = find_col(df, ["总贡献", "贡献总额", "进、出港贡献", "贡献"], numeric=True)
    volume = find_col(df, ["寄件签收量", "单量", "票数", "出港"], numeric=True)
    section_title("网点经营贡献核心排名")
    draw_rank_if_possible(df, outlet, contribution or volume, "网点贡献 TOP10")
    if franchise and contribution:
        section_title("加盟商下属网点贡献分布")
        draw_share_or_bar(df, franchise, contribution, "加盟商网点贡献占比")
    if status and contribution:
        section_title("网点状态贡献对比")
        draw_share_or_bar(df, status, contribution, "网点状态贡献结构")


def render_fee_dashboard(df: pd.DataFrame, profile) -> None:
    franchise = profile.dimensions.get("加盟商")
    weight = profile.dimensions.get("公斤段")
    fee = find_col(df, ["派费", "派件费", "续重派费", "应收"], numeric=True)
    tickets = find_col(df, ["发件票数", "派件票数", "签收票数", "票数"], numeric=True)
    section_title("派费核心排名")
    draw_rank_if_possible(df, franchise, fee or tickets, "加盟商派费 TOP10")
    if weight and fee:
        section_title("重量段派费分布")
        draw_box(df, weight, fee, "各重量段派费分布")
    if weight and tickets:
        section_title("重量段票量结构")
        draw_share_or_bar(df, weight, tickets, "重量段票量占比")


def render_one_price_dashboard(df: pd.DataFrame, profile) -> None:
    franchise = profile.dimensions.get("加盟商")
    kg = profile.dimensions.get("公斤段")
    contribution = find_col(df, ["一口价）", "贡献总额", "贡献"], numeric=True)
    revenue = find_col(df, ["一口价结算价", "费用金额", "四费", "收入"], numeric=True)
    tickets = find_col(df, ["总票数", "单量", "票数"], numeric=True)
    weight = find_col(df, ["计费重量", "重量"], numeric=True)
    section_title("一口价贡献排名")
    draw_rank_if_possible(df, franchise, contribution or revenue or tickets, "加盟商一口价贡献 TOP10")
    if kg and (contribution or revenue or tickets):
        section_title("一口价公斤段结构")
        draw_share_or_bar(df, kg, contribution or revenue or tickets, "公斤段一口价结构")
    if contribution and tickets:
        section_title("票量与贡献关系")
        draw_scatter(df, tickets, contribution, franchise, f"{tickets} vs {contribution}")
    elif revenue and weight:
        section_title("重量与收入关系")
        draw_scatter(df, weight, revenue, franchise, f"{weight} vs {revenue}")


def render_one_price_summary_dashboard(df: pd.DataFrame, profile) -> None:
    franchise = profile.dimensions.get("加盟商")
    qty = find_col(df, ["单量_4.1-4.30签收量", "单量"], numeric=True)
    daily = find_col(df, ["日均单量"], numeric=True)
    weight = find_col(df, ["计费重量"], numeric=True)
    avg_weight = find_col(df, ["均重"], numeric=True)
    four_fee = find_col(df, ["四费"], numeric=True)
    price = find_col(df, ["一口价结算价"], numeric=True)
    delivery = find_col(df, ["派件费"], numeric=True)
    contribution = find_col(df, ["贡献总额", "贡献"], numeric=True)
    ticket_contrib = find_col(df, ["单票贡献"], numeric=True)
    kg_contrib = find_col(df, ["单公斤贡献"], numeric=True)

    section_title("一口价贡献与规模排名")
    draw_rank_if_possible(df, franchise, contribution or price or qty, "加盟商一口价贡献 TOP10")

    if daily and contribution:
        section_title("日均单量与贡献关系")
        draw_scatter(df, daily, contribution, franchise, f"{daily} vs {contribution}")
    elif qty and contribution:
        section_title("单量与贡献关系")
        draw_scatter(df, qty, contribution, franchise, f"{qty} vs {contribution}")

    structure_rows = []
    for name, column in [
        ("四费", four_fee),
        ("一口价结算价", price),
        ("派件费", delivery),
        ("贡献总额", contribution),
    ]:
        if column:
            structure_rows.append({"指标": name, "金额": aggregate_metric(df, column)})
    if len(structure_rows) >= 2:
        section_title("一口价收支结构")
        structure = pd.DataFrame(structure_rows)
        if can_show_share_chart(structure.rename(columns={"金额": "指标值"})):
            draw_donut(structure, "指标", "金额", "四费/结算价/派件费/贡献结构")
        else:
            draw_bar(structure, "指标", "金额", "四费/结算价/派件费/贡献结构")


def render_region_contribution_dashboard(df: pd.DataFrame, profile) -> None:
    destination = first_existing(profile.dimensions.get("目的地"), profile.dimensions.get("区域"))
    contribution = find_col(df, ["贡献总额", "贡献"], numeric=True)
    volume = find_col(df, ["单量", "票数"], numeric=True)
    section_title("区域目的地贡献")
    if destination and (contribution or volume):
        table = grouped_metric(df, destination, contribution or volume, n=20, positive_only=True)
        draw_treemap(table, destination, "指标值", "目的地贡献/单量面积图")
    if destination and contribution:
        section_title("目的地贡献 TOP10")
        draw_rank_if_possible(df, destination, contribution, "目的地贡献 TOP10")


def render_cost_detail_dashboard(df: pd.DataFrame, profile) -> None:
    franchise = profile.dimensions.get("加盟商")
    outlet = profile.dimensions.get("网点")
    business = profile.dimensions.get("产品/业务")
    metric = find_col(df, ["发生金额", "包仓费", "中心代建包费", "建包", "实收", "费用", "金额"], numeric=True)
    section_title("费用核心排名")
    draw_rank_if_possible(df, franchise or outlet, metric, "费用 TOP10")
    if business and metric:
        section_title("费用类型结构")
        draw_share_or_bar(df, business, metric, "费用类型结构")
    if outlet and metric and outlet != franchise:
        section_title("网点费用排名")
        draw_rank_if_possible(df, outlet, metric, "网点费用 TOP10")


def render_ops_dashboard(df: pd.DataFrame, profile) -> None:
    month = profile.dimensions.get("月份")
    business = profile.dimensions.get("产品/业务")
    outlet = profile.dimensions.get("网点")
    metric = find_col(df, ["发生金额", "金额", "费用"], numeric=True)
    if month and metric and df[month].dropna().astype(str).nunique() > 1:
        section_title("运营费用月度趋势")
        trend = (
            df.groupby(month, dropna=False)[metric]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").sum())
            .reset_index()
            .rename(columns={metric: "指标值"})
            .sort_values(month)
        )
        draw_line(trend, month, "指标值", "运营费用月度趋势")
    if business and metric:
        section_title("运营费用类型结构")
        draw_share_or_bar(df, business, metric, "费用主类型结构")
    if outlet and metric:
        section_title("网点运营费用 TOP10")
        draw_rank_if_possible(df, outlet, metric, "网点运营费用 TOP10")


def render_generic_business_dashboard(df: pd.DataFrame, profile) -> None:
    metric = select_core_metric(df, profile)
    dim = select_core_dimension(df, profile)
    breakdown = select_breakdown_dimension(df, profile, dim)
    if metric and dim:
        section_title("核心排名")
        draw_rank_if_possible(df, dim, metric, f"{dim} TOP10 - {metric}")
    if metric and breakdown:
        section_title("核心结构")
        draw_share_or_bar(df, breakdown, metric, f"{breakdown}结构 - {metric}")


def filter_options(df: pd.DataFrame, column: str, limit: int = 500) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str)
    values = values[values.str.strip() != ""].drop_duplicates().sort_values().head(limit).tolist()
    return values


def render_page_nav(sheets: list[str]) -> str:
    st.sidebar.markdown("### 页面导航")
    if "current_sheet" not in st.session_state or st.session_state.current_sheet not in sheets:
        st.session_state.current_sheet = sheets[0]
    for idx, sheet in enumerate(sheets):
        selected = sheet == st.session_state.current_sheet
        if st.sidebar.button(sheet, key=f"nav_{idx}", type="primary" if selected else "secondary", use_container_width=True):
            st.session_state.current_sheet = sheet
            st.session_state.scroll_to_top = True
            st.rerun()
    return st.session_state.current_sheet


def render_global_filters(df: pd.DataFrame, dimensions: dict[str, str]) -> dict[str, list[str]]:
    st.sidebar.markdown("### 全局筛选")
    filters: dict[str, list[str]] = {}
    for dim in ["月份", "加盟商", "区域"]:
        column = dimensions.get(dim)
        if not column:
            continue
        options = filter_options(df, column)
        if not options:
            continue
        current = st.session_state.get(f"filter_{dim}", [])
        selected = st.sidebar.multiselect(f"{dim}（{column}）", options=options, default=[v for v in current if v in options])
        st.session_state[f"filter_{dim}"] = selected
        filters[dim] = selected
    if st.sidebar.button("重置筛选", use_container_width=True):
        for dim in ["月份", "加盟商", "区域"]:
            st.session_state[f"filter_{dim}"] = []
        st.rerun()
    return filters


def render_kpis(df: pd.DataFrame, profile) -> None:
    if profile.page_type == "基础档案/配置表":
        duplicate_count = int(df.duplicated().sum()) if not df.empty else 0
        null_count = int(df.isna().sum().sum()) if not df.empty else 0
        cols = st.columns(4)
        cards = [
            ("数据行数", f"{len(df):,}", "基础统计", None),
            ("字段数量", f"{len(df.columns):,}", "基础统计", None),
            ("重复行数", f"{duplicate_count:,}", "质量校验", None),
            ("空值单元格", f"{null_count:,}", "质量校验", None),
        ]
        for col, card in zip(cols, cards):
            with col:
                st.metric(card[0], card[1], delta=card[3])
                st.caption(card[2])
        return
    rows = kpi_rows(df, profile)
    if not rows:
        st.info("未识别到可汇总的核心业务指标。")
        return
    cols = st.columns(len(rows))
    for idx, row in enumerate(rows):
        delta = None if row["目标达成率"] is None else f"目标达成 {row['目标达成率']:.1%}"
        with cols[idx]:
            st.metric(row["指标"], fmt_number(row["当前值"]), delta=delta)
            st.caption(row["计算口径"])


def render_dimension_panel(profile, filters: dict[str, list[str]]) -> None:
    dimension_text = []
    for name, column in profile.dimensions.items():
        dimension_text.append(f"`{name}: {column}`")
    if not dimension_text:
        dimension_text.append("`未识别到通用维度字段`")

    active = []
    for dim, values in filters.items():
        if values:
            preview = "、".join(values[:3])
            suffix = f" 等 {len(values)} 项" if len(values) > 3 else ""
            active.append(f"{dim}: {preview}{suffix}")
    with st.container(border=True):
        st.markdown("**当前页面维度**")
        if active:
            st.caption("已应用筛选：" + "；".join(active))
        st.markdown(" ".join(dimension_text))


def load_overview_sheet(excel_bytes: bytes, sheets: list[str], preferred: list[str]) -> tuple[pd.DataFrame, object] | tuple[pd.DataFrame, None]:
    for sheet in preferred:
        if sheet in sheets:
            df, _schema = cached_sheet(excel_bytes, sheet)
            return df, build_profile(sheet, df)
    return pd.DataFrame(), None


def sum_matching_metrics(df: pd.DataFrame, keywords: list[str]) -> tuple[float, list[str]]:
    columns = [
        column
        for column in numeric_columns(df)
        if any(keyword in str(column) for keyword in keywords)
    ]
    value = float(sum(aggregate_metric(df, column) for column in columns)) if columns else 0.0
    return value, columns


def overview_dimension(df: pd.DataFrame, profile, semantic: str, keywords: list[str]) -> str | None:
    column = profile.dimensions.get(semantic) if profile else None
    if column and column in df.columns:
        return column
    return find_col(df, keywords, numeric=False)


def overview_metric(df: pd.DataFrame, keywords: list[str]) -> str | None:
    return find_col(df, keywords, numeric=True)


def render_pinned_overview(excel_bytes: bytes, sheets: list[str]) -> None:
    fee_df, fee_profile = load_overview_sheet(excel_bytes, sheets, ["派费分析报表", "出港考核、派费补贴"])
    franchise_df, franchise_profile = load_overview_sheet(excel_bytes, sheets, ["总表-加盟商", "加盟商贡献", "总表-网点"])
    deduction_df = franchise_df if not franchise_df.empty else fee_df

    franchise_col = overview_dimension(fee_df, fee_profile, "加盟商", ["所属加盟商", "加盟商", "结算对象"])
    if not franchise_col:
        franchise_col = overview_dimension(franchise_df, franchise_profile, "加盟商", ["所属加盟商", "加盟商", "结算对象"])
    flow_col = overview_dimension(fee_df, fee_profile, "目的地", ["流向", "返利流向", "目的地", "始发", "寄件方向"])
    kg_col = overview_dimension(fee_df, fee_profile, "公斤段", ["公斤段", "重量段", "重量明细"])
    fee_metric = overview_metric(fee_df, ["派费金额", "派费", "派件费", "应付派费", "应收派费", "派费总额"])
    deduction_total, deduction_cols = sum_matching_metrics(deduction_df, ["扣款", "罚款", "考核扣款", "进港扣款", "出港扣款"])

    fee_total = aggregate_metric(fee_df, fee_metric) if fee_metric else 0.0
    franchise_count = 0
    if franchise_col:
        source = fee_df if franchise_col in fee_df.columns else franchise_df
        franchise_count = int(source[franchise_col].dropna().astype(str).str.strip().replace("", np.nan).dropna().nunique())

    section_title("总览")
    with st.container(border=True):
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.metric("加盟商数量", f"{franchise_count:,}")
            st.caption("维度一：加盟商")
        with kpi_cols[1]:
            st.metric("派费金额", fmt_number(fee_total))
            st.caption(fee_metric or "未识别到派费金额字段")
        with kpi_cols[2]:
            st.metric("扣款", fmt_number(deduction_total))
            st.caption(f"匹配字段 {len(deduction_cols)} 个" if deduction_cols else "未识别到扣款字段")
        with kpi_cols[3]:
            st.metric("派费-扣款", fmt_number(fee_total - deduction_total))
            st.caption("用于汇报口径参考")

        if franchise_col:
            source_df = fee_df if franchise_col in fee_df.columns else franchise_df
            options = filter_options(source_df, franchise_col, limit=1000)
            selected = st.selectbox("加盟商下探", options=options, key="overview_franchise_drill") if options else None
            drill_df = source_df[source_df[franchise_col].astype(str) == selected] if selected else source_df
            metric = fee_metric if fee_metric and fee_metric in drill_df.columns else select_core_metric(drill_df, build_profile("总览", drill_df))
            left, right = st.columns(2)
            with left:
                if flow_col and metric and flow_col in drill_df.columns:
                    table = metric_breakdown_table(drill_df, flow_col, metric, n=12)
                    compact_bar(table, flow_col, f"{selected or '全部加盟商'} - 流向下探")
                else:
                    st.info("当前数据未识别到可下探的流向字段。")
            with right:
                if kg_col and metric and kg_col in drill_df.columns:
                    table = metric_breakdown_table(drill_df, kg_col, metric, n=12)
                    compact_bar(table, kg_col, f"{selected or '全部加盟商'} - 公斤段下探")
                else:
                    st.info("当前数据未识别到可下探的公斤段字段。")
        else:
            st.info("当前工作簿未识别到加盟商字段，暂不能生成加盟商下探。")


def analysis_frame(df: pd.DataFrame, row_limit: int | None) -> pd.DataFrame:
    if row_limit is None or len(df) <= row_limit:
        return df
    return df.sample(n=row_limit, random_state=42)


def render_abnormal_section(work_df: pd.DataFrame, profile) -> None:
    section_title("异常预警")
    if st.toggle("生成异常预警清单", value=False, key=f"abnormal_{profile.sheet_name}"):
        abnormal = abnormal_rows(work_df)
        if abnormal.empty:
            st.success("未发现负值、零值或 P99 以上高值预警。")
        else:
            st.dataframe(abnormal, use_container_width=True, height=320, hide_index=True)
    else:
        st.caption("异常预警会扫描多个数值字段，大表默认不自动生成；需要时打开上方开关。")


def render_specific_modules(df: pd.DataFrame, profile, row_limit: int | None, presentation_mode: bool) -> None:
    work_df = analysis_frame(df, row_limit)
    if len(work_df) < len(df):
        st.caption(f"快速模式：KPI 与明细表使用全量数据；图表分析基于 {len(work_df):,}/{len(df):,} 行抽样，以提升响应速度。")

    sheet = profile.sheet_name
    if sheet == "总表-加盟商" or sheet == "加盟商贡献":
        render_total_franchise_dashboard(work_df, profile)
    elif sheet == "总表-网点":
        render_total_outlet_dashboard(work_df, profile)
    elif "派费分析" in sheet:
        render_fee_dashboard(work_df, profile)
    elif sheet == "总表-一口价":
        render_one_price_summary_dashboard(work_df, profile)
    elif "一口价" in sheet:
        render_one_price_dashboard(work_df, profile)
    elif sheet == "辽宁区域贡献":
        render_region_contribution_dashboard(work_df, profile)
    elif "运营管理" in sheet:
        render_ops_dashboard(work_df, profile)
    elif "包仓费" in sheet or "中心代建包" in sheet or "出港考核" in sheet:
        render_cost_detail_dashboard(work_df, profile)
    else:
        render_generic_business_dashboard(work_df, profile)

    if presentation_mode:
        with st.expander("字段探索图表（汇报时可不展开）", expanded=False):
            render_field_visualizer(work_df, profile, compact=True)
        with st.expander("异常预警（需要时展开）", expanded=False):
            render_abnormal_section(work_df, profile)
    else:
        render_field_visualizer(work_df, profile)
        render_abnormal_section(work_df, profile)


def render_detail_table(df: pd.DataFrame, sheet_name: str) -> None:
    with st.container(border=True):
        section_title("明细数据区")
        query = st.text_input("表内模糊搜索", placeholder="输入加盟商、网点、区域、费用类型等关键词")
        view = df
        if query:
            mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
            view = df[mask]

        col_a, col_b, col_c = st.columns([1, 1, 4])
        page_size = col_a.selectbox("每页行数", [50, 100, 200, 500, 1000], index=1)
        total_pages = max(1, int(np.ceil(len(view) / page_size))) if len(view) else 1
        page = col_b.number_input("页码", min_value=1, max_value=total_pages, value=1, step=1)
        start = (page - 1) * page_size
        st.caption(f"当前筛选后 {len(view):,} 行，显示第 {page}/{total_pages} 页。表头可排序，右上角工具可全屏查看。")
        st.dataframe(view.iloc[start : start + page_size], use_container_width=True, height=520, hide_index=True)
        st.download_button(
            "导出当前筛选结果 CSV",
            data=view.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{sheet_name}_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )


def main() -> None:
    st.sidebar.title("运营看板")
    uploaded = st.sidebar.file_uploader("替换 Excel 数据源", type=["xlsx", "xlsm", "xls"])
    if not DEFAULT_EXCEL_PATH.exists() and uploaded is None:
        st.error(f"未找到默认数据源：{DEFAULT_EXCEL_PATH}")
        st.stop()

    excel_bytes = read_source_bytes(DEFAULT_EXCEL_PATH, uploaded)
    sheets = cached_sheets(excel_bytes)
    if not sheets:
        st.error("未识别到有效 Sheet。")
        st.stop()

    sheet_name = render_page_nav(sheets)
    raw_df, schema = cached_sheet(excel_bytes, sheet_name)
    profile = build_profile(sheet_name, raw_df)
    filters = render_global_filters(raw_df, profile.dimensions)
    st.sidebar.markdown("### 性能")
    presentation_mode = st.sidebar.toggle("领导汇报模式", value=True)
    fast_mode = st.sidebar.toggle("快速模式", value=True)
    row_limit_option = st.sidebar.selectbox("图表计算行数", ["2万行", "5万行", "10万行", "全量"], index=1, disabled=not fast_mode)
    row_limit_map = {"2万行": 20_000, "5万行": 50_000, "10万行": 100_000, "全量": None}
    analysis_row_limit = row_limit_map[row_limit_option] if fast_mode else None
    df = apply_filters(raw_df, filters, profile.dimensions)
    profile = build_profile(sheet_name, df)

    if st.session_state.get("scroll_to_top"):
        force_scroll_to_top()
        st.session_state.scroll_to_top = False

    st.title(sheet_name)
    st.caption(f"数据周期：{page_period(df, profile.dimensions)} | 页面类型：{profile.page_type} | 原始行数：{len(raw_df):,} | 当前行数：{len(df):,}")

    render_pinned_overview(excel_bytes, sheets)

    section_title("核心指标 KPI")
    render_kpis(df, profile)

    render_dimension_panel(profile, filters)

    analysis_tab, detail_tab, model_tab = st.tabs(["分析视图", "明细数据", "模型说明"])
    with analysis_tab:
        if profile.page_type == "基础档案/配置表":
            section_title("基础数据总览与质量校验")
            st.dataframe(quality_report(df), use_container_width=True, hide_index=True)
            if presentation_mode:
                with st.expander("字段探索图表（汇报时可不展开）", expanded=False):
                    render_field_visualizer(analysis_frame(df, analysis_row_limit), profile, compact=True)
            else:
                render_field_visualizer(analysis_frame(df, analysis_row_limit), profile, compact=True)
            section_title("基础数据预览")
            st.caption(f"展示前 {min(len(df), 100):,} 行；完整数据在「明细数据」页签中查看和导出。")
            st.dataframe(df.head(100), use_container_width=True, height=420, hide_index=True)
        else:
            render_specific_modules(df, profile, analysis_row_limit, presentation_mode)

    with detail_tab:
        render_detail_table(df, sheet_name)

    with model_tab:
        section_title("数据模型说明")
        st.write(
            {
                "表头行": f"Excel 第 {schema.header_start + 1} 至 {schema.header_end + 1} 行",
                "识别字段数": len(schema.columns),
                "KPI字段": profile.kpi_metrics,
                "页面模块": profile.modules,
            }
        )


if __name__ == "__main__":
    main()

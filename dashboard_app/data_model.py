from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd

from analysis_config import (
    AVG_METRIC_KEYWORDS,
    BASE_DATA_SHEETS,
    DIMENSION_KEYWORDS,
    FINANCIAL_BUCKETS,
    METRIC_PRIORITY,
    PAGE_MODULES,
    PAGE_PRIORITY,
    SUM_METRIC_KEYWORDS,
)


@dataclass(frozen=True)
class SheetSchema:
    sheet_name: str
    header_start: int
    header_end: int
    columns: list[str]
    rows: int
    cols: int


@dataclass(frozen=True)
class SheetProfile:
    sheet_name: str
    page_type: str
    dimensions: dict[str, str]
    metrics: list[str]
    kpi_metrics: list[str]
    modules: list[str]


def read_source_bytes(default_path: Path, uploaded: Any | None = None) -> bytes:
    if uploaded is not None:
        return uploaded.getvalue()
    return default_path.read_bytes()


def list_excel_sheets(excel_bytes: bytes) -> list[str]:
    xls = pd.ExcelFile(BytesIO(excel_bytes), engine="openpyxl")
    sheets = [s for s in xls.sheet_names if str(s).strip()]
    ordered = [s for s in PAGE_PRIORITY if s in sheets]
    ordered.extend([s for s in sheets if s not in ordered])
    return ordered


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, float) and np.isnan(value)) or str(value).strip() == ""


def _clean_cell(value: Any) -> str:
    if _is_blank(value):
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    return re.sub(r"\s+", " ", text)


def _is_number_like(value: Any) -> bool:
    if _is_blank(value):
        return False
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        return True
    text = str(value).strip().replace(",", "")
    return bool(re.fullmatch(r"[-+]?\d+(\.\d+)?%?", text))


def _row_features(row: pd.Series) -> dict[str, float]:
    values = list(row)
    nonblank = [v for v in values if not _is_blank(v)]
    numeric = [v for v in nonblank if _is_number_like(v)]
    labels = [v for v in nonblank if not _is_number_like(v)]
    cleaned = [_clean_cell(v) for v in labels]
    duplicates = len(cleaned) - len(set(cleaned))
    blanks = len(values) - len(nonblank)
    return {
        "nonblank": len(nonblank),
        "numeric": len(numeric),
        "labels": len(labels),
        "duplicates": duplicates,
        "blanks": blanks,
        "score": len(labels) * 2.0 - len(numeric) * 1.5 + duplicates * 0.4,
    }


def _looks_like_group_header(row: pd.Series) -> bool:
    f = _row_features(row)
    if f["labels"] < 2 or f["numeric"] > max(1, f["labels"] // 2):
        return False
    blank_ratio = f["blanks"] / max(1, len(row))
    duplicate_ratio = f["duplicates"] / max(1, f["labels"])
    return blank_ratio > 0.15 or duplicate_ratio > 0.15


def _looks_like_header_detail(row: pd.Series) -> bool:
    f = _row_features(row)
    return f["labels"] >= 2 and f["numeric"] <= max(1, f["labels"] // 3)


def _make_unique(columns: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for idx, column in enumerate(columns, start=1):
        name = column.strip(" _")
        if not name:
            name = f"未命名_{idx}"
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.append(name if count == 0 else f"{name}_{count + 1}")
    return result


def _combine_header_rows(raw: pd.DataFrame, start: int, end: int) -> list[str]:
    header = raw.iloc[start : end + 1].copy()
    filled = header.apply(lambda row: row.map(_clean_cell).replace("", np.nan).ffill(), axis=1).fillna("")
    columns: list[str] = []
    for col_idx in range(filled.shape[1]):
        parts: list[str] = []
        for row_idx in range(filled.shape[0]):
            part = _clean_cell(filled.iat[row_idx, col_idx])
            if part and part not in parts:
                parts.append(part)
        columns.append("_".join(parts))
    return _make_unique(columns)


def infer_schema(excel_bytes: bytes, sheet_name: str, scan_rows: int = 12) -> SheetSchema:
    raw = pd.read_excel(BytesIO(excel_bytes), sheet_name=sheet_name, header=None, nrows=scan_rows, dtype=object, engine="openpyxl")
    raw = raw.dropna(axis=1, how="all")
    if raw.empty:
        return SheetSchema(sheet_name, 0, 0, [], 0, 0)

    if sheet_name in BASE_DATA_SHEETS:
        columns = _combine_header_rows(raw, 0, 0)
        xls = pd.ExcelFile(BytesIO(excel_bytes), engine="openpyxl")
        try:
            ws = xls.book[sheet_name]
            return SheetSchema(sheet_name, 0, 0, columns, int(ws.max_row or 0), int(ws.max_column or len(columns)))
        except Exception:
            return SheetSchema(sheet_name, 0, 0, columns, 0, len(columns))

    features = [_row_features(raw.iloc[i]) for i in range(len(raw))]
    header_idx = max(range(len(features)), key=lambda i: features[i]["score"])

    start = header_idx
    while start > 0 and _looks_like_group_header(raw.iloc[start - 1]):
        start -= 1

    end = header_idx
    while end + 1 < len(raw) and _looks_like_group_header(raw.iloc[end]) and _looks_like_header_detail(raw.iloc[end + 1]):
        end += 1

    columns = _combine_header_rows(raw, start, end)

    xls = pd.ExcelFile(BytesIO(excel_bytes), engine="openpyxl")
    rows = 0
    cols = len(columns)
    try:
        ws = xls.book[sheet_name]
        rows = int(ws.max_row or 0)
        cols = int(ws.max_column or cols)
    except Exception:
        pass
    return SheetSchema(sheet_name, start, end, columns, rows, cols)


def load_sheet(excel_bytes: bytes, sheet_name: str) -> tuple[pd.DataFrame, SheetSchema]:
    schema = infer_schema(excel_bytes, sheet_name)
    if not schema.columns:
        return pd.DataFrame(), schema
    data = pd.read_excel(
        BytesIO(excel_bytes),
        sheet_name=sheet_name,
        header=None,
        skiprows=schema.header_end + 1,
        dtype=object,
        engine="openpyxl",
    )
    data = data.dropna(axis=0, how="all")
    columns = schema.columns[: data.shape[1]]
    if len(columns) < data.shape[1]:
        columns.extend([f"未命名_{i}" for i in range(len(columns) + 1, data.shape[1] + 1)])
    data.columns = _make_unique(columns)
    data = data.dropna(axis=1, how="all")
    data = data.reset_index(drop=True)
    return coerce_frame(data), schema


def coerce_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].map(lambda x: _clean_cell(x) if isinstance(x, str) else x)
        if any(key in str(col) for key in ["编码", "编号", "ID", "月份", "日期", "时间"]):
            out[col] = out[col].map(lambda x: "" if _is_blank(x) else _clean_cell(x))
            continue
        numeric = pd.to_numeric(out[col], errors="coerce")
        if numeric.notna().sum() >= max(3, int(out[col].notna().sum() * 0.65)):
            out[col] = numeric
        elif out[col].dtype == "object":
            out[col] = out[col].map(lambda x: "" if _is_blank(x) else _clean_cell(x))
    return out


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not any(k in str(c) for k in ["编码", "编号", "序号", "排名"])]


def _match_column(columns: list[str], keywords: list[str], df: pd.DataFrame | None = None, dim: str | None = None) -> str | None:
    def allowed(column: str) -> bool:
        if df is not None and column in df.columns and dim != "月份" and pd.api.types.is_numeric_dtype(df[column]):
            return False
        if dim == "区域" and any(bad in column for bad in ["是否", "特殊区域"]):
            return False
        if dim == "加盟商" and "属性" in column:
            return False
        return True

    for keyword in keywords:
        exact = [c for c in columns if allowed(c) and (c == keyword or str(c).endswith("_" + keyword))]
        if exact:
            return exact[0]
    for keyword in keywords:
        partial = [c for c in columns if allowed(c) and keyword in str(c)]
        if partial:
            return partial[0]
    return None


def detect_dimensions(df: pd.DataFrame) -> dict[str, str]:
    columns = list(map(str, df.columns))
    dims: dict[str, str] = {}
    for dim, keywords in DIMENSION_KEYWORDS.items():
        col = _match_column(columns, keywords, df=df, dim=dim)
        if col is not None:
            dims[dim] = col
    return dims


def _metric_score(column: str) -> int:
    for idx, keyword in enumerate(METRIC_PRIORITY):
        if keyword in column:
            return 10_000 - idx * 100 + min(len(column), 50)
    if any(keyword in column for keyword in SUM_METRIC_KEYWORDS + AVG_METRIC_KEYWORDS):
        return 100
    return 0


def detect_metrics(df: pd.DataFrame) -> list[str]:
    nums = numeric_columns(df)
    ranked = sorted(nums, key=lambda c: (_metric_score(str(c)), -len(str(c))), reverse=True)
    return [c for c in ranked if _metric_score(str(c)) > 0] or nums[:12]


def metric_aggregation(column: str) -> str:
    if any(keyword in column for keyword in AVG_METRIC_KEYWORDS):
        return "mean"
    return "sum"


def aggregate_metric(df: pd.DataFrame, column: str) -> float:
    series = pd.to_numeric(df[column], errors="coerce")
    if metric_aggregation(column) == "mean":
        return float(series.mean()) if series.notna().any() else 0.0
    return float(series.sum()) if series.notna().any() else 0.0


def build_profile(sheet_name: str, df: pd.DataFrame) -> SheetProfile:
    dimensions = detect_dimensions(df)
    metrics = detect_metrics(df)
    if sheet_name in BASE_DATA_SHEETS:
        page_type = "基础档案/配置表"
    elif "明细" in sheet_name or "报表" in sheet_name or "汇总表" in sheet_name:
        page_type = "业务明细页"
    else:
        page_type = "业务分析页"
    modules = PAGE_MODULES.get(sheet_name, ["generic_summary", "rank_analysis", "abnormal_list"])
    if sheet_name in BASE_DATA_SHEETS:
        modules = ["quality_overview", "detail_table", "quality_check"]
    return SheetProfile(sheet_name, page_type, dimensions, metrics, metrics[:5], modules)


def apply_filters(df: pd.DataFrame, filters: dict[str, list[str]], dimensions: dict[str, str]) -> pd.DataFrame:
    out = df
    for dim, values in filters.items():
        column = dimensions.get(dim)
        if not column or not values or column not in out.columns:
            continue
        out = out[out[column].astype(str).isin(values)]
    return out


def kpi_rows(df: pd.DataFrame, profile: SheetProfile) -> list[dict[str, Any]]:
    rows = []
    for metric in profile.kpi_metrics[:5]:
        value = aggregate_metric(df, metric)
        rows.append(
            {
                "指标": metric,
                "当前值": value,
                "计算口径": "平均" if metric_aggregation(metric) == "mean" else "求和",
                "目标达成率": infer_target_rate(df, metric),
            }
        )
    return rows


def infer_target_rate(df: pd.DataFrame, metric: str) -> float | None:
    target_cols = [c for c in numeric_columns(df) if ("目标" in str(c) or "指标" in str(c)) and c != metric]
    if not target_cols:
        return None
    target = pd.to_numeric(df[target_cols[0]], errors="coerce").sum()
    current = aggregate_metric(df, metric)
    if not target:
        return None
    return current / target


def rank_table(df: pd.DataFrame, dimension: str | None, metric: str | None, n: int = 10, ascending: bool = False) -> pd.DataFrame:
    if not dimension or not metric or dimension not in df.columns or metric not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby(dimension, dropna=False)[metric].apply(lambda s: pd.to_numeric(s, errors="coerce").sum()).reset_index()
    grouped = grouped.rename(columns={metric: "指标值"}).sort_values("指标值", ascending=ascending).head(n)
    return grouped


def distribution_table(df: pd.DataFrame, metric: str | None, bins: int = 8) -> pd.DataFrame:
    if not metric or metric not in df.columns:
        return pd.DataFrame()
    series = pd.to_numeric(df[metric], errors="coerce").dropna()
    if series.empty:
        return pd.DataFrame()
    cats = pd.cut(series, bins=min(bins, max(1, series.nunique())), duplicates="drop")
    counts = cats.value_counts().sort_index().reset_index()
    counts.columns = ["区间", "数量"]
    return counts


def financial_structure(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    nums = numeric_columns(df)
    for bucket, keywords in FINANCIAL_BUCKETS.items():
        cols = [c for c in nums if any(keyword in str(c) for keyword in keywords)]
        value = float(sum(pd.to_numeric(df[c], errors="coerce").sum() for c in cols)) if cols else 0.0
        rows.append({"类别": bucket, "金额": value, "匹配字段数": len(cols)})
    return pd.DataFrame(rows)


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["检查项", "结果"])
    duplicate_count = int(df.duplicated().sum())
    null_cells = int(df.isna().sum().sum())
    blank_strings = int((df.astype(str).apply(lambda s: s.str.strip().eq(""))).sum().sum())
    rows = [
        {"检查项": "数据行数", "结果": len(df)},
        {"检查项": "字段数量", "结果": len(df.columns)},
        {"检查项": "重复行数", "结果": duplicate_count},
        {"检查项": "空值单元格数", "结果": null_cells + blank_strings},
    ]
    for col in df.columns[:50]:
        missing = int(df[col].isna().sum() + df[col].astype(str).str.strip().eq("").sum())
        if missing:
            rows.append({"检查项": f"{col} 空值", "结果": missing})
    return pd.DataFrame(rows)


def abnormal_rows(df: pd.DataFrame, limit: int = 200) -> pd.DataFrame:
    nums = numeric_columns(df)
    if not nums:
        return pd.DataFrame()
    flags = pd.Series(False, index=df.index)
    for col in nums:
        series = pd.to_numeric(df[col], errors="coerce")
        if any(k in str(col) for k in ["费", "金额", "贡献", "补贴", "扣款", "考核"]):
            flags = flags | series.lt(0) | series.eq(0)
        high = series.quantile(0.99)
        if pd.notna(high) and high != 0:
            flags = flags | series.gt(high)
    return df.loc[flags].head(limit)


def page_period(df: pd.DataFrame, dimensions: dict[str, str]) -> str:
    column = dimensions.get("月份")
    if not column or column not in df.columns:
        return "全部周期"
    values = [v for v in df[column].dropna().astype(str).unique().tolist() if v.strip()]
    if not values:
        return "全部周期"
    values = sorted(values)
    return values[0] if len(values) == 1 else f"{values[0]} - {values[-1]}"

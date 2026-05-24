"""数据预处理：从原始 CSV 列算出 revenue / profit / cost。

v1 dashboard.py 把这部分计算混在 UI 加载逻辑里。v2 抽出来做成纯函数，
让 CLI 和外部脚本能复用。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_orders(path: str) -> pd.DataFrame:
    """加载订单 CSV 并补全 revenue / cost / profit 列。"""
    df = pd.read_csv(path)
    return prepare_orders(df)


def prepare_orders(df: pd.DataFrame) -> pd.DataFrame:
    """补 revenue / cost / profit 列；幂等。"""
    df = df.copy()
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    if "revenue" not in df.columns:
        df["revenue"] = df["quantity"] * df["unit_price"]
    if "cost" not in df.columns and "cost_price" in df.columns:
        df["cost"] = df["quantity"] * df["cost_price"]
    if "profit" not in df.columns:
        if "cost" in df.columns:
            df["profit"] = df["revenue"] - df["cost"]
        elif "cost_price" in df.columns:
            df["profit"] = df["revenue"] - df["quantity"] * df["cost_price"]
        else:
            df["profit"] = df["revenue"]    # 没有成本列 → profit = revenue
    return df


def load_products(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "last_restock_date" in df.columns:
        df["last_restock_date"] = pd.to_datetime(df["last_restock_date"],
                                                  errors="coerce")
    return df


def load_campaigns(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for c in ("start_date", "end_date"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def overview_metrics(orders_df: pd.DataFrame) -> dict:
    """整体 KPI：总单数 / 总营收 / 总利润 / 利润率 / 平均客单价。"""
    if len(orders_df) == 0:
        return {"n_orders": 0, "total_revenue": 0.0, "total_profit": 0.0,
                "profit_margin_pct": 0.0, "avg_order_value": 0.0,
                "unique_customers": 0}
    n_orders = int(len(orders_df))
    total_revenue = float(orders_df["revenue"].sum())
    total_profit = float(orders_df["profit"].sum()) if "profit" in orders_df.columns else 0.0
    margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0.0
    aov = total_revenue / n_orders if n_orders else 0.0
    n_customers = int(orders_df["customer_id"].nunique()) if "customer_id" in orders_df.columns else 0

    return {
        "n_orders": n_orders,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_margin_pct": float(margin_pct),
        "avg_order_value": float(aov),
        "unique_customers": n_customers,
    }

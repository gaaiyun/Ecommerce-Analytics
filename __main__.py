"""Ecommerce-Analytics CLI（v2）。

子命令：
    overview      整体 KPI
    orders        订单趋势 / 地域 / 城市
    products      产品分析（畅销 / 滞销 / 库存预警）
    marketing     营销 ROI / 转化率 / 渠道
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from data_prep import (
    load_campaigns, load_orders, load_products, overview_metrics,
)
from order_analyzer import OrderAnalyzer
from product_analyzer import ProductAnalyzer
from marketing_analyzer import MarketingAnalyzer


def _df_to_dict(df: pd.DataFrame) -> list:
    """DataFrame → JSON-friendly list of dict（datetime 转 str）。"""
    if df is None or len(df) == 0:
        return []
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")


def cmd_overview(args) -> int:
    orders = load_orders(args.orders)
    metrics = overview_metrics(orders)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(metrics, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    return 0


def cmd_orders(args) -> int:
    orders = load_orders(args.orders)
    analyzer = OrderAnalyzer(orders)
    payload = {
        "trend": _df_to_dict(analyzer.get_order_trend(period=args.period)),
        "regional": _df_to_dict(analyzer.get_regional_distribution()),
        "top_cities": _df_to_dict(analyzer.get_city_analysis(top_n=args.top_n)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    return 0


def cmd_products(args) -> int:
    orders = load_orders(args.orders)
    products = load_products(args.products) if args.products else None
    analyzer = ProductAnalyzer(orders, products) if products is not None else ProductAnalyzer(orders)

    payload = {}
    try:
        payload["category_analysis"] = _df_to_dict(analyzer.get_category_analysis())
    except Exception as e:
        payload["category_analysis"] = {"error": str(e)}
    try:
        payload["top_sellers"] = _df_to_dict(analyzer.get_top_sellers(top_n=args.top_n))
    except Exception as e:
        payload["top_sellers"] = {"error": str(e)}
    if products is not None:
        try:
            payload["low_stock"] = _df_to_dict(analyzer.get_low_stock_products())
        except Exception as e:
            payload["low_stock"] = {"error": str(e)}

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    return 0


def cmd_marketing(args) -> int:
    orders = load_orders(args.orders)
    campaigns = load_campaigns(args.campaigns)
    analyzer = MarketingAnalyzer(campaigns, orders)
    payload = {
        "roi": _df_to_dict(analyzer.get_campaign_roi()),
        "conversion": _df_to_dict(analyzer.get_conversion_metrics()),
    }
    try:
        payload["channel"] = _df_to_dict(analyzer.get_channel_analysis())
    except Exception:
        pass
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ecom",
                                description="电商数据 headless CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("overview", help="整体 KPI")
    sp.add_argument("--orders", required=True)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_overview)

    sp = sub.add_parser("orders", help="订单趋势 / 地域 / 城市")
    sp.add_argument("--orders", required=True)
    sp.add_argument("--period", default="D", choices=["D", "W", "ME", "M"])
    sp.add_argument("--top-n", type=int, default=10)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_orders)

    sp = sub.add_parser("products", help="品类 / 畅销 / 库存预警")
    sp.add_argument("--orders", required=True)
    sp.add_argument("--products", help="products CSV（含库存信息时才能查低库存）")
    sp.add_argument("--top-n", type=int, default=10)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_products)

    sp = sub.add_parser("marketing", help="活动 ROI / 转化率 / 渠道")
    sp.add_argument("--orders", required=True)
    sp.add_argument("--campaigns", required=True)
    sp.add_argument("-o", "--output")
    sp.set_defaults(func=cmd_marketing)

    return p


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

from datetime import datetime
from playwright.sync_api import sync_playwright
from report_data import get_report_data


def build_html(report):
    today = datetime.now().strftime("%Y-%m-%d")

    top_products_rows = "".join(
        f"<tr><td>{p['product']}</td><td>${p['revenue']:.2f}</td></tr>"
        for p in report["top_products"]
    )

    all_orders_rows = "".join(
        f"<tr><td>{o['customer']}</td><td>{o['product']}</td>"
        f"<td>${o['amount']:.2f}</td><td>{o['created_at']}</td></tr>"
        for o in report["all_orders"]
    )

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #222; margin: 40px; }}
            h1 {{ font-size: 22px; margin-bottom: 0; }}
            .date {{ color: #666; margin-top: 4px; margin-bottom: 24px; }}
            .totals {{ display: flex; gap: 40px; margin-bottom: 24px; }}
            .totals div {{ font-size: 16px; }}
            .totals strong {{ display: block; font-size: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
            th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #ddd; font-size: 13px; }}
            th {{ background: #f4f4f4; }}
            tr {{ break-inside: avoid; }}
            h2 {{ font-size: 16px; margin-top: 32px; }}
        </style>
    </head>
    <body>
        <h1>Sales Report</h1>
        <div class="date">Generated on {today}</div>

        <div class="totals">
            <div>Total orders<strong>{report['total_orders']}</strong></div>
            <div>Total revenue<strong>${report['total_revenue']:.2f}</strong></div>
        </div>

        <h2>Top 5 products by revenue</h2>
        <table>
            <thead><tr><th>Product</th><th>Revenue</th></tr></thead>
            <tbody>{top_products_rows}</tbody>
        </table>

        <h2>All orders ({report['total_orders']})</h2>
        <table>
            <thead><tr><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr></thead>
            <tbody>{all_orders_rows}</tbody>
        </table>
    </body>
    </html>
    """


def render_pdf(html, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("reports", exist_ok=True)
    report = get_report_data()
    html = build_html(report)
    render_pdf(html, "reports/test.pdf")
    print("Wrote reports/test.pdf")
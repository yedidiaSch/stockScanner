import yfinance as yf

def get_fundamental_report(symbol):
    """
    Generates an HTML report of fundamental data for a given stock symbol.

    Parameters:
        symbol (str): Stock ticker symbol.

    Returns:
        str: HTML string containing the fundamental report.
    """
    t = yf.Ticker(symbol)
    info = t.info

    # Extract short and long names
    short_name = info.get("shortName", "N/A")
    long_name = info.get("longName", "N/A")

    html = f"""
    <h3>{symbol.upper()} - Fundamental Report</h3>
    <p><b>Short Name:</b> {short_name}<br>
    <b>Long Name:</b> {long_name}</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>EPS</th><td>{info.get("trailingEps", "N/A")}</td></tr>
      <tr><th>P/E Ratio</th><td>{info.get("trailingPE", "N/A")}</td></tr>
    </table>
    """

    # Revenue Table
    try:
        income_stmt = t.financials
        revenues = income_stmt.loc["Total Revenue"]
        net_incomes = income_stmt.loc["Net Income"]

        html += """
        <h4>Revenue & Net Income per Year</h4>
        <table border="1" cellpadding="6" cellspacing="0">
          <tr><th>Date</th><th>Revenue</th><th>Net Income</th><th>Revenue Change YoY</th></tr>
        """

        last_rev = None
        for date in revenues.index:
            rev = revenues[date]
            ni = net_incomes.get(date, None)
            ni_text = f"{ni:,.0f}" if ni else "N/A"
            change = "N/A"
            if last_rev:
                change = f"{((rev - last_rev) / last_rev) * 100:.2f}%"
            html += f"<tr><td>{date.date()}</td><td>{rev:,.0f}</td><td>{ni_text}</td><td>{change}</td></tr>"
            last_rev = rev

        html += "</table>"
    except Exception:
        html += "<p><i>Revenue data not available.</i></p>"

    # Net Profit Margin
    try:
        if "Net Income" in income_stmt.index and "Total Revenue" in income_stmt.index:
            ni = income_stmt.loc["Net Income"].iloc[0]
            rev = income_stmt.loc["Total Revenue"].iloc[0]
            net_margin = (ni / rev) * 100
            html += f"<p><b>Net Profit Margin:</b> {net_margin:.2f}%</p>"
    except Exception:
        pass

    # Debt/Equity and ROE
    try:
        balance = t.balance_sheet
        if "Total Liab" in balance.index and "Total Stockholder Equity" in balance.index:
            tl = balance.loc["Total Liab"].iloc[0]
            eq = balance.loc["Total Stockholder Equity"].iloc[0]
            if eq != 0:
                de = tl / eq
                html += f"<p><b>Debt/Equity Ratio:</b> {de:.2f}</p>"
                if "Net Income" in income_stmt.index:
                    roe = (ni / eq) * 100
                    html += f"<p><b>Return on Equity (ROE):</b> {roe:.2f}%</p>"
    except Exception:
        pass

    return html

import yfinance as yf
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_fundamental_report(symbol: str) -> str:
    """
    Generates an HTML report of fundamental data for a given stock symbol.

    Parameters:
        symbol (str): Stock ticker symbol.

    Returns:
        str: HTML string containing the fundamental report.
        
    Raises:
        ValueError: If symbol is invalid.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string")
    
    symbol = symbol.strip().upper()
    
    try:
        logger.debug(f"Fetching fundamental data for {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or 'symbol' not in info:
            logger.warning(f"No fundamental data available for {symbol}")
            return create_unavailable_report(symbol)

        # Extract basic info with fallbacks
        short_name = info.get("shortName", "N/A")
        long_name = info.get("longName", "N/A")
        
        html = f"""
        <div class="fundamental-report">
        <h3>{symbol} - Fundamental Analysis</h3>
        <div class="company-info">
            <p><strong>Short Name:</strong> {short_name}</p>
            <p><strong>Long Name:</strong> {long_name}</p>
        </div>
        """

        # Key metrics table
        html += create_key_metrics_table(info)
        
        # Revenue table
        html += create_revenue_table(ticker, symbol)
        
        # Additional metrics
        html += create_additional_metrics(ticker, info)
        
        html += "</div>"
        
        return html

    except Exception as e:
        logger.error(f"Error generating fundamental report for {symbol}: {e}")
        return create_error_report(symbol, str(e))


def create_unavailable_report(symbol: str) -> str:
    """Create report when fundamental data is unavailable."""
    return f"""
    <div class="fundamental-report">
    <h3>{symbol} - Fundamental Analysis</h3>
    <p class="warning">⚠️ Fundamental data not available for this symbol.</p>
    </div>
    """


def create_error_report(symbol: str, error_msg: str) -> str:
    """Create report when an error occurs.""" 
    return f"""
    <div class="fundamental-report">
    <h3>{symbol} - Fundamental Analysis</h3>
    <p class="error">❌ Error retrieving data: {error_msg}</p>
    </div>
    """


def create_key_metrics_table(info: dict) -> str:
    """Create table of key financial metrics."""
    eps = info.get("trailingEps", "N/A")
    pe_ratio = info.get("trailingPE", "N/A")
    market_cap = info.get("marketCap", "N/A")
    
    # Format market cap if available
    if isinstance(market_cap, (int, float)):
        if market_cap > 1e12:
            market_cap = f"${market_cap/1e12:.2f}T"
        elif market_cap > 1e9:
            market_cap = f"${market_cap/1e9:.2f}B"
        elif market_cap > 1e6:
            market_cap = f"${market_cap/1e6:.2f}M"
        else:
            market_cap = f"${market_cap:,.0f}"
    
    return f"""
    <table class="metrics-table">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>EPS (Trailing)</td><td>{eps}</td></tr>
        <tr><td>P/E Ratio</td><td>{pe_ratio}</td></tr>
        <tr><td>Market Cap</td><td>{market_cap}</td></tr>
    </table>
    """


def create_revenue_table(ticker, symbol: str) -> str:
    """Create revenue and income table."""
    try:
        income_stmt = ticker.financials
        if income_stmt.empty:
            return "<p><i>Financial data not available.</i></p>"
            
        revenues = income_stmt.loc["Total Revenue"] if "Total Revenue" in income_stmt.index else None
        net_incomes = income_stmt.loc["Net Income"] if "Net Income" in income_stmt.index else None

        if revenues is None:
            return "<p><i>Revenue data not available.</i></p>"

        html = """
        <h4>📊 Revenue & Net Income (Annual)</h4>
        <table class="financial-table">
          <tr><th>Year</th><th>Revenue</th><th>Net Income</th><th>YoY Growth</th></tr>
        """

        last_rev = None
        # Sort by date descending (most recent first)
        for date in sorted(revenues.index, reverse=True)[:4]:  # Last 4 years
            rev = revenues[date]
            ni = net_incomes.get(date, None) if net_incomes is not None else None
            
            # Format values
            ni_text = f"${ni:,.0f}" if ni and not pd.isna(ni) else "N/A"
            rev_text = f"${rev:,.0f}" if rev and not pd.isna(rev) else "N/A"
            
            # Calculate YoY growth
            growth = "N/A"
            if last_rev and not pd.isna(rev) and not pd.isna(last_rev) and last_rev != 0:
                growth_pct = ((rev - last_rev) / last_rev) * 100
                growth = f"{growth_pct:+.1f}%"
            
            html += f"""
            <tr>
                <td>{date.year}</td>
                <td>{rev_text}</td>
                <td>{ni_text}</td>
                <td>{growth}</td>
            </tr>
            """
            last_rev = rev

        html += "</table>"
        return html

    except Exception as e:
        logger.warning(f"Error creating revenue table for {symbol}: {e}")
        return "<p><i>Revenue data not available.</i></p>"


def create_additional_metrics(ticker, info: dict) -> str:
    """Create additional financial metrics."""
    try:
        metrics_html = "<h4>📈 Additional Metrics</h4><ul>"
        
        # Net Profit Margin
        try:
            income_stmt = ticker.financials
            if not income_stmt.empty and "Net Income" in income_stmt.index and "Total Revenue" in income_stmt.index:
                ni = income_stmt.loc["Net Income"].iloc[0]
                rev = income_stmt.loc["Total Revenue"].iloc[0]
                if rev != 0 and not pd.isna(ni) and not pd.isna(rev):
                    net_margin = (ni / rev) * 100
                    metrics_html += f"<li><strong>Net Profit Margin:</strong> {net_margin:.2f}%</li>"
        except:
            pass

        # Debt/Equity and ROE
        try:
            balance = ticker.balance_sheet
            if not balance.empty and "Total Liab" in balance.index and "Total Stockholder Equity" in balance.index:
                tl = balance.loc["Total Liab"].iloc[0]
                eq = balance.loc["Total Stockholder Equity"].iloc[0]
                if eq != 0 and not pd.isna(tl) and not pd.isna(eq):
                    de = tl / eq
                    metrics_html += f"<li><strong>Debt/Equity Ratio:</strong> {de:.2f}</li>"
        except:
            pass

        # Book Value Per Share
        book_value = info.get("bookValue")
        if book_value:
            metrics_html += f"<li><strong>Book Value/Share:</strong> ${book_value:.2f}</li>"

        # Dividend Yield
        div_yield = info.get("dividendYield")
        if div_yield:
            metrics_html += f"<li><strong>Dividend Yield:</strong> {div_yield*100:.2f}%</li>"

        metrics_html += "</ul>"
        return metrics_html

    except Exception as e:
        logger.warning(f"Error creating additional metrics: {e}")
        return ""

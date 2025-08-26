import pandas as pd
import glob
import os
import logging
import sys
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BACKTEST_RESULTS_PREFIX

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
TOTAL_CAPITAL = 50000  # This could be moved to config.py later


def load_backtest_results() -> List[str]:
    """Load all backtest result files."""
    result_files = glob.glob(f"{BACKTEST_RESULTS_PREFIX}*.csv")
    
    if not result_files:
        logger.error("No result files found.")
        raise FileNotFoundError("No backtest result files found")
    
    logger.info(f"Found {len(result_files)} result files")
    return result_files


def process_result_file(file_path: str) -> Optional[Dict]:
    """Process a single result file and extract trade data."""
    try:
        filename = os.path.basename(file_path)
        logger.debug(f"Processing {filename}")
        
        df = pd.read_csv(file_path)
        closed = df[df["pct_change"].notnull()]

        if closed.empty:
            logger.warning(f"{filename}: No closed trades.")
            return {
                "filename": filename,
                "trades": 0,
                "avg_pct": None,
                "pct_list": [],
                "market_list": [],
                "years": []
            }

        # Extract data
        pct_list = closed["pct_change"].tolist()
        market_list = closed["market"].tolist()

        # Extract dates for year grouping
        if "exit_date" in closed.columns and closed["exit_date"].notnull().any():
            dates = pd.to_datetime(closed["exit_date"], errors="coerce")
        else:
            dates = pd.to_datetime(closed["entry_date"], errors="coerce")

        years = dates.dt.year.tolist()
        avg_pct = sum(pct_list) / len(pct_list)

        return {
            "filename": filename,
            "trades": len(pct_list),
            "avg_pct": avg_pct,
            "pct_list": pct_list,
            "market_list": market_list,
            "years": years
        }
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


def calculate_portfolio_performance(all_pcts: List[float]) -> Dict:
    """Calculate portfolio performance metrics."""
    if not all_pcts:
        raise ValueError("No trades to analyze")
    
    total_trades = len(all_pcts)
    avg_pct = sum(all_pcts) / total_trades
    capital_per_trade = TOTAL_CAPITAL / total_trades
    
    # Calculate final amount
    final_amount = sum(capital_per_trade * (1 + pct / 100) for pct in all_pcts)
    
    # Calculate win rate
    winning_trades = sum(1 for pct in all_pcts if pct > 0)
    win_rate = (winning_trades / total_trades) * 100
    
    return {
        "total_trades": total_trades,
        "avg_pct": avg_pct,
        "final_amount": final_amount,
        "win_rate": win_rate,
        "winning_trades": winning_trades
    }


def create_market_summary(all_markets: List[str], all_pcts: List[float]) -> pd.DataFrame:
    """Create market performance summary."""
    market_df = pd.DataFrame({
        "Market": all_markets,
        "PctChange": all_pcts
    })
    
    return market_df.groupby("Market").agg(
        Trades=("PctChange", "count"),
        AvgPctChange=("PctChange", "mean"),
        WinRate=("PctChange", lambda x: (x > 0).mean() * 100)
    ).reset_index().sort_values("AvgPctChange", ascending=False)


def create_year_summary(all_years: List[int], all_pcts: List[float]) -> pd.DataFrame:
    """Create yearly performance summary."""
    year_df = pd.DataFrame({
        "Year": all_years,
        "PctChange": all_pcts
    })
    
    return year_df.groupby("Year").agg(
        Trades=("PctChange", "count"),
        AvgPctChange=("PctChange", "mean"),
        WinRate=("PctChange", lambda x: (x > 0).mean() * 100)
    ).reset_index().sort_values("Year")


def print_summary_tables(portfolio_metrics: Dict, market_summary: pd.DataFrame, 
                        year_summary: pd.DataFrame) -> None:
    """Print formatted summary tables."""
    
    # Portfolio summary
    print("\n📊 Portfolio Performance Summary:")
    print("=" * 50)
    print(f"Total Trades:           {portfolio_metrics['total_trades']:>10}")
    print(f"Winning Trades:         {portfolio_metrics['winning_trades']:>10}")
    print(f"Win Rate:              {portfolio_metrics['win_rate']:>9.1f}%")
    print(f"Average % per trade:   {portfolio_metrics['avg_pct']:>9.2f}%")
    print(f"Starting Capital:      ₪{TOTAL_CAPITAL:>10,.0f}")
    print(f"Final Amount:          ₪{portfolio_metrics['final_amount']:>10,.2f}")
    print(f"Total Return:          {((portfolio_metrics['final_amount']/TOTAL_CAPITAL-1)*100):>9.2f}%")

    # Market summary
    print("\n🌍 Performance by Market:")
    print("=" * 60)
    print(f"{'Market':<15} {'Trades':>8} {'Avg %':>10} {'Win Rate':>10}")
    print("-" * 60)
    for _, row in market_summary.iterrows():
        print(f"{row['Market']:<15} {row['Trades']:>8} {row['AvgPctChange']:>9.2f}% "
              f"{row['WinRate']:>9.1f}%")

    # Year summary  
    print("\n📅 Performance by Year:")
    print("=" * 50)
    print(f"{'Year':<8} {'Trades':>8} {'Avg %':>10} {'Win Rate':>10}")
    print("-" * 50)
    for _, row in year_summary.iterrows():
        print(f"{int(row['Year']):<8} {row['Trades']:>8} {row['AvgPctChange']:>9.2f}% "
              f"{row['WinRate']:>9.1f}%")


def save_reports(summary_rows: List[Dict], market_summary: pd.DataFrame, 
                year_summary: pd.DataFrame) -> None:
    """Save all summary reports to CSV files."""
    try:
        # Main summary
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv("summary_report.csv", index=False)
        logger.info("Summary report saved to 'summary_report.csv'")

        # Market summary
        market_summary.to_csv("market_summary_report.csv", index=False)
        logger.info("Market summary saved to 'market_summary_report.csv'")

        # Year summary
        year_summary.to_csv("year_summary_report.csv", index=False)
        logger.info("Year summary saved to 'year_summary_report.csv'")
        
    except Exception as e:
        logger.error(f"Error saving reports: {e}")
        raise


def cleanup_result_files(result_files: List[str]) -> None:
    """Clean up temporary result files."""
    try:
        for file_path in result_files:
            os.remove(file_path)
        logger.info("All result files have been deleted.")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")


def main():
    """Main function to process backtest results and generate reports."""
    try:
        # Load result files
        result_files = load_backtest_results()

        # Process all files
        summary_rows = []
        all_pcts = []
        all_markets = []
        all_years = []

        for file_path in result_files:
            result = process_result_file(file_path)
            
            if result is not None:
                summary_rows.append({
                    "File": result["filename"],
                    "Trades": result["trades"],
                    "Avg % Change": result["avg_pct"]
                })
                
                all_pcts.extend(result["pct_list"])
                all_markets.extend(result["market_list"])
                all_years.extend(result["years"])

        if not all_pcts:
            logger.error("No closed trades found in any files.")
            return

        # Calculate performance metrics
        portfolio_metrics = calculate_portfolio_performance(all_pcts)
        
        # Add total row to summary
        summary_rows.append({
            "File": "TOTAL",
            "Trades": portfolio_metrics["total_trades"],
            "Avg % Change": portfolio_metrics["avg_pct"]
        })

        # Create summaries
        market_summary = create_market_summary(all_markets, all_pcts)
        year_summary = create_year_summary(all_years, all_pcts)

        # Display results
        print_summary_tables(portfolio_metrics, market_summary, year_summary)

        # Save reports
        save_reports(summary_rows, market_summary, year_summary)

        # Cleanup
        cleanup_result_files(result_files)

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()

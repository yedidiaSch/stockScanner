import pandas as pd
import glob
import os

# Constants
TOTAL_CAPITAL = 50000

# Find all result files
result_files = glob.glob("backtest_results_*.csv")

if not result_files:
    print("⚠️ No result files found.")
    exit()

# Initialize summary variables
summary_rows = []
all_pcts = []
all_markets = []
all_years = []
all_years_markets = []

# Process each result file
for file_path in result_files:
    filename = os.path.basename(file_path)
    df = pd.read_csv(file_path)
    closed = df[df["pct_change"].notnull()]

    if closed.empty:
        print(f"🔹 {filename}: No closed trades.")
        summary_rows.append({
            "File": filename,
            "Trades": 0,
            "Avg % Change": None
        })
        continue

    # Extract percentage changes and market data
    pct_list = closed["pct_change"].tolist()
    market_list = closed["market"].tolist()

    # Extract dates for year grouping
    if "exit_date" in closed.columns and closed["exit_date"].notnull().any():
        dates = pd.to_datetime(closed["exit_date"], errors="coerce")
    else:
        dates = pd.to_datetime(closed["entry_date"], errors="coerce")

    years = dates.dt.year.tolist()

    # Aggregate data
    all_pcts.extend(pct_list)
    all_markets.extend(market_list)
    all_years.extend(years)

    # Combine year and market for cross-grouping
    years_markets = [f"{year}_{market}" for year, market in zip(years, market_list)]
    all_years_markets.extend(years_markets)

    # Calculate average percentage change for the file
    avg_pct_file = sum(pct_list) / len(pct_list)

    summary_rows.append({
        "File": filename,
        "Trades": len(pct_list),
        "Avg % Change": avg_pct_file
    })

if not all_pcts:
    print("\n⚠️ No closed trades at all.")
    exit()

# Global summary calculations
avg_pct = sum(all_pcts) / len(all_pcts)
capital_per_trade = TOTAL_CAPITAL / len(all_pcts)
final_amount = 0
for pct in all_pcts:
    final_amount += capital_per_trade * (1 + pct / 100)

# Print global summary
print("\n📊 Global Summary:")
print(f"- Total trades:           {len(all_pcts):>5}")
print(f"- Average % per trade:   {avg_pct:>6.2f}%")
print(f"- Final amount (from {TOTAL_CAPITAL:,.0f} ₪): {final_amount:,.2f} ₪")

# Save global summary to CSV
summary_rows.append({
    "File": "TOTAL",
    "Trades": len(all_pcts),
    "Avg % Change": avg_pct
})
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv("summary_report.csv", index=False)
print("\n✅ Summary report saved to 'summary_report.csv'")

# Market summary
market_df = pd.DataFrame({
    "Market": all_markets,
    "PctChange": all_pcts
})
grouped_market = market_df.groupby("Market").agg(
    Trades=("PctChange", "count"),
    AvgPctChange=("PctChange", "mean")
).reset_index()

# Print market summary
print("\n🌍 Performance by Market:")
print(f"{'Market':<15} {'Trades':>6} {'Avg %':>8}")
print("-" * 32)
for idx, row in grouped_market.iterrows():
    print(f"{row['Market']:<15} {row['Trades']:>6} {row['AvgPctChange']:>8.2f}%")

# Save market summary to CSV
grouped_market.to_csv("market_summary_report.csv", index=False)
print("\n✅ Market summary report saved to 'market_summary_report.csv'")

# Year summary
year_df = pd.DataFrame({
    "Year": all_years,
    "PctChange": all_pcts
})
grouped_years = year_df.groupby("Year").agg(
    Trades=("PctChange", "count"),
    AvgPctChange=("PctChange", "mean")
).reset_index().sort_values("Year")

# Print year summary
print("\n📅 Performance by Year:")
print(f"{'Year':<6} {'Trades':>6} {'Avg %':>8}")
print("-" * 25)
for idx, row in grouped_years.iterrows():
    print(f"{int(row['Year']):<6} {row['Trades']:>6} {row['AvgPctChange']:>8.2f}%")

# Save year summary to CSV
grouped_years.to_csv("year_summary_report.csv", index=False)
print("\n✅ Year summary report saved to 'year_summary_report.csv'")

# Year + Market summary
year_market_df = pd.DataFrame({
    "Year_Market": all_years_markets,
    "PctChange": all_pcts
})

# Split combined columns back into separate year and market columns
year_market_df[['Year', 'Market']] = year_market_df['Year_Market'].str.split('_', expand=True)
year_market_df['Year'] = year_market_df['Year'].astype(int)

grouped_year_market = year_market_df.groupby(['Year', 'Market']).agg(
    Trades=("PctChange", "count"),
    AvgPctChange=("PctChange", "mean")
).reset_index().sort_values(["Year", "Market"])

# Print year + market summary
print("\n📅🌍 Performance by Year & Market:")
print(f"{'Year':<6} {'Market':<12} {'Trades':>6} {'Avg %':>8}")
print("-" * 40)
for idx, row in grouped_year_market.iterrows():
    print(f"{int(row['Year']):<6} {row['Market']:<12} {row['Trades']:>6} {row['AvgPctChange']:>8.2f}%")

# Save year + market summary to CSV
grouped_year_market.to_csv("year_market_summary_report.csv", index=False)
print("\n✅ Year & Market summary report saved to 'year_market_summary_report.csv'")

# Delete all result files
for file_path in result_files:
    os.remove(file_path)

print("\n✅ All result files have been deleted.")

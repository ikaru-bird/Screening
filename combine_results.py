import pandas as pd
import glob
import os

def combine_csvs(file_pattern, output_file):
    """
    Finds all CSV files matching a pattern, concatenates them,
    and saves the result to a new CSV file.
    """
    files = glob.glob(file_pattern)
    if not files:
        print(f"No files found for pattern: {file_pattern}")
        return

    df_list = [pd.read_csv(f) for f in files]
    combined_df = pd.concat(df_list, ignore_index=True)

    # This is a stock file. Sort by Relative Strength and re-rank.
    combined_df = combined_df.sort_values('Relative Strength', ascending=False)
    combined_df.drop_duplicates(subset=['Ticker'], keep='first', inplace=True)
    combined_df['Rank'] = range(1, len(combined_df) + 1)
    combined_df = combined_df.set_index('Rank', drop=True)

    combined_df.to_csv(output_file)
    print(f"Combined {len(files)} files into {output_file}")


def recalculate_industries(combined_stocks_file, output_industries_file):
    """
    Recalculates the industry rankings from the combined stock data.
    This is more accurate than just merging the partial industry files.
    """
    stocks_df = pd.read_csv(combined_stocks_file, index_col='Rank')

    # Define columns to aggregate. Exclude the RS_*W/M columns that were dropped.
    agg_cols = ['Industry','Relative Strength','Diff','RS Momentum','RM_1W','RM_1M','RM_3M','RM_6M']

    # This logic is copied from RelativeStrength.py
    rs_sector = stocks_df[agg_cols].groupby('Industry').mean()
    rs_sector = rs_sector.sort_values('Relative Strength', ascending=False)
    rs_sector2 = rs_sector.reset_index(drop=False)

    rs_sector2['Rank'] = rs_sector2.index + 1

    # Re-calculate percentiles on the main RS column
    total_rows = len(rs_sector2)
    rs_sector2['Percentile'] = (rs_sector2['Relative Strength'].rank(ascending=True, method='average') - 1) / (total_rows - 1) * 100
    rs_sector2['Percentile'] = rs_sector2['Percentile'].round().clip(1, 99).astype(int)

    # We cannot calculate percentiles for RS_1W etc. as they are not in the source stocks_df
    # We also cannot calculate the 'Diff' column accurately without RS_1W.
    # The original script calculates Diff on the stock level, then averages it. We will do the same.
    # The 'Diff' column is already averaged by the groupby().mean() call above.

    rs_sector2['Tickers'] = ""
    for sector_name in rs_sector2['Industry']:
        tickers_str = ','.join(stocks_df[stocks_df['Industry'] == sector_name]['Ticker'].tolist())
        rs_sector2.loc[rs_sector2['Industry'] == sector_name, 'Tickers'] = tickers_str

    rs_sector2 = rs_sector2.set_index('Rank', drop=True)

    # We don't need to drop columns as we didn't include them in the aggregation

    rs_sector2.to_csv(output_industries_file)
    print(f"Recalculated and saved industry data to {output_industries_file}")


if __name__ == "__main__":
    # Combine stock files
    stock_pattern = '_files/RS/us_results/rs_stocks_us_*.csv'
    final_stock_file = '_files/RS/rs_stocks_us.csv'
    combine_csvs(stock_pattern, final_stock_file)

    # Recalculate industries from the combined stock file
    final_industry_file = '_files/RS/rs_industries_us.csv'
    recalculate_industries(final_stock_file, final_industry_file)

import pandas as pd
import glob
import os

def calculate_percentile(df, column_name, result_column_name):
    """A helper function to calculate and assign percentiles."""
    total_rows = len(df)
    if total_rows > 1:
        df[result_column_name] = (df[column_name].rank(ascending=True, method='average') - 1) / (total_rows - 1) * 100
    else:
        df[result_column_name] = 100
    df[result_column_name] = df[result_column_name].round().clip(1, 99).astype(int)
    return df

def combine_and_process_data(results_dir, stocks_pattern, industries_pattern, final_stocks_file, final_industries_file):
    """
    Main logic to combine and process chunked results.
    """
    # 1. Combine all stock results into a single DataFrame
    stock_files = glob.glob(os.path.join(results_dir, stocks_pattern))
    if not stock_files:
        print(f"No stock files found for pattern: {stocks_pattern}")
        return

    print(f"Combining {len(stock_files)} stock data files...")
    stock_df_list = [pd.read_csv(f) for f in stock_files]
    combined_stocks_df = pd.concat(stock_df_list, ignore_index=True)
    combined_stocks_df.drop_duplicates(subset=['Ticker'], keep='first', inplace=True)

    # 2. Recalculate ranks and percentiles for the combined stocks
    combined_stocks_df.sort_values('Relative Strength', ascending=False, inplace=True)
    combined_stocks_df.reset_index(drop=True, inplace=True)
    combined_stocks_df['Rank'] = range(1, len(combined_stocks_df) + 1)

    percentile_cols = {
        'Relative Strength': 'Percentile', 'RS_1W': '1 Week Ago', 'RS_1M': '1 Month Ago',
        'RS_3M': '3 Months Ago', 'RS_6M': '6 Months Ago'
    }
    for data_col, percentile_col in percentile_cols.items():
        combined_stocks_df = calculate_percentile(combined_stocks_df, data_col, percentile_col)

    # 3. Recalculate industry data from the combined stock data
    print("Recalculating industry rankings...")
    industry_cols = ['Industry', 'Relative Strength', 'Diff', 'RS_1W', 'RS_1M', 'RS_3M', 'RS_6M',
                     'RS Momentum', 'RM_1W', 'RM_1M', 'RM_3M', 'RM_6M']
    rs_sector = combined_stocks_df[industry_cols].groupby('Industry').mean()
    rs_sector.sort_values('Relative Strength', ascending=False, inplace=True)
    rs_sector.reset_index(inplace=True)
    rs_sector['Rank'] = range(1, len(rs_sector) + 1)

    for data_col, percentile_col in percentile_cols.items():
        rs_sector = calculate_percentile(rs_sector, data_col, percentile_col)

    tickers_by_industry = combined_stocks_df.groupby('Industry')['Ticker'].apply(lambda x: ','.join(x)).reset_index(name='Tickers')
    rs_sector = pd.merge(rs_sector, tickers_by_industry, on='Industry')

    # 4. Prepare final DataFrames by dropping temporary columns and setting index
    cols_to_drop = ['RS_1W', 'RS_1M', 'RS_3M', 'RS_6M']

    final_stocks_output = combined_stocks_df.drop(columns=cols_to_drop, errors='ignore').set_index('Rank')
    final_industries_output = rs_sector.drop(columns=cols_to_drop, errors='ignore').set_index('Rank')

    # 5. Save final files
    final_stocks_output.to_csv(final_stocks_file)
    final_industries_output.to_csv(final_industries_file)
    print(f"Successfully created final stock file: {final_stocks_file}")
    print(f"Successfully created final industry file: {final_industries_file}")

if __name__ == "__main__":
    us_results_dir = '_files/RS/results'
    combine_and_process_data(
        results_dir=us_results_dir,
        stocks_pattern='stocks_us_chunk_*.csv',
        industries_pattern='industries_us_chunk_*.csv',
        final_stocks_file='_files/RS/rs_stocks_us.csv',
        final_industries_file='_files/RS/rs_industries_us.csv'
    )

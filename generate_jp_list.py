import sys
import pandas as pd
import numpy as np
import searchIndustryJP as ind

def generate_list(output_list_file, jp_ind_txt):
    """
    Fetches the list of JP stocks from the JPX website,
    enriches it with industry data from yfinance (using a local cache),
    and saves it to a CSV file.
    """
    print("Fetching stock list from JPX...")
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    stock_codes = pd.read_excel(url, sheet_name='Sheet1')

    stock_codes = stock_codes.rename(columns={'コード': 'Ticker', "市場・商品区分":"SEGMENT", '33業種区分':'Sector', '規模コード':'SIZE'})
    stock_codes['SIZE'] = stock_codes['SIZE'].replace('-', '99').astype(int)

    print("Filtering for Prime and Standard markets...")
    stock_codes = stock_codes.query("SEGMENT == 'プライム（内国株式）' or SEGMENT == 'スタンダード（内国株式）'")

    stock_codes2 = stock_codes.copy()
    stock_codes2['Ticker'] = stock_codes2['Ticker'].apply(lambda x: '{:04}.T'.format(x))
    stock_codes2['Industry'] = np.nan

    try:
        df_tbl = ind.readTable(jp_ind_txt)
    except FileNotFoundError:
        df_tbl = pd.DataFrame(columns=['Ticker']) # Create empty df if cache doesn't exist

    missing_industries = []
    print("Checking for industries in local cache...")
    for index, data in stock_codes2.iterrows():
        ticker = data['Ticker']
        industry = ind.searchIndustry(df_tbl, ticker)
        if industry == "-----":
            missing_industries.append((index, data))
        else:
            stock_codes2.loc[index, 'Industry'] = industry

    if missing_industries:
        print(f"Found {len(missing_industries)} tickers with missing industries. Fetching from yfinance...")
        new_industry_lines = []
        for index, data in missing_industries:
            ticker = data['Ticker']
            industry = ind.getTickerIndustry(ticker)
            if industry and str(industry) != 'None':
                stock_codes2.loc[index, 'Industry'] = industry
                new_industry_lines.append(f"{data['Ticker']}~{data['銘柄名']}~{data['Sector']}~{str(industry)}\n")

        if new_industry_lines:
            print(f"Appending {len(new_industry_lines)} new industries to cache file: {jp_ind_txt}")
            with open(jp_ind_txt, mode='a', encoding='utf-8') as f:
                f.writelines(new_industry_lines)

    stock_codes2['Industry'] = stock_codes2['Industry'].fillna('---')

    stock_codes2.to_csv(output_list_file, index=False)
    print(f"JP Ticker list generated with {len(stock_codes2)} tickers and saved to {output_list_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_jp_list.py <output_csv_file> <industry_cache_txt_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    industry_cache_file = sys.argv[2]
    generate_list(output_file, industry_cache_file)

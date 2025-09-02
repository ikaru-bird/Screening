# --------------------------------------------- #
# 日本株のRelative Strength計算
# --------------------------------------------- #
import sys
import pandas as pd
import RelativeStrength as rs
import numpy as np
import searchIndustryJP as ind
import os

# --------------------------------------------- #
# 処理開始（メイン）
# --------------------------------------------- #
if __name__ == "__main__":

    # パラメータで動作を切り替える
    # Mode 1: "generate_list" -> JPXからリストを取得し、tickerリストをCSVに保存
    # Mode 2: "process_chunk" -> tickerリストのチャンクを処理
    mode = os.environ.get("JP_RS_MODE", "process_chunk")

    if mode == "generate_list":
        print("Running in 'generate_list' mode...")
        output_list_file = sys.argv[1]
        jp_ind_txt    = sys.argv[2]

        url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
        stock_codes = pd.read_excel(url, sheet_name='Sheet1')
        stock_codes = stock_codes.rename(columns={'コード': 'Ticker', "市場・商品区分":"SEGMENT", '33業種区分':'Sector', '規模コード':'SIZE'})
        stock_codes['SIZE'] = stock_codes['SIZE'].replace('-', '99')
        stock_codes['SIZE'] = stock_codes['SIZE'].astype(int)

        stock_codes = stock_codes.query("SEGMENT == 'プライム（内国株式）' or SEGMENT == 'スタンダード（内国株式）'")

        stock_codes2 = stock_codes.copy()
        stock_codes2['Ticker'] = stock_codes2['Ticker'].apply(lambda x: '{:04}.T'.format(x))
        stock_codes2['Industry'] = np.nan
        stock_codes2['Industry'] = stock_codes2['Industry'].astype('object')

        df_tbl = ind.readTable(jp_ind_txt)

        missing_industries = []
        print("Checking for industries in local cache...")
        for index, data in stock_codes2.iterrows():
            ticker = data['Ticker']
            industry = ind.searchIndustry(df_tbl, ticker)
            if industry == "-----":
                missing_industries.append((index, data))
            else:
                stock_codes2.loc[index, 'Industry'] = industry

        print(f"Found {len(missing_industries)} tickers with missing industries. Fetching from yfinance...")

        new_industry_lines = []
        for index, data in missing_industries:
            ticker = data['Ticker']
            industry = ind.getTickerIndustry(ticker)
            if industry and str(industry) != 'None':
                stock_codes2.loc[index, 'Industry'] = industry
                line = f"{ticker}~{data['銘柄名']}~{data['Sector']}~{str(industry)}\n"
                new_industry_lines.append(line)

        if new_industry_lines:
            print(f"Appending {len(new_industry_lines)} new industries to cache file.")
            with open(jp_ind_txt, mode='a', encoding='utf-8') as f:
                f.writelines(new_industry_lines)

        stock_codes2['Industry'] = stock_codes2['Industry'].fillna('---')

        stock_codes2.to_csv(output_list_file, index=False)
        print(f"Full ticker list saved to {output_list_file}")

    elif mode == "process_chunk":
        # print("Running in 'process_chunk' mode...")
        input_chunk_file = sys.argv[1]
        rs_result_csv = sys.argv[2]
        rs_sector_csv = sys.argv[3]

        stock_codes_chunk = pd.read_csv(input_chunk_file)

        # 処理実行
        rs.calc_rs(stock_codes_chunk, rs_result_csv, rs_sector_csv)

    else:
        print(f"Error: Invalid mode '{mode}'. Set JP_RS_MODE to 'generate_list' or 'process_chunk'.")
        sys.exit(1)

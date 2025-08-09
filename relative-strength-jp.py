# --------------------------------------------- #
# 日本株のRelative Strength計算
# --------------------------------------------- #
import sys
import pandas as pd
import RelativeStrength as rs
import numpy as np
import searchIndustryJP as ind

# --------------------------------------------- #
# 処理開始（メイン）
# --------------------------------------------- #
if __name__ == "__main__":
    
    #パラメータ受取り
    args          = sys.argv
    rs_result_csv = args[1]
    rs_sector_csv = args[2]
    jp_ind_txt    = args[3]
    
# --------------------------------------------- #
# 株式コードとセクター情報を読み込み
# --------------------------------------------- #
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    stock_codes = pd.read_excel(url, sheet_name='Sheet1')
#   stock_codes = stock_codes.rename(columns={'コード': 'Ticker', "市場・商品区分":"SEGMENT", '33業種区分':'Industry', '規模コード':'SIZE'})
    stock_codes = stock_codes.rename(columns={'コード': 'Ticker', "市場・商品区分":"SEGMENT", '33業種区分':'Sector', '規模コード':'SIZE'})
    stock_codes = stock_codes.replace({'SIZE':{'-':99}})
    stock_codes['SIZE'] = stock_codes['SIZE'].astype(int)

#   stock_codes = stock_codes.query("SEGMENT.str.contains('内国株式')")               # 国内株式全部
#   stock_codes = stock_codes.query("SEGMENT.str.contains('内国株式') and SIZE <= 7") # プライム+TOPIX Small2以上
    stock_codes = stock_codes.query("SEGMENT == 'プライム（内国株式）' or SEGMENT == 'スタンダード（内国株式）'") # プライム+スタンダード
    
    # 銘柄コードを4桁+'T'に変換
    stock_codes2 = stock_codes.copy()
#   stock_codes2['Ticker'] = stock_codes2['Ticker'].apply(lambda x: '{:04d}.T'.format(x))
    stock_codes2['Ticker'] = stock_codes2['Ticker'].apply(lambda x: '{:04}.T'.format(x))
    
    # Industry列を追加（値はnan）
    stock_codes2 = stock_codes2.assign(Industry = np.nan)
    # Industry列をobject型に設定
    stock_codes2['Industry'] = stock_codes2['Industry'].astype('object')
    
    # Industryテーブル読み込み
    df_tbl = ind.readTable(jp_ind_txt)
    
    # stock_codes2をループ処理
    for index, data in stock_codes2.iterrows():
        # テキストファイルから産業区分を検索
        industry = ind.searchIndustry(df_tbl, data['Ticker'])
        # 該当がない場合は、yfinanceから検索してファイルに追加
        if industry == "-----":
            industry = ind.getTickerIndustry(data['Ticker'])
            strLine  = data['Ticker'] + '~' + data['銘柄名'] + '~' + data['Sector'] + '~' + str(industry) + '\n'
            if str(industry) != 'None': # 業種区分が'None'の場合はファイルに追加しない
                ind.addFile(jp_ind_txt, strLine)
        # Dataframeに追加
        stock_codes2.loc[index, 'Industry'] = industry
    
    # 処理実行
    rs.calc_rs(stock_codes2, rs_result_csv, rs_sector_csv)


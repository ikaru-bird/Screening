# --------------------------------------------- #
# 米国株のRelative Strength計算
# --------------------------------------------- #
import sys
import pandas as pd
import RelativeStrength as rs

# --------------------------------------------- #
# 処理開始（メイン）
# --------------------------------------------- #
if __name__ == "__main__":
    
    #パラメータ受取り
    args          = sys.argv
    in_path       = args[1]
    rs_result_csv = args[2]
    rs_sector_csv = args[3]
    
    # inputファイルから銘柄群のシンボルを取得
    columns = ["Ticker", "Company", "Sector", "Industry", "Market Cap", "P/E", "Fwd P/E", "Earnings", "Volume", "Price"]
    stock_codes = pd.read_csv(in_path, sep="~", header=None, names=columns)
    
    # 処理実行
    rs.calc_rs(stock_codes, rs_result_csv, rs_sector_csv)


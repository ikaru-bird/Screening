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
    if len(sys.argv) < 4:
        print("Usage: python relative-strength-us.py <input_chunk_file> <rs_result_csv> <rs_sector_csv>")
        sys.exit(1)

    in_path       = sys.argv[1]
    rs_result_csv = sys.argv[2]
    rs_sector_csv = sys.argv[3]

    # inputファイルから銘柄群のシンボルを取得
    # The new shell script provides a chunk file with a header.
    # The original getList_US.py does not have a header.
    # To handle both, we can try to read with a header and if it fails, read without.
    # However, the shell script now controls the workflow, so we can assume the format.
    # The input file is now just a list of tickers, one per line.

    # The getList_US.py script creates a file with a header and '~' separator.
    columns = ["Ticker", "Company", "Sector", "Industry", "Market Cap", "P/E", "Fwd P/E", "Earnings", "Volume", "Price"]
    try:
        stock_codes = pd.read_csv(in_path, sep="~", header=None, names=columns)
    except pd.errors.EmptyDataError:
        print(f"Input file {in_path} is empty, skipping.")
        sys.exit(0)

    # 処理実行
    rs.calc_rs(stock_codes, rs_result_csv, rs_sector_csv)

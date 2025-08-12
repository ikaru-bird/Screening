# moduleをインポート

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

# 全角英数字を半角に変換
import unicodedata
def zenkaku_to_hankaku(zh_text):
    zh_res = unicodedata.normalize('NFKC', zh_text)
    return zh_res

import requests
import pandas as pd
from classGetExcelList import GetExcelList
import searchIndustryJP as ind

# パラメータ受取り
args = sys.argv
xlspath = args[1]
outpath = args[2]
listdir = args[3]
ind_txt = args[4]

# 銘柄リストをダウンロード
chkLink = GetExcelList()
baseurl = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
urlList = chkLink.getLink(baseurl)
if len(urlList) > 0:
    url = urlList[0]
else:
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

r   = requests.get(url)
with open(xlspath, 'wb') as output:
    output.write(r.content)

# シートをDataFrameに読み込み
input_book       = pd.ExcelFile(xlspath)
input_sheet_name = input_book.sheet_names
df0              = input_book.parse(input_sheet_name[0], encoding='utf-8')

# 列名の変更・値の置換・型変更
df1 = df0.rename(columns={"市場・商品区分": "SEGMENT", "規模コード": "SIZE"})
# Replace '-' with 99 to avoid FutureWarning
df1['SIZE'] = df1['SIZE'].replace('-', 99)
df1['SIZE'] = df1['SIZE'].astype(int)

# df1 = df1.query("SEGMENT == 'プライム（内国株式）'") # プライム市場のみ
# df1 = df1.query("SEGMENT.str.contains('内国株式')")  # 国内株式全部
# df1 = df1.query("SEGMENT.str.contains('内国株式') and SIZE <= 4")  # 国内株式+TOPIX Mid400以上
df1 = df1.query("SEGMENT.str.contains('内国株式') and SIZE <= 6")    # 国内株式+TOPIX Small1以上
# df1 = df1.query("SEGMENT == 'プライム（内国株式）' and SIZE <= 6") # プライム+TOPIX Small1以上
# df1 = df1.query("SEGMENT == 'プライム（内国株式）' and SIZE <= 7") # プライム+TOPIX Small2以上
# df1   = df1.query("SEGMENT == 'プライム（内国株式）' or SEGMENT == 'スタンダード（内国株式）'") # プライム+スタンダード

# 決算カレンダーの空箱
cal_df = pd.DataFrame(columns=["DATE","CODE","会社名","決算期末","業種名","種別","市場区分"])

# 決算カレンダーをダウンロード
url = "https://www.jpx.co.jp/listing/event-schedules/financial-announcement/index.html"
urlList = chkLink.getLink(url)
if len(urlList) == 0:
    urlList = ['https://www.jpx.co.jp/listing/event-schedules/financial-announcement/tvdivq0000001ofb-att/kessan12_0203.xlsx', 'https://www.jpx.co.jp/listing/event-schedules/financial-announcement/tvdivq0000001ofb-att/kessan01_0217.xlsx']

for item in urlList:
    r = requests.get(item)
    xlspath = listdir + item[item.rfind('/')+1:]
    with open(xlspath, 'wb') as output:
        output.write(r.content)

    try:
        # シートをDataFrameに読み込み
        input_book = pd.ExcelFile(xlspath)
        input_sheet_name = input_book.sheet_names
        cal_dfw = input_book.parse(input_sheet_name[0], header=4, encoding='utf-8')

        # 列名の変更、欠落値の除去、型変換、結合
        cal_dfw = cal_dfw.rename(columns={"決算発表予定日\nScheduled Dates for Earnings Announcements": "DATE", "コード\nCode": "CODE"})
        cal_dfw.dropna(subset=['CODE'], inplace=True)
        # cal_dfw['CODE'] = cal_dfw['CODE'].astype('int')
        cal_df = pd.concat([cal_df, cal_dfw])
    except Exception as e:
        print(f"Error processing {xlspath}: {e}")
        continue


# インデックスの設定
cal_df.reset_index(drop=True)
cal_df.set_index("CODE", inplace=True)
# print(cal_df)

# 重複したインデックスを削除（最初の行を残す）
cal_df = cal_df[~cal_df.index.duplicated(keep='first')]

# 証券コードリストを出力
with open(outpath, 'w', encoding='utf-8') as f:
    # Industryテーブル読み込み
    df_tbl = ind.readTable(ind_txt)
    
    # データ数だけループ
    for column_name, item in df1.iterrows():
        # 決算日を検索
        try:
#           Ern_dt = str(cal_df.iloc[int(item[1])]['DATE']) # 警告のため↓へ修正
            Ern_dt = str(cal_df.iloc[item.name]['DATE'])
        except:
            Ern_dt = ""
        
        # 銘柄関連情報を取得(yfinanceから)
        try:
            strTicker = str(item.iloc[1]) + '.T'
            ticker = yf.Ticker(strTicker)
            ticker_info = ticker.info
        except:
            ticker_info = []
        
        # industryを取得(テキストファイルから)
        industry = ind.searchIndustry(df_tbl, strTicker)
        
        # データ書き込み（社名にカンマが入っている場合があるので"~"区切り）
#       f.write(str(item[1])+'.T~' + str(item[2]) + '~' + str(item[7]) + '~' + str(item[5]) + '~~~~' + Ern_dt[:Ern_dt.rfind(' ')] + '~~\n')
#       f.write(str(item[1])+'.T~' + zenkaku_to_hankaku(str(item[2])) + '~' + str(item[7]) + '~' + industry + '~~~~' + Ern_dt[:Ern_dt.rfind(' ')] + '~~\n')
        f.write(str(item.iloc[1]) + '.T~' + zenkaku_to_hankaku(str(item.iloc[2])) + '~' + str(item.iloc[7]) + '~' + industry + '~~~~' + Ern_dt[:Ern_dt.rfind(' ')] + '~~\n')

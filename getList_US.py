#moduleをインポート
import sys
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import time

#パラメータ受取り
args = sys.argv
outpath = args[1]
url     = args[2]

# 空のDaafame
# cols  = ['No.','Ticker','Company','Sector','Industry','Market Cap','P/E','Fwd P/E','Earnings','Volume','Price']
headers = ['No.','Ticker','Company','Sector','Industry','Market Cap','P/E','Fwd P/E','Price','Volume','Earnings']

stock_list = pd.DataFrame(index=[], columns=headers)

# finvizのURL
# url = 'https://finviz.com/screener.ashx?v=152&f=cap_smallover,fa_epsqoq_o10,fa_epsyoy_o10,ind_stocksonly,sh_price_o7&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'

site = requests.get(url, headers={'User-Agent': 'Custom'})
data = BeautifulSoup(site.text,'html.parser')

# optionタグのみ読み込む
article = data.find_all("option")
# print(article)

for item_html in article:
    # データに"Page"と入った物があれば、ページ数を表すデータ
    if item_html.text[:4] == "Page":
        #”Page 1/96"の"96"だけが欲しいので、"/"でデータを区切って"/"の後ろのデータだけ取る
        tmp = item_html.text.split('/')
        tmp = tmp[1].splitlines()
        np  = int(tmp[0])
        print("Pages: " + str(np))
        break

# ページ数だけループ
for i in range(0, np):
    # URL読み込み（urlに(ページNo)*20+1が入る）
    url2 = url + '&r=' + str((i*20)+1)
    
    j = 0
    for j in range(3):
        try:
            # データ取得
            ua     = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            site   = requests.get(url2, headers={'User-Agent': ua})
            data   = BeautifulSoup(site.text,'html.parser')
            
            # タグの解析
            # スクリーニング結果のテーブルに含まれるclass名を指定する
            # 例）<table class="styled-table... screener_table">
            table = data.find_all('table', {'class': 'screener_table'})[0]
            rows = table.find_all('tr')
            
            # テーブルから値を抽出
            data = []
            for row in rows[1:]:
                cols = row.find_all('td')
                cols = [col.text.strip() for col in cols]
                data.append(cols)
            
            # Pandas Dataframeに格納
            df = pd.DataFrame(data, columns=headers)
            df = df.set_index('No.', drop=False)
            

        except Exception as e:
            print(f"エラーが発生しました：{e}")
            print(f"Error Retry ::: Page = {i + 1} ::: Count = {j + 1}")
            # 5秒スリープしてリトライ
            time.sleep(5)
        else:
            # 例外が発生しなかった場合、ループを抜ける
            break
    
    # Dataframeの結合
    stock_list = pd.concat([stock_list, df], axis=0)
#   stock_list = stock_list.reset_index(drop=True)
#   print(stock_list)

# リストの件数出力
print("Count: " + str(len(stock_list)))

# リストをファイル出力
with open(outpath, 'w', encoding='utf-8') as f:
    # データ数だけループ
    for column_name, item in stock_list.iterrows():
        # データ書き込み（社名にカンマが入っている場合があるので"~"区切り）
#       f.write(str(item[1]) + '~' + str(item[2]) + '~' + str(item[3]) + '~' + str(item[4]) + '~' + str(item[5]) + '~' + str(item[6]) + '~' + str(item[7]) + '~' + str(item[10]) + '~' + str(item[9]) + '~' + str(item[8]) + '\n')
        f.write(str(item.iloc[1]) + '~' + str(item.iloc[2]) + '~' + str(item.iloc[3]) + '~' + str(item.iloc[4]) + '~' + str(item.iloc[5]) + '~' + str(item.iloc[6]) + '~' + str(item.iloc[7]) + '~' + str(item.iloc[10]) + '~' + str(item.iloc[9]) + '~' + str(item.iloc[8]) + '\n')

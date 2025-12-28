#moduleをインポート
import sys
from bs4 import BeautifulSoup
import re
from curl_cffi import requests
import pandas as pd
import time

#パラメータ受取り
args = sys.argv
outpath = args[1]
url     = args[2]

# 空のDaafame
headers = ['No.','Ticker','Company','Sector','Industry','Market Cap','P/E','Fwd P/E','Price','Volume','Earnings']
stock_list = pd.DataFrame(index=[], columns=headers)

# ヘッダー
req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

# 最初のページを取得して総ページ数を確認
site = requests.get(url, headers=req_headers, impersonate="chrome110")
data = BeautifulSoup(site.text,'html.parser')

# optionタグからページ数を取得
article = data.find_all("option")
np = 1
for item_html in article:
    if item_html.text.startswith("Page"):
        try:
            tmp = item_html.text.split('/')
            if len(tmp) > 1:
                tmp = tmp[1].splitlines()
                np  = int(tmp[0])
                print("Pages: " + str(np))
            break
        except (ValueError, IndexError):
            # ページ数が取得できない場合はループを続ける
            continue

# 各ページからデータを取得
for i in range(0, np):
    url2 = url + '&r=' + str((i*20)+1)

    df = None
    for j in range(3): #リトライ処理
        try:
            site = requests.get(url2, headers=req_headers, impersonate="chrome110")
            data = BeautifulSoup(site.text,'html.parser')

            # 'screener_table'クラスを持つテーブルを探す
            table = data.find('table', {'class': 'screener_table'})
            if table is None:
                 # 新しいクラス名でも試す
                table = data.find('table', {'class': 'screener-new_table'})

            if table is None:
                # それでも見つからなければ、より汎用的な方法で探す
                all_tables = data.find_all('table')
                for t in all_tables:
                    if 'Ticker' in t.text:
                        table = t
                        break

            if table is None:
                raise ValueError("Could not find the screener table.")

            rows = table.find_all('tr')

            table_data = []
            for row in rows[1:]:
                cols = row.find_all('td')
                cols_text = [col.text.strip() for col in cols]
                if len(cols_text) == len(headers):
                    table_data.append(cols_text)

            if not table_data:
                # 有効なデータ行がない場合はリトライ
                raise ValueError("No data rows found in table.")

            df = pd.DataFrame(table_data, columns=headers)
            df = df.set_index('No.', drop=False)

            break # 成功したらリトライループを抜ける
        except Exception as e:
            print(f"Error on page {i + 1}, attempt {j + 1}: {e}")
            time.sleep(5)

    if df is not None:
        stock_list = pd.concat([stock_list, df], axis=0)

# リストの件数出力
print("Count: " + str(len(stock_list)))

# リストをファイル出力
with open(outpath, 'w', encoding='utf-8') as f:
    for _, item in stock_list.iterrows():
        f.write('~'.join(map(str, [item.iloc[1], item.iloc[2], item.iloc[3], item.iloc[4], item.iloc[5], item.iloc[6], item.iloc[7], item.iloc[10], item.iloc[9], item.iloc[8]])) + '\n')

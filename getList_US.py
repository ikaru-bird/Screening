#moduleをインポート
import sys
from bs4 import BeautifulSoup
import re
from curl_cffi import requests
import pandas as pd
import time
import os

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

# optionタグからページ数を取得（従来レイアウト用）
article = data.find_all("option")
np = 1
for item_html in article:
    text = item_html.text.strip()
    if text.startswith("Page"):
        try:
            tmp = text.split('/')
            if len(tmp) > 1:
                tmp = tmp[1].splitlines()
                np  = int(tmp[0].strip().split()[0])
                break
        except (ValueError, IndexError):
            continue
    elif "/" in text:
        tmp = text.split('/')
        if len(tmp) > 1 and tmp[1].strip().isdigit():
            try:
                np = int(tmp[1].strip())
                break
            except ValueError:
                continue

# 新レイアウト用のページ数取得
if np == 1:
    count_p = data.find('p', class_=lambda c: c and 'fv-table_toolbar-count' in c)
    if count_p:
        match_total = re.search(r'/\s*(\d+)\s*Total', count_p.text)
        if match_total:
            total_items = int(match_total.group(1))
            np = (total_items + 19) // 20

    if np == 1:
        nav_pager = data.find('nav', class_=lambda c: c and 'fv-table_toolbar-pages' in c)
        if nav_pager:
            match_nav = re.search(r'/\s*(\d+)', nav_pager.text)
            if match_nav:
                np = int(match_nav.group(1))

if np > 50:
    print(f"Pages: {np} (capped to 50 due to Finviz limit)")
    np = 50
else:
    print("Pages: " + str(np))

# 各ページからデータを取得
stop_fetching = False
for i in range(0, np):
    if stop_fetching:
        break

    url2 = url + '&r=' + str((i*20)+1)

    df = None
    for j in range(3): #リトライ処理
        try:
            site = requests.get(url2, headers=req_headers, impersonate="chrome110")
            if site.status_code == 403:
                print(f"Access forbidden (403) on page {i + 1}. Stopping page fetch.")
                stop_fetching = True
                break
            if site.status_code != 200:
                raise ValueError(f"HTTP status {site.status_code}")

            data = BeautifulSoup(site.text,'html.parser')

            table_data = []

            # 1. 新レイアウト (divベースのGrid)
            div_rows = data.find_all('div', class_=lambda c: c and 'fv-table_row' in c)
            if div_rows:
                for row in div_rows:
                    col_dict = {}
                    cells = row.find_all('div', class_=lambda c: c and 'fv-table_cell' in c)
                    for cell in cells:
                        cid = cell.get('data-column-id')
                        if not cid:
                            continue
                        if cid == 'ticker':
                            t_val = cell.get('data-ticker') or row.get('data-row-key')
                            if not t_val:
                                a_tag = cell.find('a', class_=lambda c: c and 'fv-table_link' in c)
                                if a_tag:
                                    spans = a_tag.find_all('span')
                                    t_val = spans[-1].text.strip() if spans else a_tag.text.strip()
                            col_dict['Ticker'] = t_val if t_val else cell.text.strip()
                        elif cid == 'row':
                            col_dict['No.'] = cell.text.strip()
                        elif cid == 'company':
                            col_dict['Company'] = cell.text.strip()
                        elif cid == 'sector':
                            col_dict['Sector'] = cell.text.strip()
                        elif cid == 'industry':
                            col_dict['Industry'] = cell.text.strip()
                        elif cid == 'marketCap':
                            col_dict['Market Cap'] = cell.text.strip()
                        elif cid == 'PE':
                            col_dict['P/E'] = cell.text.strip()
                        elif cid == 'forwardPE':
                            col_dict['Fwd P/E'] = cell.text.strip()
                        elif cid == 'price':
                            col_dict['Price'] = cell.text.strip()
                        elif cid == 'volume':
                            col_dict['Volume'] = cell.text.strip()
                        elif cid == 'earningsDate':
                            col_dict['Earnings'] = cell.text.strip()

                    row_vals = [col_dict.get(h, '') for h in headers]
                    if any(row_vals):
                        table_data.append(row_vals)

            # 2. 従来レイアウト (tableベース) のフォールバック
            if not table_data:
                table = data.find('table', {'class': 'screener_table'})
                if table is None:
                    table = data.find('table', {'class': 'screener-new_table'})
                if table is None:
                    all_tables = data.find_all('table')
                    for t in all_tables:
                        if 'Ticker' in t.text:
                            table = t
                            break

                if table is not None:
                    rows = table.find_all('tr')
                    for row in rows[1:]:
                        cols = row.find_all('td')
                        cols_text = []
                        for idx, col in enumerate(cols):
                            if idx == 1:  # Ticker column
                                ticker_a = col.find('a', class_='tab-link')
                                if ticker_a:
                                    cols_text.append(ticker_a.text.strip())
                                elif col.has_attr('data-boxover-ticker'):
                                    cols_text.append(col['data-boxover-ticker'].strip())
                                else:
                                    cols_text.append(col.text.strip())
                            else:
                                cols_text.append(col.text.strip())
                        if len(cols_text) == len(headers):
                            table_data.append(cols_text)

            if not table_data:
                raise ValueError("Could not find screener data in table or div layout.")

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
dirname = os.path.dirname(outpath)
if dirname:
    os.makedirs(dirname, exist_ok=True)

with open(outpath, 'w', encoding='utf-8') as f:
    for _, item in stock_list.iterrows():
        f.write('~'.join(map(str, [item.iloc[1], item.iloc[2], item.iloc[3], item.iloc[4], item.iloc[5], item.iloc[6], item.iloc[7], item.iloc[10], item.iloc[9], item.iloc[8]])) + '\n')

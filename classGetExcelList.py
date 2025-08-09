# coding: UTF-8

# Googleドライブのライブラリを指定(for Google Colab)
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

from urllib.parse import urlparse
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import requests

#---------------------------------------#
# ページ内のリンク検索クラス
#---------------------------------------#
class GetExcelList():

#---------------------------------------#
# Excelファイルへのリンクを返す
#---------------------------------------#
    def getLink(self, url):
        urlList    = []

        # URLをパースする
        parsed_url = urlparse(url)
        # スキーマを取得
        scheme = parsed_url.scheme
        # ホスト名を取得
        netloc = parsed_url.netloc
        # 階層を取得
        path = parsed_url.path
#       path = url[:url.rfind('/')]
        
        # HTMLの取得・パース処理
        response = requests.get(f"{url}")
        html = BeautifulSoup(response.text, 'html.parser')
        for link in html.findAll("a"):
            href = link.get('href')
            if href is None:
                pass
            else:
            # hrefがないAタグや、index.htmlがある場合は省く
                if ("http" not in href and "index.html" not in href):
                    href = href.replace('../', '')
                    href = href.replace('./', '')
                    href = href.replace('//', '')
            # 拡張子がxlsとxlsxファイルのURLだけ取得する
                    if (".xls" in href or ".xlsx" in href ):
                        if href[-1] == "/":
                            urlList.append(f"{dirurl}{href}index.php")
                        else:
                            if href[0] == "/":
                                urlList.append(f"{scheme}://{netloc}/{href[1:]}")
                            else:
                                urlList.append(f"{scheme}://{netloc}{path}{href}")
        # 配列に格納されている値をユニークにする
        urlList = list(dict.fromkeys(urlList))
        return urlList

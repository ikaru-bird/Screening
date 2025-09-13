# --------------------------------------------- #
# 米国株のRelative Strength計算
# --------------------------------------------- #
import sys
import pandas as pd
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --------------------------------------------- #
# フォント指定（日本語対応）
# --------------------------------------------- #
# Google Colab実行の場合（フォントファイルを指定）
import japanize_matplotlib
fp  = fm.FontProperties(fname='_files/Fonts/Meiryo/meiryo.ttc')
fpb = fm.FontProperties(fname='_files/Fonts/Meiryo/meiryob.ttc')
# --------------------------------------------- #
# PC実行の場合（フォントに'メイリオ'を指定）
# fp  = fm.FontProperties(family='Meiryo', weight='normal')
# fpb = fm.FontProperties(family='Meiryo', weight='bold')
# --------------------------------------------- #
plt.rcParams['font.family'] = fp.get_family()
# --------------------------------------------- #

# --------------------------------------------- #
# 画像出力処理
# --------------------------------------------- #
def draw_rs(rs_sector_csv, rs_sector_img):
    # csvファイルの読み込み
    df_rs_sector = pd.read_csv(filepath_or_buffer=rs_sector_csv, index_col=0)
    
    # RS Rating 70以上に絞り込み
    df_rs_sector = df_rs_sector.query('Percentile >= 70')
    
    # 出力用テーブル空枠
    tbl_data = []
    
    # figureを作成
    fig = plt.figure(figsize=(10, 10), dpi=100)
    
    # subplotを追加
    ax1 = fig.add_subplot(111)
    
    # 表示設定
    ax1.axis("tight")
    ax1.axis("off")
    
    # 背景に画像を設定する
#   background_img = "_files/images/ikaru_logo.png"
#   background = plt.imread(background_img)
#   fig.figimage(background, 0, 0, alpha=0.1, zorder=0)
    
    # 背景にテキストを挿入
    ax1.text(0.5, 0.5, '@ikaru_bird', ha='center', va='center', transform=ax1.transAxes, fontsize=60, alpha=0.1, weight='bold', fontproperties=fpb, rotation=30, zorder=1)
    
    #全体のタイトル
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt_text = now.strftime('%Y/%m/%d(%a) %H:%M %Z')
    strTitle  = '::: 米国株／業種区分別／Relative Strength :::\n' + dt_text
    plt.suptitle(strTitle)
    
    # テーブルに出力項目を追加
    # ヘッダー
    tbl_data.append(["Rank", "業種区分", "前週比", "RS Rating", "1ヵ月前", "3ヵ月前", "6ヵ月前", "Tickers(Top5)"])
    # ボディ
    count = 0  # ループ回数をカウントする変数
    for index, data in df_rs_sector.iterrows():
        
        split_tickers = data['Tickers'].split(",")  # カンマで分割
        output_tickers = ", ".join(split_tickers[:5])    # 先頭の5つの要素を取得し、カンマで結合
        
        strUDmark = ''
        if round(data['Diff']) == 0:
            strUDmark = '－'
        elif round(data['Diff']) > 0:
            strUDmark = '↑'
        elif round(data['Diff']) < 0:
            strUDmark = '↓'
        
        tbl_data.append([index, data['Industry'], strUDmark, round(data['Percentile']), round(data['1 Month Ago']), round(data['3 Months Ago']), round(data['6 Months Ago']), output_tickers])
        
        count += 1       # ループ回数をインクリメント
        if count >= 30:  # カウントが30以上の場合、Break
            break
    
    # テーブル出力
    ax1_tbl = ax1.table(cellText=tbl_data, cellLoc='left', loc='center')
    
    # テーブルのフォントサイズを固定
    ax1_tbl.auto_set_font_size(False)
    ax1_tbl.set_fontsize(9)
    
    # 余白を調整
    ax1_tbl.scale(1, 2)
    plt.subplots_adjust(left=0.2, bottom=0.2, right=0.8, top=0.8)
    
    # テーブルの高さ・背景色を調整
    i = 0 # カウンタ
    for pos, cell in ax1_tbl.get_celld().items():
    #   cell.set_height(1/len(data))
        
        # 'RS Rating'のセル背景色
        if i > 7 and 3 <= i % 8 <= 6:  
            cell_val = float(cell.get_text().get_text())
            if 80 > cell_val >= 70:            # 値が70以上～80未満の場合
                cell.set_facecolor('#fffacd')  # 背景を黄色に設定
            elif 90 > cell_val >= 80:          # 値が80以上～90未満の場合
                cell.set_facecolor('#ffd700')  # 背景をオレンジに設定
            elif cell_val >= 90:               # 値が90以上の場合
                cell.set_facecolor('#ffb6c1')  # 背景を赤色に設定
        elif i <= 7:
            cell.set_facecolor('#191970')      # ヘッダーの色設定
            cell.set_text_props(weight='bold', fontproperties=fpb, color='white')
        
        # セル幅セット
        if i%8 == 0:
            cell.set_width(0.07)
        elif i%8 == 1:
            cell.set_width(0.4)
        elif i%8 == 2:
            # RS RatingのUP/Downの色設定
            cell.set_width(0.1)
            if cell.get_text().get_text() == '↑':
                cell.set_text_props(weight='bold', fontproperties=fpb, color='red')
            elif cell.get_text().get_text() == '↓':
                cell.set_text_props(weight='bold', fontproperties=fpb, color='blue')
        elif i%8 == 3:
            cell.set_width(0.14)
        elif i%8 == 4:
            cell.set_width(0.11)
        elif i%8 == 5:
            cell.set_width(0.11)
        elif i%8 == 6:
            cell.set_width(0.11)
        elif i%8 == 7:
            cell.set_width(0.45)
        i += 1 # カウンタ加算
    
    # 画像ファイルを保存
    plt.savefig(rs_sector_img)
    # plt.show()
    plt.close()


# --------------------------------------------- #
# 処理開始（メイン）
# --------------------------------------------- #
if __name__ == "__main__":
    
    #パラメータ受取り
    args          = sys.argv
    rs_sector_csv = args[1]
    rs_sector_img = args[2]
    
    # 処理実行
    draw_rs(rs_sector_csv, rs_sector_img)


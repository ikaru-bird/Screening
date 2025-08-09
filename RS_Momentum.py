import sys
import pandas as pd
import matplotlib.pyplot as plt

# パラメータ受取り
args    = sys.argv
inpath  = args[1]
outpath = args[2]
count   = int(args[3])

try:
    # CSVファイルの読み込み
    df = pd.read_csv(inpath)
    df = df.head(count)
except FileNotFoundError:
    print(f"Error: The file {inpath} was not found.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print("Error: The file is empty.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

# X軸とY軸の列マッピング
x_columns = ['Percentile', '1 Week Ago', '1 Month Ago', '3 Months Ago']
y_columns = ['RS Momentum', 'RM_1W', 'RM_1M', 'RM_3M']

# 列が存在するか確認
for col in x_columns + y_columns:
    if col not in df.columns:
        print(f"Error: Column {col} not found in the data.")
        sys.exit(1)

# カラーマップの定義
color_map = plt.cm.tab20

# 各業界のデータをプロット
plt.figure(figsize=(10, 6))
for idx, row in df.iterrows():
    industry_color = color_map(idx % len(color_map.colors))  # インデックスに基づいて色を取得
    x_values = row[x_columns].values
    y_values = row[y_columns].values
    plt.plot(x_values, y_values, label=row['Industry'], linestyle='--', marker='o', color=industry_color)
    plt.plot(x_values[0], y_values[0], marker='*', markersize=12, color=industry_color)  # 開始点に同じ色を使用

# タイトルとラベルの追加
plt.title('Sectors RS Percentile / RS Momentum')
plt.xlabel('RS Percentile')
plt.ylabel('RS Momentum')

# 凡例の追加
plt.legend(loc='best', fontsize='small')

# プロットの表示と保存
plt.grid(True)
try:
    plt.savefig(outpath)
except Exception as e:
    print(f"Error: Could not save the plot. {e}")
    sys.exit(1)
plt.close()

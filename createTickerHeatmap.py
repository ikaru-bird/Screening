import pandas as pd
import matplotlib
matplotlib.use('Agg') # 安定したバックエンドを指定
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
import squarify
import textwrap

# === 引数チェック ===
if len(sys.argv) != 4:
    print("Usage: python createTickerHeatmap.py <input_file> <output_file> <region>")
    sys.exit(1)

# === 引数読込 ===
input_file = sys.argv[1]
output_file = sys.argv[2]
region = sys.argv[3]

# === ファイル読込 ===
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: Input file not found at {input_file}")
    sys.exit(1)

# === 列の整形 ===
df.columns = [c.strip() for c in df.columns]
for col in ['Diff', 'RS Momentum']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df.dropna(subset=['Diff', 'RS Momentum', 'Industry'], inplace=True)

# === フィルタ条件 ===
diff_threshold = df['Diff'].quantile(0.95)
rs_threshold = df['RS Momentum'].quantile(0.95)
filtered_df = df[
    (df['Diff'] >= diff_threshold) &
    (df['RS Momentum'] >= rs_threshold) &
    (df['RS Momentum'] > 0.5)
].copy()

# === Industryでの集計 ===
industry_agg = filtered_df.groupby('Industry').agg(
    total_diff=('Diff', 'sum')
).reset_index()

# 企業数が少ないIndustryを除外
industry_counts = filtered_df['Industry'].value_counts()
valid_industries = industry_counts[industry_counts >= 1].index
industry_agg = industry_agg[industry_agg['Industry'].isin(valid_industries)]
filtered_df = filtered_df[filtered_df['Industry'].isin(valid_industries)]

# データがない場合は終了
if filtered_df.empty or industry_agg.empty:
    print("No data to plot after filtering. Exiting.")
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "No data to display", ha='center', va='center')
    plt.savefig(output_file)
    sys.exit(0)

# === ソートとインデックスのリセット ===
industry_agg = industry_agg.sort_values('total_diff', ascending=False).reset_index(drop=True)
filtered_df = filtered_df.sort_values(['Industry', 'Diff'], ascending=[True, False])

# === 可視化設定 ===
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(16, 10), facecolor='#0a0d1a')
ax.set_facecolor('#0a0d1a')
ax.axis('off')

# === カラーマップ設定 ===
vmin = filtered_df['RS Momentum'].min()
vmax = filtered_df['RS Momentum'].max()
norm = plt.Normalize(vmin=vmin, vmax=vmax)
cmap = plt.cm.coolwarm

# === 描画領域の定義 ===
x, y, dx, dy = 0, 0, 100, 100

# === 階層的ツリーマップの描画ロジック ===

# 1. Industryレベルの矩形を計算
industry_sizes = industry_agg['total_diff'].values
if any(s <= 0 for s in industry_sizes):
    print("Warning: Industry sizes must be positive. Filtering out non-positive values.")
    positive_mask = industry_sizes > 0
    industry_sizes = industry_sizes[positive_mask]
    industry_agg = industry_agg[positive_mask].reset_index(drop=True) # 再度リセット

industry_rects = squarify.normalize_sizes(industry_sizes, dx, dy)
industry_plots = squarify.squarify(industry_rects, x, y, dx, dy)

# 2. 各Industry矩形内にTickerを描画
for i, row in industry_agg.iterrows(): # 'i' is now guaranteed to be 0, 1, 2...
    industry_name = row['Industry']
    industry_plot = industry_plots[i]
    ix, iy, idx, idy = industry_plot['x'], industry_plot['y'], industry_plot['dx'], industry_plot['dy']

    # Industryの枠線
    rect = patches.Rectangle((ix, iy), idx, idy, linewidth=2.5, edgecolor='#2c3e50', facecolor='none', zorder=5)
    ax.add_patch(rect)

    # Industryラベル
    wrapped_industry = textwrap.fill(industry_name, width=15)
    ax.text(ix + 2, iy + idy - 2, wrapped_industry,
            ha='left', va='top', fontsize=12, color='white', weight='bold', zorder=10)

    # このIndustryに属するTickerを取得し、インデックスをリセット
    tickers_in_industry = filtered_df[filtered_df['Industry'] == industry_name].reset_index(drop=True)
    ticker_sizes = tickers_in_industry['Diff'].values

    if len(ticker_sizes) > 0:
        # Tickerレベルの矩形を計算
        ticker_rects = squarify.normalize_sizes(ticker_sizes, idx, idy)
        ticker_plots = squarify.squarify(ticker_rects, ix, iy, idx, idy)

        for j, ticker_row in tickers_in_industry.iterrows(): # 'j' is now guaranteed to be 0, 1, 2...
            ticker_plot = ticker_plots[j]
            tx, ty, tdx, tdy = ticker_plot['x'], ticker_plot['y'], ticker_plot['dx'], ticker_plot['dy']

            # Ticker矩形
            color = cmap(norm(ticker_row['RS Momentum']))
            rect_ticker = patches.Rectangle((tx, ty), tdx, tdy, linewidth=1, edgecolor='#0a0d1a', facecolor=color, zorder=1)
            ax.add_patch(rect_ticker)

            # Tickerラベル
            font_size = 9
            if tdx * tdy < len(ticker_row['Ticker']) * 20 or tdx < 10 or tdy < 10:
                pass # 小さすぎる場合は描画しない
            else:
                ax.text(tx + tdx / 2, ty + tdy / 2, ticker_row['Ticker'],
                       ha='center', va='center', fontsize=font_size, color='white', weight='bold', zorder=10)

# === タイトル ===
ax.set_title(f"TOP STOCKS ({region})", fontsize=22, color='gray', weight='bold', pad=20)
fig.text(0.5, 0.92, "Grouped by Industry (Top 5% by Diff & RS Momentum)", fontsize=12, color='gray', ha='center')

# === 描画範囲の設定 ===
ax.set_xlim(x, x + dx)
ax.set_ylim(y, y + dy)

# === 保存 ===
plt.tight_layout(pad=1)
plt.savefig(output_file, dpi=250, bbox_inches='tight')

print(f"Hierarchical treemap has been successfully generated and saved to {output_file}")

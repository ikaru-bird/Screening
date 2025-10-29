import pandas as pd
import matplotlib.pyplot as plt
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
df = pd.read_csv(input_file)

# === 列の整形 ===
df.columns = [c.strip() for c in df.columns]
for col in ['Diff', 'RS Momentum']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# === フィルタ条件 ===
diff_threshold = df['Diff'].quantile(0.95)
rs_threshold = df['RS Momentum'].quantile(0.95)
filtered = df[
    (df['Diff'] >= diff_threshold) &
    (df['RS Momentum'] >= rs_threshold) &
    (df['RS Momentum'] > 0.5)
].copy()

# === ソート ===
filtered = filtered.sort_values('RS Momentum', ascending=False).reset_index(drop=True)

# === 可視化設定 ===
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_facecolor('#0a0d1a')
ax.axis('off')

# === ツリーマップデータ準備 ===
sizes = filtered['Diff']
colors = filtered['RS Momentum']
labels = [f"{ticker}\n{textwrap.fill(industry, 15)}" for ticker, industry in zip(filtered['Ticker'], filtered['Industry'])]


# カラーマップ設定
norm = plt.Normalize(vmin=colors.min(), vmax=colors.max())
cmap = plt.cm.coolwarm
color_mapped = [cmap(norm(value)) for value in colors]

# === ツリーマップ描画 ===
# ラベルは後で手動で追加するため、ここでは描画しない
squarify.plot(sizes=sizes, color=color_mapped, ax=ax)

# === ラベル描画 ===
# squarify.plotがaxに追加したパッチ(矩形)のリストを取得
patches = ax.patches
for i, rect in enumerate(patches):
    ticker = filtered['Ticker'].iloc[i]
    industry = textwrap.fill(filtered['Industry'].iloc[i], 15)

    # テキストを中央に配置
    x, y, dx, dy = rect.get_x(), rect.get_y(), rect.get_width(), rect.get_height()

    # Y座標を矩形の高さに基づいて調整
    y_ticker = y + dy / 2 + dy * 0.08
    y_industry = y + dy / 2 - dy * 0.08

    ax.text(x + dx / 2, y_ticker, ticker,
            ha='center', va='center', fontsize=9, color='white', weight='bold')
    ax.text(x + dx / 2, y_industry, industry,
            ha='center', va='center', fontsize=8, color='white')

# === タイトル ===
ax.set_title(f"TOP STOCKS ({region})", fontsize=22, color='gray', weight='bold', pad=20)
fig.text(0.5, 0.92, "Diff in top 5%, RS Momentum > 0.5", fontsize=12, color='gray', ha='center')


# === 保存 ===
plt.tight_layout(pad=1)
plt.savefig(output_file, dpi=250, bbox_inches='tight', facecolor='#0a0d1a')

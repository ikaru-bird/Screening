import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === ファイル読込 ===
path = '_files/RS/rs_stocks_us.csv'  # ファイルパスを指定
df = pd.read_csv(path)

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
n = len(filtered)
cols = int(np.ceil(np.sqrt(n)))
rows = int(np.ceil(n / cols))

fig, ax = plt.subplots(figsize=(12, 8))
plt.style.use('dark_background')
ax.set_facecolor('#0a0d1a')
ax.axis('off')

# 正規化とカラーマップ設定
sizes = filtered['Diff']
colors = filtered['RS Momentum']
norm = plt.Normalize(colors.min(), colors.max())
cmap = plt.cm.coolwarm

# === ヒートマップ描画 ===
width = 1 / cols
height = 1 / rows

for i, (ticker, diff, rs) in enumerate(zip(filtered['Ticker'], sizes, colors)):
    row = i // cols
    col = i % cols
    x = col * width
    y = 1 - (row + 1) * height

    color = cmap(norm(rs))
    ax.add_patch(plt.Rectangle((x, y), width, height, color=color, ec='black', lw=0.6))

    label = f"{ticker}\n{rs:.2f}"
    ax.text(x + width/2, y + height/2, label,
            ha='center', va='center', fontsize=9,
            color='white', weight='bold')

# === タイトル ===
ax.text(0.5, 1.05, "STOCKS", fontsize=22, color='gray', ha='center', weight='bold')
ax.text(0.5, 1.01, "Diff in top 5%, RS Momentum > 0.5", fontsize=12, color='gray', ha='center')

# === 保存 ===
plt.tight_layout()
plt.savefig('_files/RS/topTickers.png', dpi=250, bbox_inches='tight', facecolor='#0a0d1a')
plt.show()

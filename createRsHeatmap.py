import sys
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import datetime
import pytz
import textwrap
import argparse
import time

def get_color(rs_rating):
    """Maps RS Rating to a color based on a linear gradient."""

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb_color):
        r, g, b = rgb_color
        return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

    if rs_rating < 80:
        return '#ccece6'  # Lightest green for values below the main range

    # Define the colors for the gradient.
    # Higher RS ratings will be a stronger green.
    color_start_hex = '#ccece6'  # for RS rating 80
    color_end_hex   = '#2ca25f'  # for RS rating 99

    # Convert hex to RGB
    r_start, g_start, b_start = hex_to_rgb(color_start_hex)
    r_end, g_end, b_end = hex_to_rgb(color_end_hex)

    # Define the RS rating range for the gradient
    rating_min = 80
    rating_max = 99

    # Clamp the rating to the defined range
    rs_rating_clamped = max(rating_min, min(rs_rating, rating_max))

    # Calculate the interpolation factor (0.0 to 1.0)
    if (rating_max - rating_min) == 0:
        t = 1.0 # If range is zero, use the end color
    else:
        t = (rs_rating_clamped - rating_min) / (rating_max - rating_min)

    # Linear interpolation for each color channel
    r = r_start + t * (r_end - r_start)
    g = g_start + t * (g_end - g_start)
    b = b_start + t * (b_end - b_start)

    return rgb_to_hex((r, g, b))

def create_heatmap(csv_path, output_path, region):
    """Generates the RS heatmap from the provided CSV file."""
    # 1. Load and filter data
    df = pd.read_csv(csv_path)

    # Identify top industries by Diff and RS Momentum
    top_diff = df.nlargest(10, 'Diff')
    top_rs   = df.nlargest(20, 'RS Momentum')
    top_diff_industries = set(top_diff['Industry'])
    top_rs_industries   = set(top_rs['Industry'])

    df_filtered = df[(df['Percentile'] >= 80) & (df['Percentile'] <= 99)].head(28)

    common_industries = top_diff_industries & top_rs_industries
    filtered_common = df_filtered[df_filtered['Industry'].isin(common_industries)]
    
    top_industries = (
        filtered_common
        .sort_values(by='Diff', ascending=False)
        .head(3)['Industry']
        .unique()
    )

    # --- Print Top Industries and Tickers ---
    print("\n--- Top Industries and Tickers ---")
    for industry in top_industries:
        industry_row = df_filtered[df_filtered['Industry'] == industry]
        if not industry_row.empty:
            tickers_str = industry_row['Tickers'].iloc[0]
            tickers_list = tickers_str.split(',')
            top_3_tickers = tickers_list[:3]
            print(f"{industry} {' '.join(top_3_tickers)}")
    # -----------------------------------------

    # 2. Set up the plot
    fig = plt.figure(figsize=(12, 16), dpi=150)
    gs = GridSpec(8, 4, figure=fig, hspace=0.2, wspace=0.2, height_ratios=[0.5, 1, 1, 1, 1, 1, 1, 1])

    # 3. Add main title and legend
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
#   now = datetime.datetime.now(pytz.timezone('UTC'))
#   dt_text = now.strftime('Update: %Y/%m/%d(%a)')
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt_text = now.strftime('%Y/%m/%d(%a) %H:%M JST')
    
    title_text = f'::: {region} Stock / Relative Strength :::'
    ax_title.text(0.0, 0.8, title_text, ha='left', va='center', fontsize=24, fontweight='bold')
    ax_title.text(0.0, 0.3, dt_text, ha='left', va='center', fontsize=16)

    # Add legend
    #legend_elements = [
    #    plt.Rectangle((0, 0), 1, 1, color='#006d2c', label='97-99'),
    #    plt.Rectangle((0, 0), 1, 1, color='#2ca25f', label='94-96'),
    #    plt.Rectangle((0, 0), 1, 1, color='#66c2a4', label='91-93'),
    #    plt.Rectangle((0, 0), 1, 1, color='#99d8c9', label='88-90'),
    #    plt.Rectangle((0, 0), 1, 1, color='#ccece6', label='85-87'),
    #    plt.Rectangle((0, 0), 1, 1, color='#ffffb2', label='82-84'),
    #    plt.Rectangle((0, 0), 1, 1, color='#fed976', label='80-81')
    #]
    #ax_title.legend(handles=legend_elements, title="RS Rating", loc='upper right', ncol=4, frameon=False, fontsize='small')


    # 4. Iterate and create each cell
    for i, (index, row) in enumerate(df_filtered.iterrows()):
        row_idx = (i // 4) + 1
        col_idx = i % 4

        ax = fig.add_subplot(gs[row_idx, col_idx])

        rs_rating = row['Percentile']
        sector_name = row['Industry']
        diff = row['Diff']
        tickers = row['Tickers'].split(',')
        top_ticker = tickers[0] if tickers else ''

        # Cell background color
        ax.set_facecolor(get_color(rs_rating))
        for spine in ax.spines.values():
            spine.set_edgecolor('none')

        # Remove ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Add text
        wrapped_sector_name = textwrap.fill(sector_name, width=20)
        ax.text(0.05, 0.95, wrapped_sector_name, transform=ax.transAxes, fontsize=10, color='black', va='top', fontweight='bold')

        # Up/Down arrow
        arrow = ''
        color = 'black'
        if diff > 0:
            # Check if the industry is in the top 10 for both Diff and RS Momentum
            if sector_name in top_industries:
                arrow = '▲▲'
            else:
                arrow = '▲'
            color = 'lime'
        elif diff < 0:
            arrow = '▼'
            color = 'red'
        ax.text(0.05, 0.5, arrow, transform=ax.transAxes, fontsize=20, color=color, va='center', ha='left')

        # RS Rating (bottom-right)
        ax.text(0.95, 0.15, f"{int(rs_rating)}", transform=ax.transAxes, fontsize=28, fontweight='bold', color='white', ha='right', va='bottom')

        # Top 3 Tickers (bottom-left) - first one bold
        if len(tickers) > 0:
            first_ticker = tickers[0]
            other_tickers_str = ', '.join(tickers[1:3])

            # Use mathtext for bolding the first ticker without requiring LaTeX
            bold_first_ticker = r"$\bf{" + first_ticker + "}$"

            full_text = bold_first_ticker
            if other_tickers_str:
                full_text += ', ' + other_tickers_str

            ax.text(0.05, 0.05, full_text, transform=ax.transAxes, fontsize=9, color='black', va='bottom', ha='left')

        # Add mini-chart
        if top_ticker:
            stock_data = pd.DataFrame()
            for attempt in range(3):
                try:
                    stock_data = yf.download(top_ticker, period='90d', progress=False, auto_adjust=True)
                    if not stock_data.empty:
                        break  # Success
                except Exception as e:
                    print(f"An exception occurred while downloading {top_ticker}: {e}")
                    stock_data = pd.DataFrame() # Ensure data is empty on exception

                # If we are here, the download failed. Announce retry and sleep.
                if attempt < 2: # Don't announce or sleep on the last attempt
                    print(f"Download failed for {top_ticker}. Attempt {attempt+1}/3. Retrying in 10s...")
                    time.sleep(10)

            if not stock_data.empty:
                chart_ax = ax.inset_axes([0.1, 0.25, 0.8, 0.6], zorder=0)
                chart_ax.plot(stock_data.index, stock_data['Close'], color='white', linewidth=1.5)
                chart_ax.axis('off')
            else:
                ax.text(0.5, 0.5, "Chart NA", color='black', fontsize=8, ha='center', va='center')

    # 5. Save the figure
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to {output_path}")

if __name__ == "__main__":

    # パラメータ受取り
    args     = sys.argv
    region   = args[1]
    csv_path = args[2]
    out_path = args[3]

    create_heatmap(csv_path, out_path, region)

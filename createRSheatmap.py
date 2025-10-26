# create_rs_heatmap.py
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import datetime
import pytz
import textwrap

def get_color(rs_rating):
    """Maps RS Rating to a color based on the provided image."""
    if rs_rating >= 97:
        return '#006d2c'  # Darkest Green
    elif rs_rating >= 94:
        return '#2ca25f'
    elif rs_rating >= 91:
        return '#66c2a4'
    elif rs_rating >= 88:
        return '#99d8c9'
    elif rs_rating >= 85:
        return '#ccece6'  # Lightest Green
    elif rs_rating >= 82:
        return '#ffffb2'  # Lightest Yellow
    elif rs_rating >= 80:
        return '#fed976'  # Light Orange
    return '#feb24c'      # Orange

def create_heatmap(csv_path, output_path):
    """Generates the RS heatmap from the provided CSV file."""
    # 1. Load and filter data
    df = pd.read_csv(csv_path)
    df_filtered = df[(df['Percentile'] >= 80) & (df['Percentile'] <= 99)].head(28)

    # 2. Set up the plot
    fig = plt.figure(figsize=(12, 16), dpi=150)
    gs = GridSpec(8, 4, figure=fig, hspace=0.4, wspace=0.3)

    # 3. Add main title and legend
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    now = datetime.datetime.now(pytz.timezone('UTC'))
    dt_text = now.strftime('Update %Y/%m/%d(%a)')
    ax_title.text(0.0, 0.8, 'US Stock Relative Strength Heatmap', ha='left', va='center', fontsize=24, fontweight='bold')
    ax_title.text(0.0, 0.5, dt_text, ha='left', va='center', fontsize=16)

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
        top_3_tickers = ', '.join(tickers[:3])

        # Cell background color
        ax.set_facecolor(get_color(rs_rating))
        for spine in ax.spines.values():
            spine.set_edgecolor('none')

        # Remove ticks
        ax.set_xticks([])
        ax.set_yticks([])

        # Add text
        wrapped_sector_name = textwrap.fill(sector_name, width=20)
        ax.text(0.05, 0.9, wrapped_sector_name, transform=ax.transAxes, fontsize=10, color='black', va='top', fontweight='bold')
        ax.text(0.05, 0.6, f"{int(rs_rating)}", transform=ax.transAxes, fontsize=28, fontweight='bold', color='black', va='top')
        
        # Up/Down arrow
        arrow = ''
        color = 'black'
        if diff > 0:
            arrow = '▲'
            color = 'green'
        elif diff < 0:
            arrow = '▼'
            color = 'red'
        ax.text(0.95, 0.7, arrow, transform=ax.transAxes, fontsize=20, color=color, va='top', ha='right')
        
        # Top 3 Tickers
        ax.text(0.95, 0.6, top_3_tickers, transform=ax.transAxes, fontsize=8, color='black', va='top', ha='right')

        # Add mini-chart
        if top_ticker:
            try:
                stock_data = yf.download(top_ticker, period='90d', progress=False)
                if not stock_data.empty:
                    chart_ax = ax.inset_axes([0.1, 0.1, 0.8, 0.5])
                    chart_ax.plot(stock_data.index, stock_data['Close'], color='black', linewidth=1.5)
                    chart_ax.axis('off') # Correctly hides all chart axes, labels, and borders
            except Exception as e:
                ax.text(0.5, 0.35, "Chart NA", color='black', fontsize=8, ha='center', va='center')

    
    # 5. Save the figure
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Heatmap saved to {output_path}")

if __name__ == "__main__":
    CSV_FILE    = '_files/RS/rs_industries_us.csv'
    OUTPUT_FILE = '_files/RS/SectorRS_Heatmap_US.png'
    create_heatmap(CSV_FILE, OUTPUT_FILE)


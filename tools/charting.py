# rs_outperformance_kite_system/tools/charting.py

import matplotlib.pyplot as plt
import pandas as pd
import os
from core.rs_calculator import add_ama, add_donchian_channel

def plot_rs_chart(symbol, stock_df, index_df, pattern=None, show=False):
    try:
        df = stock_df.copy()
        index = index_df.copy()
        df = add_ama(df)
        df = add_donchian_channel(df)

        # RS ratio
        df['rs'] = df['close'] / index['close']

        # Chart setup
        plt.figure(figsize=(10, 5))
        plt.title(f"{symbol} RS Chart" + (f" – {pattern}" if pattern else ""), fontsize=14)
        plt.plot(df['rs'], label='RS Ratio', color='blue')
        plt.plot(df['ama'], label='AMA (Price)', linestyle='--', alpha=0.7)
        plt.plot(df['donchian_high'], label='Donchian High', linestyle='--', alpha=0.5, color='green')
        plt.plot(df['donchian_low'], label='Donchian Low', linestyle='--', alpha=0.5, color='red')
        plt.legend()
        plt.grid(True)

        output_path = f"output/reports/charts/{symbol}_rs_chart.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        if show:
            plt.show()
        plt.close()

        return output_path
    except Exception as e:
        print(f"[ERROR] Could not generate chart for {symbol}: {e}")
        return None

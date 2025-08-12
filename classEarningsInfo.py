# coding: UTF-8

import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks/my-modules')

import pandas as pd
import datetime as dt
import yfinance as yf # Import yfinance here

class EarningsInfo():
    def __init__(self, ticker_obj):
        self.ticker = ticker_obj
        self.income_stmt = None
        self.quarterly_income_stmt = None
        self.earnings_history = None
        try:
            # Data is fetched on demand from the ticker object
            self.income_stmt = self.ticker.income_stmt
            self.quarterly_income_stmt = self.ticker.quarterly_income_stmt
            self.earnings_history = self.ticker.earnings_history
        except Exception as e:
            print(f"Could not fetch income statements for {self.ticker.ticker}: {e}")

    def isfloat(self, s):
        try:
            float(str(s))
        except (ValueError, TypeError):
            return False
        return True

    def _get_eps_from_stmt(self, stmt):
        if stmt is None:
            return None
        if 'Basic EPS' in stmt.index:
            return stmt.loc['Basic EPS']
        return None

    def _check_roe(self, roe):
        if not self.isfloat(roe):
            return False, "N/A"
        if float(roe) < 0.15:
            return False, f"{float(roe):.1%} < 15%"
        return True, f"{float(roe):.1%} >= 15%"

    def _check_annual_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.income_stmt)
            if eps_data is None or len(eps_data) < 4:
                return False, "data < 4 years"

            eps_list = eps_data.head(4).tolist()
            eps0, eps1, eps2, eps3 = eps_list

            if any(not self.isfloat(e) for e in eps_list):
                return False, "invalid data"

            if eps0 <= 0 or eps1 <= 0 or eps2 <= 0 or eps3 <= 0:
                 if eps0 > 0 and eps3 < 0:
                    return True, f"turnaround ({eps3:.2f} -> {eps0:.2f})"
                 return False, f"not consistently positive"

            g1 = (eps0 - eps1) / abs(eps1)
            g2 = (eps1 - eps2) / abs(eps2)
            g3 = (eps2 - eps3) / abs(eps3)
            avg_growth = (g1 + g2 + g3) / 3

            if avg_growth < 0.25:
                return False, f"{avg_growth:.1%} < 25%"

            return True, f"{avg_growth:.1%} >= 25%"
        except Exception as e:
            return False, f"error"

    def _check_quarterly_eps_yoy_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 5:
                return False, "data < 5 quarters"

            eps0 = eps_data.iloc[0]
            eps4 = eps_data.iloc[4]

            if not self.isfloat(eps0) or not self.isfloat(eps4):
                 return False, "invalid data"

            if eps0 <= 0:
                return False, f"latest quarter({eps0:.2f}) not positive"
            if eps4 <= 0:
                return True, f"turned positive ({eps4:.2f} -> {eps0:.2f})"

            growth = (eps0 - eps4) / abs(eps4)
            if growth < 0.25:
                return False, f"{growth:.1%} < 25%"

            return True, f"{growth:.1%} >= 25%"
        except Exception as e:
            return False, f"error"

    def _check_consecutive_quarterly_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 2:
                return False, "data < 2 quarters"

            eps0 = eps_data.iloc[0]
            eps1 = eps_data.iloc[1]

            if not self.isfloat(eps0) or not self.isfloat(eps1):
                 return False, "invalid data"

            if eps0 <= eps1:
                return False, f"{eps1:.2f} -> {eps0:.2f}"

            return True, f"{eps1:.2f} -> {eps0:.2f}"
        except Exception as e:
            return False, f"error"

    def get_fundamental_screening_results(self, roe):
        results = {}
        results['ROE'] = self._check_roe(roe)
        results['EPS Annual Growth'] = self._check_annual_eps_growth()
        results['EPS YoY Growth'] = self._check_quarterly_eps_yoy_growth()
        results['EPS Quarterly Growth'] = self._check_consecutive_quarterly_eps_growth()

        # 4項目中3項目以上がTrueならPassとする
        num_passed = sum(res[0] for res in results.values())
        final_pass = num_passed >= 3

        return final_pass, results

    def _format_million(self, val):
        if not self.isfloat(val):
            return "N/A"
        return f"{val/1e6:.1f}M"

    def get_formatted_earnings_summary(self):
        """Formats the quarterly earnings data for chart display."""
        try:
            if self.earnings_history is None or self.quarterly_income_stmt is None:
                return "N/A"

            # 過去4四半期に絞る
            earnings_df = self.earnings_history.tail(4).sort_index(ascending=False)

            lines = []
            for i in range(min(len(earnings_df), 4)):
                report_date = earnings_df.index[i].strftime('%Y-%m-%d')

                actual_eps = earnings_df['Reported EPS'].iloc[i]
                estimated_eps = earnings_df['EPS Estimate'].iloc[i]

                # 対応する収益レポートを見つける
                # 日付が一番近いものを採用
                matching_rev_date = self.quarterly_income_stmt.index[
                    self.quarterly_income_stmt.index.get_loc(earnings_df.index[i], method='nearest')
                ]
                actual_revenue = self.quarterly_income_stmt.loc[matching_rev_date, 'Total Revenue']

                # 予想収益はearnings_historyにはないので、ここではN/Aとする
                # (より正確な情報を得るには別のAPIソースが必要になる可能性がある)
                estimated_revenue = "N/A"

                eps_beat = "O" if actual_eps > estimated_eps else "X"
                rev_beat = "N/A" # 予想収益がないため

                lines.append(f"{report_date}")
                lines.append(f" - Revenue : {self._format_million(actual_revenue)} vs {estimated_revenue} : {rev_beat}")
                lines.append(f" - EPS : {actual_eps:.2f} vs {estimated_eps:.2f} : {eps_beat}")

            return "\n".join(lines)
        except Exception as e:
            # print(f"Error formatting earnings: {e}")
            return "N/A" # エラー時はN/Aを返す

    # The following methods are kept for compatibility with original DrawChart, but are now deprecated
    def getAnnualEPS(self):
        return "N/A", "N/A"
    def getQuarterlyEPS(self):
        return "N/A"

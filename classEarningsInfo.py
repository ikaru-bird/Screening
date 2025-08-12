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
        self.revenue_estimate = None
        try:
            # Data is fetched on demand from the ticker object
            self.income_stmt = self.ticker.income_stmt
            self.quarterly_income_stmt = self.ticker.quarterly_income_stmt
            self.earnings_history = self.ticker.earnings_history
            self.revenue_estimate = self.ticker.revenue_estimate
        except Exception as e:
            print(f"Could not fetch financial data for {self.ticker.ticker}: {e}")

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
            if self.earnings_history is None or self.quarterly_income_stmt is None or self.revenue_estimate is None:
                return "N/A"

            earnings_df = self.earnings_history.tail(4).sort_index(ascending=False)

            lines = []
            for i in range(min(len(earnings_df), 4)):
                report_date_dt = earnings_df.index[i]
                report_date = report_date_dt.strftime('%Y-%m-%d')

                actual_eps = earnings_df['epsActual'].iloc[i]
                estimated_eps = earnings_df['epsEstimate'].iloc[i]

                matching_rev_date = self.quarterly_income_stmt.index[
                    self.quarterly_income_stmt.index.get_loc(report_date_dt, method='nearest')
                ]
                actual_revenue = self.quarterly_income_stmt.loc[matching_rev_date, 'Total Revenue']

                # Find the corresponding revenue estimate
                # The revenue_estimate index is often named 'period' and is like '0q', '-1q'
                # We will assume the order matches the earnings history
                estimated_revenue = "N/A"
                if self.revenue_estimate is not None and i < len(self.revenue_estimate):
                     est_rev_series = self.revenue_estimate.iloc[i]
                     if 'avg' in est_rev_series:
                         estimated_revenue = est_rev_series['avg']

                eps_beat_char = "O" if actual_eps > estimated_eps else "X"

                rev_beat_char = "N/A"
                if self.isfloat(actual_revenue) and self.isfloat(estimated_revenue):
                    rev_beat_char = "O" if actual_revenue > estimated_revenue else "X"

                lines.append(f"{report_date}")
                lines.append(f" {rev_beat_char} : Revenue : {self._format_million(actual_revenue)} vs {self._format_million(estimated_revenue)}")
                lines.append(f" {eps_beat_char} : EPS : {actual_eps:.2f} vs {estimated_eps:.2f}")

            return "\n".join(lines)
        except Exception as e:
            return "N/A"

    # The following methods are kept for compatibility with original DrawChart, but are now deprecated
    def getAnnualEPS(self):
        return "N/A", "N/A"
    def getQuarterlyEPS(self):
        return "N/A"

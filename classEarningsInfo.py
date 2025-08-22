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
        self.earnings_estimate = None
        try:
            # Data is fetched on demand from the ticker object
            self.income_stmt = self.ticker.income_stmt
            self.quarterly_income_stmt = self.ticker.quarterly_income_stmt
            self.earnings_history = self.ticker.earnings_history
            self.revenue_estimate = self.ticker.revenue_estimate
            self.earnings_estimate = self.ticker.earnings_estimate
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

        eps_series = None

        # Try 'Basic EPS' first
        if 'Basic EPS' in stmt.index:
            series = stmt.loc['Basic EPS']
            # Check if the series contains at least one valid number
            if series.notna().any():
                eps_series = series

        # If 'Basic EPS' is not good, try 'Diluted EPS'
        if eps_series is None and 'Diluted EPS' in stmt.index:
            series = stmt.loc['Diluted EPS']
            # Check if the series contains at least one valid number
            if series.notna().any():
                eps_series = series

        return eps_series

    def _check_roe(self, roe):
        if not self.isfloat(roe):
            return None, "N/A"
        if float(roe) < 0.15:
            return False, f"{float(roe):.1%} < 15%"
        return True, f"{float(roe):.1%} >= 15%"

    def _check_annual_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.income_stmt)
            if eps_data is None or len(eps_data) < 4:
                return None, "data < 4 years"

            eps_list = eps_data.head(4).tolist()
            eps0, eps1, eps2, eps3 = eps_list

            if any(not self.isfloat(e) for e in eps_list):
                return None, "invalid data"

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
            return None, f"error"

    def _check_quarterly_eps_yoy_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 5:
                return None, "data < 5 quarters"

            eps0 = eps_data.iloc[0]
            eps4 = eps_data.iloc[4]

            if not self.isfloat(eps0) or not self.isfloat(eps4):
                 return None, "invalid data"

            if eps0 <= 0:
                return False, f"latest quarter({eps0:.2f}) not positive"
            if eps4 <= 0:
                return True, f"turned positive ({eps4:.2f} -> {eps0:.2f})"

            growth = (eps0 - eps4) / abs(eps4)
            if growth < 0.25:
                return False, f"{growth:.1%} < 25%"

            return True, f"{growth:.1%} >= 25%"
        except Exception as e:
            return None, f"error"

    def _check_consecutive_quarterly_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 2:
                return None, "data < 2 quarters"

            eps0 = eps_data.iloc[0]
            eps1 = eps_data.iloc[1]

            if not self.isfloat(eps0) or not self.isfloat(eps1):
                 return None, "invalid data"

            if eps0 <= eps1:
                return False, f"{eps1:.2f} -> {eps0:.2f}"

            return True, f"{eps1:.2f} -> {eps0:.2f}"
        except Exception as e:
            return None, f"error"

    def get_fundamental_screening_results(self, roe):
        results = {}
        results['ROE'] = self._check_roe(roe)
        results['EPS Annual Growth'] = self._check_annual_eps_growth()
        results['EPS YoY Growth'] = self._check_quarterly_eps_yoy_growth()
        results['EPS Quarterly Growth'] = self._check_consecutive_quarterly_eps_growth()

        # 4項目中3項目以上がTrueまたはNoneならPassとする
        # num_passed = sum(res[0] for res in results.values())
        num_passed = sum(1 for res in results.values() if res[0] is True or res[0] is None)
        final_pass = num_passed >= 3

        return final_pass, results

    def _format_million(self, val):
        if not self.isfloat(val):
            return "N/A"
        return f"{val/1e6:.1f}M"

    def get_formatted_earnings_summary(self):
        """Formats the quarterly earnings data for chart display based on user-specified format."""
        lines = []

        # --- Next Quarter Estimates ---
        try:
            next_qtr_rev_str = "N/A"
            if self.revenue_estimate is not None and not self.revenue_estimate.empty and '+1q' in self.revenue_estimate.index:
                next_qtr_rev_val = self.revenue_estimate.loc['+1q', 'avg']
                next_qtr_rev_str = self._format_million(next_qtr_rev_val)

            next_qtr_eps_str = "N/A"
            if self.earnings_estimate is not None and not self.earnings_estimate.empty and '+1q' in self.earnings_estimate.index:
                next_qtr_eps_val = self.earnings_estimate.loc['+1q', 'avg']
                if self.isfloat(next_qtr_eps_val):
                    next_qtr_eps_str = f"{next_qtr_eps_val:.2f}"

            if next_qtr_rev_str != "N/A" or next_qtr_eps_str != "N/A":
                lines.append("Next Qtr.")
                lines.append(f"  Revenue : {next_qtr_rev_str}")
                lines.append(f"  EPS : {next_qtr_eps_str}")
        except Exception:
            pass # Ignore if estimates can't be fetched

        # --- Past Quarters History ---
        try:
            if self.earnings_history is None or self.earnings_history.empty:
                if not lines:
                     return "N/A"
                else:
                     return "\n".join(lines)

            earnings_df = self.earnings_history.tail(4).sort_index(ascending=False)

            for i in range(min(len(earnings_df), 4)):
                report_date_dt = earnings_df.index[i]
                report_date = report_date_dt.strftime('%Y-%m-%d')
                lines.append(f"{report_date}")

                # --- Revenue (Actuals only) ---
                actual_revenue_str = "N/A"
                if self.quarterly_income_stmt is not None and not self.quarterly_income_stmt.empty and 'Total Revenue' in self.quarterly_income_stmt.index:
                    try:
                        matching_rev_date = self.quarterly_income_stmt.columns[abs(self.quarterly_income_stmt.columns - report_date_dt).argmin()]
                        if abs(matching_rev_date - report_date_dt).days < 30:
                            actual_revenue = self.quarterly_income_stmt.loc['Total Revenue', matching_rev_date]
                            actual_revenue_str = self._format_million(actual_revenue)
                    except Exception:
                        pass
                lines.append(f"  Revenue : {actual_revenue_str}")

                # --- EPS (Actual vs Estimate) ---
                actual_eps = earnings_df['epsActual'].iloc[i]
                estimated_eps = earnings_df['epsEstimate'].iloc[i]

                if self.isfloat(actual_eps) and self.isfloat(estimated_eps):
                    eps_beat_char = "O" if actual_eps > estimated_eps else "X"
                    lines.append(f"{eps_beat_char} EPS : {actual_eps:.2f} vs {estimated_eps:.2f}")
                else:
                    actual_eps_str = f"{actual_eps:.2f}" if self.isfloat(actual_eps) else "N/A"
                    est_eps_str = f"{estimated_eps:.2f}" if self.isfloat(estimated_eps) else "N/A"
                    lines.append(f"- EPS : {actual_eps_str} vs {est_eps_str}")

        except Exception as e:
            if lines:
                return "\n".join(lines)
            return "N/A"

        if not lines:
            return "N/A"

        return "\n".join(lines)

    # The following methods are kept for compatibility with original DrawChart, but are now deprecated
    def getAnnualEPS(self):
        return "N/A", "N/A"
    def getQuarterlyEPS(self):
        return "N/A"

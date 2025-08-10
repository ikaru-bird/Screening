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
        try:
            # Data is fetched on demand from the ticker object
            self.income_stmt = self.ticker.income_stmt
            self.quarterly_income_stmt = self.ticker.quarterly_income_stmt
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
            return False, "ROE N/A"
        if float(roe) < 0.15:
            return False, f"ROE({float(roe):.1%}) < 15%"
        return True, f"ROE({float(roe):.1%}) >= 15%"

    def _check_annual_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.income_stmt)
            if eps_data is None or len(eps_data) < 4:
                return False, "Annual EPS data < 4 years"

            eps_list = eps_data.head(4).tolist()
            eps0, eps1, eps2, eps3 = eps_list

            if any(not self.isfloat(e) for e in eps_list):
                return False, "Invalid annual EPS data"

            if eps0 <= 0 or eps1 <= 0 or eps2 <= 0 or eps3 <= 0:
                 if eps0 > 0 and eps3 < 0:
                    return True, f"Turnaround annual EPS ({eps3:.2f} -> {eps0:.2f})"
                 return False, f"EPS not consistently positive for growth check"

            g1 = (eps0 - eps1) / abs(eps1)
            g2 = (eps1 - eps2) / abs(eps2)
            g3 = (eps2 - eps3) / abs(eps3)
            avg_growth = (g1 + g2 + g3) / 3

            if avg_growth < 0.25:
                return False, f"Avg annual EPS growth({avg_growth:.1%}) < 25%"

            return True, f"Avg annual EPS growth({avg_growth:.1%}) >= 25%"
        except Exception as e:
            return False, f"Error in annual EPS check: {e}"

    def _check_quarterly_eps_yoy_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 5:
                return False, "Quarterly EPS data < 5 quarters"

            eps0 = eps_data.iloc[0]
            eps4 = eps_data.iloc[4]

            if not self.isfloat(eps0) or not self.isfloat(eps4):
                 return False, "Invalid quarterly EPS data"

            if eps0 <= 0:
                return False, f"Latest quarter EPS({eps0:.2f}) not positive"
            if eps4 <= 0:
                return True, f"Quarterly EPS turned positive ({eps4:.2f} -> {eps0:.2f})"

            growth = (eps0 - eps4) / abs(eps4)
            if growth < 0.25:
                return False, f"Quarterly YoY growth({growth:.1%}) < 25%"

            return True, f"Quarterly YoY growth({growth:.1%}) >= 25%"
        except Exception as e:
            return False, f"Error in quarterly EPS check: {e}"

    def _check_consecutive_quarterly_eps_growth(self):
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 2:
                return False, "Quarterly data < 2 quarters"

            eps0 = eps_data.iloc[0]
            eps1 = eps_data.iloc[1]

            if not self.isfloat(eps0) or not self.isfloat(eps1):
                 return False, "Invalid consecutive quarterly EPS data"

            if eps0 <= eps1:
                return False, f"Not growing consecutively ({eps1:.2f} -> {eps0:.2f})"

            return True, f"Growing consecutively ({eps1:.2f} -> {eps0:.2f})"
        except Exception as e:
            return False, f"Error in consecutive EPS check: {e}"

    def get_fundamental_screening_results(self, roe):
        results = {}
        results['ROE'] = self._check_roe(roe)
        results['Annual EPS Growth'] = self._check_annual_eps_growth()
        results['Quarterly EPS YoY Growth'] = self._check_quarterly_eps_yoy_growth()
        results['Consecutive Quarterly EPS Growth'] = self._check_consecutive_quarterly_eps_growth()
        all_passed = all(res[0] for res in results.values())
        return all_passed, results

    def getQuarterlyEarnings(self):
        """チャート表示用に四半期決算情報を整形する"""
        try:
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 4:
                return "N/A"

            lines = []
            for i in range(4):
                quarter_date = eps_data.index[i].strftime('%Y-%m-%d')
                eps_value = eps_data.iloc[i]
                lines.append(f"{quarter_date}: EPS {eps_value:.2f}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error formatting earnings: {e}"

    # The following methods are kept for compatibility with original DrawChart, but are now deprecated
    def getAnnualEPS(self):
        return "N/A", "N/A"
    def getQuarterlyEPS(self):
        return "N/A"

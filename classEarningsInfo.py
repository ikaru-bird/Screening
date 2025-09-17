# coding: UTF-8

import pandas as pd
import datetime as dt
import yfinance as yf # Import yfinance here
import math

class EarningsInfo():
    # --- ファンダメンタル・スクリーニングの閾値設定 ---
    # ここで設定した値に基づいて、各ファンダメンタル項目が評価されます。
    FUNDAMENTAL_THRESHOLDS = {
        # ROE (自己資本利益率) の閾値。これを上回る必要があります。(Strict:0.15 Midium:0.12)
        'ROE_THRESHOLD': 0.12,

        # 年次EPS（1株当たり利益）成長率の閾値。過去3年間の平均成長率がこれを上回る必要があります。(Strict:0.25 Midium:0.15)
        'ANNUAL_EPS_GROWTH_THRESHOLD': 0.15,

        # 四半期EPSの前年同期比（YoY）成長率の閾値。これを上回る必要があります。(Strict:0.25 Midium:0.15)
        'QUARTERLY_EPS_YOY_GROWTH_THRESHOLD': 0.15,

        # 最新の四半期EPSが、直前の四半期EPSを上回っているかのチェック。
        # Trueの場合、成長が加速していると判断します。
        # この項目は成長率ではなく、大小比較のみを行います。
        # earningsQuarterlyGrowthが利用可能な場合は、その値がこの閾値を超えているかを見ます。(Strict:0.25 Midium:0.15)
        'CONSECUTIVE_QUARTERLY_EPS_GROWTH_THRESHOLD': 0.15,

        # スクリーニングをパスするために必要な項目数。
        # 上記4つの項目のうち、何項目がTrueまたはNone（データなし）であれば合格とするか。
        'PASSING_CRITERIA_COUNT': 3
    }

    def __init__(self, ticker_obj, info=None):
        self.ticker = ticker_obj
        self.info = info if info is not None else {}
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
            f = float(str(s))
            return not (math.isnan(f) or math.isinf(f))
        except (ValueError, TypeError):
            return False

    def _get_eps_from_stmt(self, stmt):
        if stmt is None:
            return None
        if 'Basic EPS' in stmt.index:
            return stmt.loc['Basic EPS']
        return None

    def _check_roe(self, roe):
        threshold = self.FUNDAMENTAL_THRESHOLDS['ROE_THRESHOLD']
        if not self.isfloat(roe):
            return None, "N/A"
        if float(roe) < threshold:
            return False, f"{float(roe):.1%} < {threshold:.0%}"
        return True, f"{float(roe):.1%} >= {threshold:.0%}"

    def _check_annual_eps_growth(self):
        threshold = self.FUNDAMENTAL_THRESHOLDS['ANNUAL_EPS_GROWTH_THRESHOLD']
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
                 return False, f"not positive"

            g1 = (eps0 - eps1) / abs(eps1) if abs(eps1) != 0 else 0
            g2 = (eps1 - eps2) / abs(eps2) if abs(eps2) != 0 else 0
            g3 = (eps2 - eps3) / abs(eps3) if abs(eps3) != 0 else 0
            avg_growth = (g1 + g2 + g3) / 3

            if math.isnan(avg_growth):
                return None, "unavailable"

            if avg_growth < threshold:
                return False, f"{avg_growth:.1%} < {threshold:.0%}"

            return True, f"{avg_growth:.1%} >= {threshold:.0%}"
        except Exception as e:
            return None, f"error"

    def _check_quarterly_eps_yoy_growth(self):
        threshold = self.FUNDAMENTAL_THRESHOLDS['QUARTERLY_EPS_YOY_GROWTH_THRESHOLD']
        try:
            # --- Primary Source: ticker.info ---
            growth = self.info.get('earningsQuarterlyGrowth')
            if self.isfloat(growth):
                if growth < threshold:
                    return False, f"{growth:.1%} < {threshold:.0%}"
                return True, f"{growth:.1%} >= {threshold:.0%}"

            # --- Fallback Source: Statements/History ---
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 5:
                if self.earnings_history is not None and not self.earnings_history.empty and len(self.earnings_history) >= 5:
                    eps_data = self.earnings_history['epsActual']
                else:
                    return None, "data < 5 quarters"

            eps0 = eps_data.iloc[0]
            eps4 = eps_data.iloc[4]

            if not self.isfloat(eps0) or not self.isfloat(eps4):
                 return None, "invalid data"

            if eps0 <= 0:
                return False, f"latest quarter({eps0:.2f}) not positive"
            if eps4 <= 0:
                return True, f"turned positive ({eps4:.2f} -> {eps0:.2f})"

            growth = (eps0 - eps4) / abs(eps4) if abs(eps4) != 0 else 0
            if growth < threshold:
                return False, f"{growth:.1%} < {threshold:.0%}"

            return True, f"{growth:.1%} >= {threshold:.0%}"
        except Exception as e:
            return None, f"error"

    def _check_consecutive_quarterly_eps_growth(self):
        threshold = self.FUNDAMENTAL_THRESHOLDS['CONSECUTIVE_QUARTERLY_EPS_GROWTH_THRESHOLD']
        try:
            # --- Primary Source: ticker.info (using YoY as a proxy for strength) ---
            growth = self.info.get('earningsQuarterlyGrowth')
            if self.isfloat(growth):
                if growth > threshold: # Use same threshold as YoY
                    return True, f"{growth:.1%}"
                else:
                    return False, f"{growth:.1%}"

            # --- Fallback Source: Statements/History ---
            eps_data = self._get_eps_from_stmt(self.quarterly_income_stmt)
            if eps_data is None or len(eps_data) < 2:
                if self.earnings_history is not None and not self.earnings_history.empty and len(self.earnings_history) >= 2:
                    eps_data = self.earnings_history['epsActual']
                else:
                    return None, "data < 2 quarters"

            eps0 = eps_data.iloc[0]
            eps1 = eps_data.iloc[1]

            if not self.isfloat(eps0) or not self.isfloat(eps1):
                 return None, "unavailable"

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

        # 4項目中、設定した数以上がTrueまたはNullならPassとする
        passing_count = self.FUNDAMENTAL_THRESHOLDS['PASSING_CRITERIA_COUNT']
        num_passed = sum(1 for res in results.values() if res[0] is True or res[0] is None)
        final_pass = num_passed >= passing_count

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
                try:  # 売上高取得を個別にtry-catchで囲む
                    if self.quarterly_income_stmt is not None and not self.quarterly_income_stmt.empty and 'Total Revenue' in self.quarterly_income_stmt.index:
                        matching_rev_date = self.quarterly_income_stmt.columns[abs(self.quarterly_income_stmt.columns - report_date_dt).argmin()]
                        if abs(matching_rev_date - report_date_dt).days < 30:
                            actual_revenue = self.quarterly_income_stmt.loc['Total Revenue', matching_rev_date]
                            actual_revenue_str = self._format_million(actual_revenue)
                except Exception:
                    pass  # エラーが発生しても actual_revenue_str = "N/A" のまま続行
                
                lines.append(f"  Revenue : {actual_revenue_str}")

                # --- EPS (Actual vs Estimate) ---
                try:  # EPS取得も個別にtry-catchで囲む
                    actual_eps = earnings_df['epsActual'].iloc[i]
                    estimated_eps = earnings_df['epsEstimate'].iloc[i]

                    if self.isfloat(actual_eps) and self.isfloat(estimated_eps):
                        eps_beat_char = "O" if actual_eps > estimated_eps else "X"
                        lines.append(f"{eps_beat_char} EPS : {actual_eps:.2f} vs {estimated_eps:.2f}")
                    else:
                        actual_eps_str = f"{actual_eps:.2f}" if self.isfloat(actual_eps) else "N/A"
                        est_eps_str = f"{estimated_eps:.2f}" if self.isfloat(estimated_eps) else "N/A"
                        lines.append(f"-- EPS : {actual_eps_str} vs {est_eps_str}")
                except Exception:
                    lines.append("-- EPS : N/A vs N/A")  # EPSでエラーが発生した場合

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

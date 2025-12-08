# coding: UTF-8

import os, fnmatch
import pandas as pd
import datetime as dt
import time
import pytz
from classDrawChart import DrawChart

#---------------------------------------#
# 株価データ分析クラス
#---------------------------------------#
class CheckData():

    PATTERN_PARAMS = {
        'trend_templete': {
            'data_period_days': 728,
            'ma200_uptime_days': 20,
            'low_52w_period_days': 365,
            'price_vs_52w_low_ratio': 1.3,
            'price_vs_52w_high_ratio': 0.75,
        },
        'buy_point': {
            'data_period_days': 728,
            'ma200_slope_threshold': 0.0005,
            'rebound_ma200_ratio': 1.01,
            'pullback_ma200_ratio': 0.9,
            'pullback_ma50_ratio': 1.01,
        },
        'golden_cross': {
            'data_period_days': 728,
            'ma200_slope_threshold': 0.0005,
        },
        'short_sign': {
            'data_period_days': 455,
            'test_count': 3,
        },
        'vcp': {
            'peak_search_days': 90,
            'contractions': [
                {'depth': (0.65, 0.75), 'retracement': (0.95, 1.0)},
                {'depth': (0.8, 0.9),   'retracement': (0.95, 1.0)},
                {'depth': (0.9, 0.97),  'retracement': (1.0, 1.0)} # retracement is not checked for the last one
            ],
            'pivot_range': 0.01, # +/- 1%
            'atr_factor': 0.5, # ATRによる動的調整のための係数
        },
        'vcp2': { # This is a variation, maybe merge later
            'peak_search_days': 90,
            'contraction1_depth': (0.65, 0.75),
            'contraction1_retracement': (0.95, 1.0),
            'contraction2_depth': (0.8, 0.9), # from retracement1
            'contraction3_depth': (0.9, 0.97), # from retracement1
            'pivot_range': 0.01,
        },
        'double_bottom': {
            'peak_search_days': 60,
            'retracement_days_ratio': 0.67,
            'retracement_ratio': (0.92, 1.0),
            'bottom2_search_days_ratio': 0.5,
            'bottom_similarity_ratio': (0.92, 1.0),
            'pivot_ratio': 0.98,
        },
        'double_bottom2': { # This is a variation
            'peak_search_days': 60,
            'bottom1_search_days_ratio': 0.5,
            'bottom_similarity_ratio': (0.92, 1.0),
            'retracement_ratio': (0.92, 1.0),
            'pivot_ratio': 0.98,
        },
        'cup_with_handle': {
            'lookback_period': "2y",
            'uptrend_lookback_days': 90,
            'uptrend_min_rise_factor': 1.3,
            'cup_min_depth_factor': 1.25,
            'cup_min_duration_days': 49,
            'cup_max_duration_days': 455,
            'cup_lip_max_deviation': 1.10,
            'cup_lip_min_deviation': 0.90,
            'cup_min_rounded_points': 5,
            'handle_max_duration_days': 35,
            'handle_min_duration_days': 5,
            'handle_depth_min_factor': 0.85,
            'handle_depth_max_factor': 1.00,
            'pivot_lookahead_days': 180,
            'volume_breakout_factor': 1.5,
        },
        'flat_base': {
            'peak_search_days_ago': 7, # self.outPeriod
            'base_min_rise_ratio': 1.2,
            'base_depth': (0.85, 0.95),
            'base_duration_weeks': (4, 8),
            'breakout_volume_multiplier': 1.5, # ブレイクアウト時の出来高乗数
        },
        'on_minervini': {
            'base_weeks_min': 7,
            'base_weeks_max': 65,
            'volatility_multiplier_min': 2.0,
            'volatility_multiplier_max': 3.0,
            'volume_reduction_threshold': 0.3,
        }
    }

#---------------------------------------#
# コンストラクタ
#---------------------------------------#
    def __init__(self, out_path, chart_dir, ma_short, ma_mid, ma_s_long, ma_long, rs_csv1, rs_csv2, txt_path, timezone_str=None):

        # パラメータをセット
        self.params = self.PATTERN_PARAMS

        # 移動平均の期間をセット
        self.ma_short   = ma_short
        self.ma_mid     = ma_mid
        self.ma_s_long  = ma_s_long
        self.ma_long    = ma_long

        # チャートを出力する期間
        self.outPeriod = 7

        # データ処理用DataFrame(空箱)
        self.df = pd.DataFrame()

        # ファイル名・ティッカー文字列格納用
        self.strBaseName = "---"
        self.strTicker   = "---"

        # 今日の日付をセット
        self.today = dt.datetime.now(pytz.utc)
        if timezone_str:
            self.display_tz = pytz.timezone(timezone_str)
        else:
            self.display_tz = None

        # CSVの読込時に日付で絞り込む場合は指定
#       self.start_dt = self.today - dt.timedelta(days=455)  # 65週前の日付
#       self.start_dt = self.today - dt.timedelta(days=728)  # 104週前の日付

        # チャートの出力先
        self.base_dir = chart_dir

        # チャート出力クラスの作成
        self.chart = DrawChart(self.ma_short, self.ma_mid, self.ma_s_long, self.ma_long, rs_csv1, rs_csv2, txt_path)

        # 決算情報(空箱)
        self.ern_info = None

        # ファイルの存在チェック
        is_file = os.path.isfile(out_path)
        if is_file == True:
#           self.w = open(out_path, mode="a", encoding="CP932", errors="ignore")
            self.w = open(out_path, mode="a", encoding="utf-8", errors="ignore")
        else:
            # 出力ファイルの作成
#           self.w = open(out_path, mode="w", encoding="CP932", errors="ignore")
            self.w = open(out_path, mode="w", encoding="utf-8", errors="ignore")
            # ファイルのヘッダー出力
            self.w.write("\"日付\",\"タイプ\",\"コード\",\"会社名\",\"業種区分\",\"業種RS\",\"UDVR\",\"UDVR.prev\",\"UD判定\",\"VOLUME\",\"Price\"\n")
            self.w.flush()

#---------------------------------------#
# デストラクタ
#---------------------------------------#
    def __del__(self):
        # 出力ファイルを閉じる
        self.w.close()

#---------------------------------------#
# 決算情報をセット
#---------------------------------------#
    def set_earnings_info(self, ern_info):
        self.ern_info = ern_info

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（メイン）
#------------------------------------------------#
    def isTrendTemplete(self):
        """
        トレンドテンプレートの条件を満たしているかチェックします。
        満たしている場合はTrueを返し、後続の買いサイン判定を呼び出します。
        このメソッドはchkData.pyのメインロジックから呼び出されることを想定しています。
        """
        res = self.TrendTemplete_Check()
        is_pass = (res[0] >= 7)

        if is_pass:
            print(self.strTicker + " is ::: Trend Templete ::: ")
            # isBuySignの呼び出しは、ファンダメンタルチェックをパスした後に
            # chkData.py側で制御するため、ここでは呼び出さない。
            # self.isBuySign()

        return is_pass

#------------------------------------------------#
# トレンドテンプレート判定処理スタート（全件チャート出力）
#------------------------------------------------#
    def isTrendTempleteAll(self):

    # 処理呼び出し
        res = self.TrendTemplete_Check()
        td_abs = abs(self.today - res[1])
#       if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
        if (res[0] >= 7):
            strLabel = "trend templete"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し

#------------------------------------------------#
# 買いサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isBuySign(self):

    # 処理呼び出し
        # Cup with Handle判定
        res = self.Cup_with_Handle_Check()
        td_abs = abs(self.today - res[1])
        if (res[0] >= 4) and (td_abs.days <= self.outPeriod):
            strLabel = "cup with handle(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        else:
            # Flat Base判定
            res = self.FlatBase_Check()
            td_abs = abs(self.today - res[1])
            if (res[0] >= 3) and (td_abs.days <= self.outPeriod):
                strLabel = "flat base(" + str(res[0]) + ")"
                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
            else:
                # Double Bottom判定
                res = self.DoubleBottom_Check()
                td_abs = abs(self.today - res[1])
                if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                    strLabel = "double bottom(" + str(res[0]) + ")"
                    self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
                else:
                    # VCP判定
                    res = self.VCP_Check()
                    td_abs = abs(self.today - res[1])
                    if (res[0] >= 7) and (td_abs.days <= self.outPeriod):
                        strLabel = "vcp(" + str(res[0]) + ")"
                        self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
#                            else:
#                                # ON_Minervini_Check
#                                res = self.ON_Minervini_Check()
#                                if (res[0] == 1):
#                                    td_abs = abs(self.today - res[1])
#                                    if (td_abs.days <= self.outPeriod):
#                                        strLabel = "Base Formation"
#                                        self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（オニミネ・ニパターン）
#------------------------------------------------#
    def isON_Minervini(self):

    # 処理呼び出し
        res = self.ON_Minervini_Check()
        if (res[0] == 1):
            td_abs = abs(self.today - res[1])
            if (td_abs.days <= self.outPeriod):
                strLabel = "Base Formation"
                self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（グランビルの法則）
#------------------------------------------------#
    def isGranville(self):

    # 処理呼び出し
        res = self.BuyPoint_Check()
        td_abs = abs(self.today - res[1])
        if ((res[0] == 1) or (res[0] == 3) or (res[0] == 50)) and (td_abs.days <= self.outPeriod):
            strLabel = "buy sign(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 買いサイン判定処理スタート（Goldern Cross判定）
#------------------------------------------------#
    def isGoldernCross(self):

    # 処理呼び出し
        res = self.GC_Check()
        td_abs = abs(self.today - res[1])
        if (res[0] != "0") and (td_abs.days <= self.outPeriod):
            strLabel = "golden cross(" + str(res[0]) + ")"
            self.writeFlles(res, strLabel)  # CSV、チャート書き込み呼び出し
        return

#------------------------------------------------#
# 売りサイン判定処理スタート（メイン）
#------------------------------------------------#
    def isShortSign(self):

    # 処理呼び出し
        res = self.ShortSign_Check()

    # 出力ファイルへ書き込み（ステータスが5以上かつ指定日以内のの場合）
        td_abs = abs(self.today - res[1])
        if (res[0] >= 5) and (td_abs.days <= self.outPeriod):
                strLabel = "short sign"
                self.writeFlles(res, strLabel) # CSV、チャート書き込み呼び出し
        return

#---------------------------------------#
# トレンドテンプレート判定処理
#---------------------------------------#
    def TrendTemplete_Check(self):

    # Dataframeをセット
        df0 = self.df
        p = self.params['trend_templete']

        start_dt = self.today - dt.timedelta(days=p['data_period_days'])
        try:
            pass
        except Exception as e:
            print(e)
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 直近の日付、終値
        if len(df0.index) > 0:
            idxtoday = df0.index[-1]
            close_p  = df0.loc[idxtoday, 'Close']
        else:
            return 0, start_dt

    # ① 終値が150日と200日移動平均線より上
        if (close_p >= df0.loc[idxtoday, 'MA150']) and (close_p >= df0.loc[idxtoday, 'MA200']):
            pass
        else:
            return 0, start_dt

    # ② 150日移動平均線が200日移動平均線より上
        if df0.loc[idxtoday, 'MA150'] >= df0.loc[idxtoday, 'MA200']:
            pass
        else:
            return 1, start_dt

    # ③ 200日移動平均線が少なくとも1ヵ月以上上昇トレンド
        idx_pos = df0.index.get_loc(idxtoday)
        if idx_pos >= p['ma200_uptime_days']:
            idxlastm = df0.index[idx_pos - p['ma200_uptime_days']]
        else:
            idxlastm = df0.index[0]  # データ不足時は最古の比較対象を使用
        if (df0.loc[idxtoday, 'DIFF'] > 0) and (df0.loc[idxlastm, 'DIFF'] > 0):
            pass
        else:
            return 2, start_dt

    # ④ 50日移動平均線が150日、200日移動平均線より上
        if (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA150']) and (df0.loc[idxtoday, 'MA50'] >= df0.loc[idxtoday, 'MA200']):
            pass
        else:
            return 3, start_dt

    # ⑤ 現在の株価が50日移動平均線より上
        if close_p >= df0.loc[idxtoday, 'MA50']:
            pass
        else:
            return 4, start_dt

    # ⑥ 現在の株価が52週安値より少なくとも30％高い
        start_dt_52w = self.today - dt.timedelta(days=p['low_52w_period_days'])
        df1 = df0.query('@start_dt_52w <= index')           # データ範囲を絞り込み

        rows   = df1['Low']
        min_val = rows.min()
        idxmin = rows.idxmin()

        if close_p >= min_val * p['price_vs_52w_low_ratio']:
            pass
        else:
            return 5, start_dt

    # ⑦ 現在の株価は52週高値から25％以内
        rows   = df0['High']
        max_val = rows.max()
        idxmax = rows.idxmax()

        if close_p >= max_val * p['price_vs_52w_high_ratio']:
            return 7, idxtoday
        else:
            return 6, start_dt

#---------------------------------------#
# 買いシグナル判定処理
#---------------------------------------#
    def BuyPoint_Check(self):

    # Dataframeをセット
        df0 = self.df
        p = self.params['buy_point']
        slope_th = p['ma200_slope_threshold']

        start_dt = self.today - dt.timedelta(days=p['data_period_days'])
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 戻り値蓄積用リスト
        reslist = [[0,start_dt,0]]

    # 買い①：株価がMA200を超える（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close > MA200 and Close.shift(1) <= MA200.shift(1) and DIFF > @slope_th')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([1,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い②：株価がMA200を下回る（移動平均の傾きがプラス）
        try:
            df1 = df0.query('Close < MA200 and Close.shift(1) >= MA200.shift(1) and DIFF > @slope_th')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([2,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い③：株価がMA200上で反発（移動平均の傾きがプラス）
        try:
            rebound_ma200_ratio = p['rebound_ma200_ratio']
            df1 = df0.query('Close < MA10 and MA200 * @rebound_ma200_ratio >= Close >= MA200 and DIFF > @slope_th')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([3,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い④：株価がMA200を割って大きく下落（移動平均の傾きがプラス）
        try:
            pullback_ma200_ratio = p['pullback_ma200_ratio']
            df1 = df0.query('MA200 * @pullback_ma200_ratio >= Close and DIFF > @slope_th')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([4,buypoint_dt,df1.loc[buypoint_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 買い⑤：株価がMA50プルバック（移動平均の傾きがプラス）
        try:
            pullback_ma50_ratio = p['pullback_ma50_ratio']
            df1 = df0.query('Close < MA10 and MA50 * @pullback_ma50_ratio >= Close >= MA50 and Close.shift(1) > MA50.shift(1) * @pullback_ma50_ratio and DIFF > @slope_th')
            if len(df1.index) > 0:
                buypoint_dt = df1.index[0]
                buypoint_p  = df1.loc[buypoint_dt, "Close"]
                reslist.append([50, buypoint_dt, df1.loc[buypoint_dt, "DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 戻り値リストを日付で逆順ソート
        reslist = sorted(reslist, reverse=True, key=lambda x: x[1])  #[1]に注目してソート
        return reslist[0][0], reslist[0][1]

#---------------------------------------#
# ゴールデンクロス判定処理
#---------------------------------------#
    def GC_Check(self):

    # Dataframeをセット
        df0 = self.df
        p = self.params['golden_cross']
        slope_th = p['ma200_slope_threshold']

        start_dt = self.today - dt.timedelta(days=p['data_period_days'])
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み

    # 戻り値蓄積用リスト
        reslist = [["0",start_dt,0]]

    # ① MA50とMA150がゴールデンクロス（MA200の傾きがプラス）
        try:
            df1 = df0.query('MA50 > MA150 and MA50.shift(1) <= MA150.shift(1) and DIFF > @slope_th')
            if len(df1.index) > 0:
                gc_dt = df1.index[0]                      # MA50とMA150がGCした日
                buypoint_p = df1.loc[gc_dt, "Close"]
                reslist.append(["50-150",gc_dt,df1.loc[gc_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # ② MA150とMA200がゴールデンクロス（MA200の傾きがプラス）
        try:
            df1 = df0.query('MA150 > MA200 and MA150.shift(1) <= MA200.shift(1) and DIFF > @slope_th')
            if len(df1.index) > 0:
                gc_dt = df1.index[0]                      # MA150とMA200がGCした日
                buypoint_p = df1.loc[gc_dt, "Close"]
                reslist.append(["150-200",gc_dt,df1.loc[gc_dt,"DIFF"]])
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    # 戻り値リストを日付で逆順ソート
        reslist = sorted(reslist, reverse=True, key=lambda x: x[1])  #[1]に注目してソート
        return reslist[0][0], reslist[0][1]

#---------------------------------------#
# 売りシグナル判定処理
#---------------------------------------#
    def ShortSign_Check(self):

    # Dataframeをセット
        df0 = self.df
        p = self.params['short_sign']

        start_dt = self.today - dt.timedelta(days=p['data_period_days'])
        df0 = df0.query('@start_dt <= index')           # データ範囲を絞り込み
        rows = df0['High']

    #①期間の最高値日を取得
        if len(df0.index) > 0:
            max_val = rows.max()
            idxmax = rows.idxmax()
            pass
        else:
            return 0, start_dt

    #②出来高を伴う50日移動平均割れ
        df1 = df0.query('index > @idxmax and Close < MA50 and Volume > MA_VOL')

    # STEP2判定
        if len(df1.index) > 0:
            under_ma50_dt = df1.index[0]
            neckline_p    = df1.loc[under_ma50_dt, "Close"]
            pass
        else:
            return 1, idxmax

    #③その後、3回以上50日移動平均を超える
        i = 0
        for i in range(p['test_count']): # 3回ループ
            # 50日移動平均超え
            df1 = df0.query('index > @under_ma50_dt and Close > @neckline_p and Close > MA50')
            if len(df1.index) > 0:
                over_ma50_dt = df1.index[0]

                # 50日移動平均割れ
                df1 = df0.query('index > @over_ma50_dt and Close > @neckline_p and Close < MA50')
                if len(df1.index) > 0:
                    under_ma50_dt = df1.index[0]
                    continue
                else:
                    return 2, under_ma50_dt
                    break
            else:
                return 2, under_ma50_dt
                break
        else:
            pass

#    ④最後の上昇の出来高が少ない
#       print(int(df1.loc[over_ma50_dt, "Volume"]))
#       print(int(df1.loc[over_ma50_dt, "MA_VOL"]))

    # STEP4判定
        if df0.loc[over_ma50_dt, "Volume"] < df0.loc[over_ma50_dt, "MA_VOL"]:
            pass
        else:
            return 3, under_ma50_dt

    #⑤出来高を伴う下落
        df1 = df0.query('index > @over_ma50_dt and Close < MA50 and Volume > MA_VOL')

    # STEP5判定（出来高を伴う50日移動平均割れ）
        if len(df1.index) > 0:
            short_signal_dt = df1.index[0]
            return 5, short_signal_dt
        else:
            return 4, over_ma50_dt

#---------------------------------------#
# VCP判定処理
#---------------------------------------#
    def VCP_Check(self):

    # Dataframeを参照渡し
        df0 = self.df
        if df0.empty:
            return 0, self.today

        p = self.params['vcp']
        atr_factor = p.get('atr_factor', 0.5) # ATR係数を取得、なければデフォルト値

    #①最高値を探す
        df1  = df0[: self.today - dt.timedelta(days=p['peak_search_days'])]
        rows = df1['High']

        if len(df1.index) > 0:
            max_val = rows.max()
            idxmax = rows.idxmax()
        else:
            return 0, df0.index[-1]

        # 最高値時点のATRを取得し、動的調整値を計算
        try:
            atr_at_peak = df0.loc[idxmax, 'ATR']
            atr_ratio = (atr_at_peak / max_val) * atr_factor
        except (KeyError, ZeroDivisionError):
            atr_ratio = 0 # ATRが計算できない場合は調整なし

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min_val = rows.min()
        idxmin = rows.idxmin()

    # 最安値値判定 (ATRで動的調整)
        c = p['contractions'][0]
        depth_lower_bound = c['depth'][0] - atr_ratio
        depth_upper_bound = c['depth'][1] + atr_ratio
        if (min_val / max_val >= depth_lower_bound) and (min_val / max_val <= depth_upper_bound):
            pass
        else:
            return 1, idxmax

    #③1番底以降の最高値（戻り高値）を探す
#   #　最高値日と最安値日の同数以上
#       days_div = abs(int((idxmin - idxmax).days)) # 中間日の日数
#       df2  = df1[idxmin + dt.timedelta(days=days_div) : self.today]
        df2  = df1[idxmin : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            return 2, idxmin

    # 戻り高値判定
        if (max2 / max_val >= c['retracement'][0]) and (max2 / max_val <= c['retracement'][1]):
            pass
        else:
            return 2, idxmin

    #④戻り高値以降の二番底を探す
        df2  = df1[idxmax2 : self.today]
        rows = df2['Low']
        min2 = rows.min()
        idxmin2 = rows.idxmin()

    # 二番底判定 (ATRで動的調整)
        c = p['contractions'][1]
        depth_lower_bound = c['depth'][0] - atr_ratio
        depth_upper_bound = c['depth'][1] + atr_ratio
        if (min2 / max2 >= depth_lower_bound) and (min2 / max2 <= depth_upper_bound):
            pass
        else:
            return 3, idxmin2

    #⑤2番底以降の最高値（戻り高値）を探す
        df2  = df1[idxmin2 : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max3 = rows.max()
            idxmax3 = rows.idxmax()
        else:
            return 4, idxmin

    # 戻り高値判定
        if (max3 / max2 >= c['retracement'][0]) and (max3 / max2 <= c['retracement'][1]):
            pass
        else:
            return 4, idxmin

    #⑥戻り高値以降の三番底を探す
        df2  = df1[idxmax3 : self.today]
        rows = df2['Low']
        min3 = rows.min()
        idxmin3 = rows.idxmin()

    # 三番底判定 (ATRで動的調整)
        c = p['contractions'][2]
        depth_lower_bound = c['depth'][0] - atr_ratio
        depth_upper_bound = c['depth'][1] + atr_ratio
        if (min3 / max3 >= depth_lower_bound) and (min3 / max3 <= depth_upper_bound):
            pass
        else:
            return 5, idxmin2

    #⑦ピボット判定
        pivot_p1 = max3 * (1 - p['pivot_range'])
        pivot_p2 = max3 * (1 + p['pivot_range'])
        df2 = df1.query('index > @idxmin3 & @pivot_p1 <= High <= @pivot_p2')

    # STEP7判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            pass
        else:
            return 6, idxmax3

    #⑧ピボットBreakout判定
        df2 = df1.query('index > @pivot_dt1 & High >= @max3')

    # STEP8判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            return 8, pivot_dt2
        else:
            return 7, pivot_dt1

#---------------------------------------#
# Double Bottom判定処理
#---------------------------------------#
    def DoubleBottom_Check(self):

    # Dataframeを参照渡し
        df0 = self.df
        if df0.empty:
            return 1, self.today, []

        p = self.params['double_bottom']

    # 補助線描画用リスト
        alist= []

    #①最高値を探す
        df1  = df0[: self.today - dt.timedelta(days=p['peak_search_days'])]
        rows = df1['High']

        if len(df1.index) > 0:
            max_val = rows.max()
            idxmax = rows.idxmax()
            alist.append([idxmax, df0.loc[idxmax,"High"]])
        else:
            return 1, df0.index[-1], alist

    #②最高値以降の最安値を探す（1番底）
        df1  = df0[idxmax : self.today]
        rows = df1['Low']
        min_val = rows.min()
        idxmin = rows.idxmin()
        alist.append([idxmin, df0.loc[idxmin,"Low"]])

    #③1番底以降の最高値（戻り高値）を探す
    #　最高値日と最安値日の同数以上
        days_div = int(abs(int((idxmin - idxmax).days)) * p['retracement_days_ratio'])

        df2  = df1[idxmin + dt.timedelta(days=days_div) : self.today]
        rows = df2['High']

        if len(df2.index) > 0:
            max2 = rows.max()
            idxmax2 = rows.idxmax()
        else:
            return 2, idxmin, alist

    # 戻り高値判定
        if (max2 / max_val >= p['retracement_ratio'][0]) and (max2 / max_val <= p['retracement_ratio'][1]):
            alist.append([idxmax2, df0.loc[idxmax2,"High"]])
        else:
            return 2, idxmin, alist

    #④戻り高値と以降の2番底を探す
    #　最高値日と最安値日の中間日以前
        days_div = abs(int(((idxmin - idxmax).days) * p['bottom2_search_days_ratio']))
        df2  = df1[idxmax2 + dt.timedelta(days=days_div) : self.today]
#       df2  = df1[idxmax2 : self.today]

        if len(df2.index) > 0:
            rows    = df2['Low']
            min2    = rows.min()
            idxmin2 = rows.idxmin()
        else:
            return 3, idxmax2, alist

    # 二番底判定
        if (min_val / min2 >= p['bottom_similarity_ratio'][0]) and (min_val / min2 <= p['bottom_similarity_ratio'][1]):
            alist.append([idxmin2, df0.loc[idxmin2,"Low"]])
        else:
            return 3, idxmin2, alist

    #⑤ピボット判定
        pivot_p = max2 * p['pivot_ratio']
        df2 = df0.query('index > @idxmin2 & High >= @pivot_p')

    # STEP5判定
        if len(df2.index) > 0:
            pivot_dt1 = df2.index[0]
            alist.append([pivot_dt1, df0.loc[pivot_dt1,"High"]])
        else:
            return 4, idxmax2, alist

    #⑥ピボットBreakout判定
        df2 = df0.query('index >= @pivot_dt1 & High >= @max2')

    # STEP6判定
        if len(df2.index) > 0:
            pivot_dt2 = df2.index[0]
            alist.append([pivot_dt2, df0.loc[pivot_dt2,"High"]])
            return 6, pivot_dt2, alist
        else:
            return 5, pivot_dt1, alist

#---------------------------------------#
# カップウィズハンドル判定処理 (HELPER METHODS)
#---------------------------------------#
    def _cwh_check_prior_uptrend(self, df, left_lip_date):
        """ Checks if there was a significant uptrend prior to the cup's formation. """
        p = self.params['cup_with_handle']
        uptrend_lookback_days = p['uptrend_lookback_days']
        uptrend_min_rise_factor = p['uptrend_min_rise_factor']

        uptrend_start_date = left_lip_date - dt.timedelta(days=uptrend_lookback_days)
        uptrend_df = df.loc[uptrend_start_date:left_lip_date]

        if uptrend_df.empty:
            return False, "Not enough data for uptrend check"

        start_price = uptrend_df['Close'].iloc[0]
        end_price = df.loc[left_lip_date, 'High']

        if end_price >= start_price * uptrend_min_rise_factor:
            return True, "Prior uptrend confirmed"
        else:
            return False, f"Price did not rise enough in the {uptrend_lookback_days} days prior to the cup"

    def _cwh_find_cup_shape(self, df):
        """ Identifies a valid cup shape based on a high on the left, a bottom, and a high on the right. """
        p = self.params['cup_with_handle']
        cup_min_duration_days = p['cup_min_duration_days']
        cup_max_duration_days = p['cup_max_duration_days']
        cup_min_depth_factor = p['cup_min_depth_factor']
        cup_lip_max_deviation = p['cup_lip_max_deviation']
        cup_lip_min_deviation = p['cup_lip_min_deviation']
        cup_min_rounded_points = p['cup_min_rounded_points']

        if len(df) < cup_min_duration_days:
            return None, None, None, None, "Not enough historical data to form a cup"

        # Find the high point (left lip) in the first 75% of the lookback period
        left_side_df = df.iloc[:int(len(df) * 0.75)]
        left_lip_date = left_side_df['High'].idxmax()
        left_lip_price = left_side_df['High'].max()

        # The cup bottom must occur after the left lip, within a reasonable timeframe
        cup_search_end_date = left_lip_date + dt.timedelta(days=cup_max_duration_days)
        cup_df = df.loc[left_lip_date:cup_search_end_date]
        if len(cup_df) < cup_min_duration_days:
            return None, None, None, None, "Not enough data after left lip to form a cup"

        cup_bottom_date = cup_df['Low'].idxmin()
        cup_bottom_price = cup_df['Low'].min()

        # Check cup depth
        if not left_lip_price >= cup_bottom_price * cup_min_depth_factor:
            return None, None, None, None, f"Cup is not deep enough. Depth must be >{cup_min_depth_factor}x"

        # Check cup duration
        cup_duration = (cup_bottom_date - left_lip_date).days
        if not (cup_min_duration_days <= cup_duration <= cup_max_duration_days):
            return None, None, None, None, f"Cup duration ({cup_duration} days) is out of range"

        # Find the right lip of the cup
        right_side_df = df.loc[cup_bottom_date:]
        if right_side_df.empty:
            return None, None, None, None, "No data available to form the right side of the cup"

        # The right lip should be close in price to the left lip
        price_match_upper = left_lip_price * cup_lip_max_deviation
        price_match_lower = left_lip_price * cup_lip_min_deviation

        potential_right_lips = right_side_df[right_side_df['High'].between(price_match_lower, price_match_upper)]
        if potential_right_lips.empty:
            return None, None, None, None, "Could not find a matching right lip for the cup"

        right_lip_date = potential_right_lips.index[0]
        right_lip_price = potential_right_lips['High'].iloc[0]

        # Verify a "U" shape by checking that the bottom is not too sharp
        cup_period_df = df.loc[left_lip_date:right_lip_date]
        low_points_count = cup_period_df[cup_period_df['Low'] < cup_bottom_price * 1.1].shape[0]
        if low_points_count < cup_min_rounded_points:
            return None, None, None, None, f"Cup bottom is too sharp (V-shaped), not enough rounding ({low_points_count} points)"

        return left_lip_date, cup_bottom_date, cup_bottom_price, right_lip_date, None

    def _cwh_check_handle_formation(self, df, right_lip_date, cup_high_price, cup_bottom_price):
        """ Checks for the handle formation after the right lip of the cup. """
        p = self.params['cup_with_handle']
        handle_max_duration_days = p['handle_max_duration_days']
        handle_min_duration_days = p['handle_min_duration_days']

        handle_start_date = right_lip_date
        handle_lookahead_end_date = handle_start_date + dt.timedelta(days=handle_max_duration_days)
        handle_df = df.loc[handle_start_date:handle_lookahead_end_date]

        if handle_df.empty or len(handle_df) < handle_min_duration_days:
            return None, None, "Not enough data to form a handle"

        # Handle should be a shallow pullback from the right lip's high
        pullback_df = handle_df[handle_df['Low'] < cup_high_price]
        if pullback_df.empty:
            # If no pullback, it might be breaking out directly. Pivot is the cup high.
            return right_lip_date, cup_high_price, "No classic handle pullback found; watching for breakout from lip"

        handle_low_date = pullback_df['Low'].idxmin()
        handle_duration = (handle_low_date - right_lip_date).days

        if not (handle_min_duration_days <= handle_duration <= handle_max_duration_days):
            return None, None, f"Handle duration ({handle_duration} days) is out of range"

        # The handle's low should not be too deep.
        # The pullback is not allowed to be more than 1/3rd of the cup's depth.
        handle_low_price = pullback_df['Low'].min()
        cup_depth = cup_high_price - cup_bottom_price
        min_handle_low_price = cup_high_price - (cup_depth / 3)

        if handle_low_price < min_handle_low_price:
            return None, None, f"Handle pullback is too deep. Low: {handle_low_price:.2f}, Min Allowable: {min_handle_low_price:.2f}"

        # Final check: Ensure the pattern hasn't broken down. The latest close must be above the handle's low.
        last_close = df['Close'].iloc[-1]
        if last_close < handle_low_price:
            return None, None, f"Pattern invalidated. Current price ({last_close:.2f}) is below handle low ({handle_low_price:.2f})"

        # The pivot point for the breakout is the high of the right lip
        pivot_price = cup_high_price
        return handle_low_date, pivot_price, None

    def _cwh_check_pivot_breakout(self, df, handle_low_date, pivot_price):
        """ Checks for a breakout above the pivot point with high volume. """
        p = self.params['cup_with_handle']
        pivot_lookahead_days = p['pivot_lookahead_days']
        volume_breakout_factor = p['volume_breakout_factor']

        breakout_lookahead_end_date = handle_low_date + dt.timedelta(days=pivot_lookahead_days)

        # Look for the first day price crossed the pivot
        pivot_df = df.query('index > @handle_low_date and index <= @breakout_lookahead_end_date and High >= @pivot_price')

        if pivot_df.empty:
            return False, "NO_BREAKOUT"

        breakout_date = pivot_df.index[0]
        breakout_day = pivot_df.iloc[0]
        one_month_ago = self.today - dt.timedelta(days=30)

        # Check for volume on the breakout day
        volume_ok = False
        if breakout_day.name in df.index:
            # Use MA_VOL which is pre-calculated
            mean_volume_50d = df.loc[breakout_day.name, 'MA_VOL']
            if pd.notna(mean_volume_50d) and breakout_day['Volume'] > mean_volume_50d * volume_breakout_factor:
                volume_ok = True

        # Evaluate based on volume and date
        if volume_ok:
            # High-volume breakout: success, unless it's old
            if breakout_date < one_month_ago:
                return False, f"OLD_BREAKOUT: Breakout on {breakout_date.date()} is older than 1 month"
            return True, f"Pattern detected with volume breakout on {breakout_date.date()}"
        else:
            # Low-volume crossing: potential WATCH, unless it's old
            if breakout_date < one_month_ago:
                return False, f"STALE_WATCH: Low-volume pivot cross on {breakout_date.date()} is older than 1 month"
            return False, "Pivot breakout occurred but without sufficient volume"

#---------------------------------------#
# カップウィズハンドル判定処理 (リファクタリング版)
#---------------------------------------#
    def Cup_with_Handle_Check(self):
        df = self.df.sort_index()
        if df.empty:
            return 0, self.today, []

        # Check for valid volume data. If not present, the pattern cannot be confirmed.
        if 'Volume' not in df.columns or df['Volume'].isnull().all() or (df['Volume'] == 0).all():
            dummy_dt = df.index[-1] if not df.empty else self.today
            return 0, dummy_dt, []

        p = self.params['cup_with_handle']
        dummy_dt = df.index[-1] # Use last valid date as the default
        alist = []

        # Stage 1: Find a valid cup shape (left lip, bottom, right lip).
        left_lip_date, cup_bottom_date, cup_bottom_price, right_lip_date, err = self._cwh_find_cup_shape(df)
        if err:
            # For simplicity, returning 0 for all initial failures.
            # A more granular return code could be implemented later if needed.
            return 0, dummy_dt, alist

        # Stage 2: Check for a prior uptrend before the cup.
        is_uptrend, reason = self._cwh_check_prior_uptrend(df, left_lip_date)
        if not is_uptrend:
            return 1, left_lip_date, alist

        # The pivot point is the high of the right lip (the start of the handle).
        cup_high_price = df.loc[right_lip_date, 'High']

        # Stage 3: Check for the handle formation.
        handle_low_date, returned_pivot, err = self._cwh_check_handle_formation(df, right_lip_date, cup_high_price, cup_bottom_price)

        # The pivot price for a CWH is ALWAYS the high of the cup.
        pivot_price = cup_high_price
        if pivot_price is None:
            return 2, right_lip_date, alist # Should not happen if cup shape is found

        # Check for disqualifying errors from the handle formation.
        if err and "No classic handle" not in err:
            return 3, right_lip_date, alist

        handle_low_price = None
        if err and "No classic handle" in err:
            # If no handle, the breakout check should start from the right lip
            handle_low_date = right_lip_date
        else: # A valid handle was found
            handle_low_price = df.loc[handle_low_date, 'Low']

        # Prepare data for charting (alist).
        alist.append((left_lip_date, df.loc[left_lip_date, 'High']))
        alist.append((cup_bottom_date, cup_bottom_price))
        alist.append((right_lip_date, df.loc[right_lip_date, 'High']))
        if handle_low_price is not None:
            alist.append((handle_low_date, handle_low_price))

        # Stage 4: Look for a pivot breakout.
        is_breakout, breakout_reason = self._cwh_check_pivot_breakout(df, handle_low_date, pivot_price)

        # Map string results to integer status codes
        if is_breakout:
            # Successful breakout with volume
            breakout_date = df.query('index > @handle_low_date and High >= @pivot_price').index[0]
            alist.append((breakout_date, df.loc[breakout_date, 'High']))
            return 6, breakout_date, alist

        if "OLD_BREAKOUT" in breakout_reason or "STALE_WATCH" in breakout_reason:
            # Breakout is too old to be actionable
            return 4, right_lip_date, alist

        if "without sufficient volume" in breakout_reason:
            # Awaiting volume confirmation
            return 5, df.index[-1], alist

        # Awaiting breakout from handle or lip
        return 5, df.index[-1], alist

#---------------------------------------#
# フラットベース判定処理
#---------------------------------------#
    def FlatBase_Check(self):

    # Dataframeを参照渡し
        df0 = self.df
        if df0.empty:
            return 0, self.today, []

        p = self.params['flat_base']
        breakout_vol_mult = p.get('breakout_volume_multiplier', 1.5)

    # 補助線描画用リスト
        alist= []

    # ダミー用戻り値
        dummy_dt = df0.index[-1]

    #①ベースの開始
    #　期間の最安値日を取得
        rows = df0['Low']
        if len(df0.index) > 0:
            min_val = rows.min()
            idxmin = rows.idxmin()
#           alist.append((idxmin, df0.loc[idxmin,"Low"]))
        else:
            return 0, dummy_dt, alist

    #②ベースの頂点
    #　期間の最安値日以降、直近の最高値が最安値の1.2倍以上
        df1 = df0.loc[idxmin:]
        if len(df1) > p['peak_search_days_ago']:
            df1 = df1.iloc[:-p['peak_search_days_ago']]
        else:
            return 1, dummy_dt, alist # データ不足

        if len(df1.index) > 0:
            rows = df1['High']
            max_val = rows.max()
            idxmax = rows.idxmax()
            alist.append((idxmax, df0.loc[idxmax,"High"]))
        else:
            return 1, dummy_dt, alist

    # STEP2判定
        if max_val > min_val * p['base_min_rise_ratio']:
            pass
        else:
            return 1, idxmin, alist

    #③ベースの形成
    #　最高値から5～15%下落
        df1 = df0[idxmax : self.today]

    # ベース価格のレンジ
        base_p1 = max_val * p['base_depth'][0]
        base_p2 = max_val * p['base_depth'][1]

        df2 = df1.query('@base_p1 <= Close <= @base_p2')

    # STEP3判定
        if len(df2.index) > 0:
            base_sdt = df2.index[0]                # ベース開始日
            base_edt = df2.index[-1]               # ベース終了日
            base_len = len(df0.loc[idxmax:base_edt]) # ベース構成日数 (取引日数)

            # ベースの最安値、最高値、最安日を取得
            df1_base = df0[base_sdt : base_edt]
            base_min = df1_base['Close'].min()
            base_max = df1_base['Close'].max()
            base_bdt = df1_base['Close'].idxmin()

            # ベース構成日数(最高値日から約4～8週間)と最安値が高値-15%を下回らない
            base_duration_days_min = p['base_duration_weeks'][0] * 5
            base_duration_days_max = p['base_duration_weeks'][1] * 5
            if (base_len >= base_duration_days_min) and (base_len <= base_duration_days_max) and (base_min >= base_p1) and (base_max <= base_p2):
                alist.append((base_sdt, df0.loc[base_sdt,"Close"])) # ベースの開始
                alist.append((base_bdt, df0.loc[base_bdt,"Low"]))   # ベースの最安
                alist.append((base_edt, df0.loc[base_edt,"Close"])) # ベースの終了
            else:
                return 2, idxmax, alist
        else:
            return 2, idxmax, alist

    #④ピボット判定 (出来高条件を追加)
    #　直近価格がピボットポイントを超え、かつ出来高が急増
        df2 = df0.query('@base_edt < index & High >= @max_val & Volume > MA_VOL * @breakout_vol_mult')

    # STEP4判定
        if len(df2.index) > 0:
            pvt_dt = df2.index[0]
            alist.append((pvt_dt, df0.loc[pvt_dt,"High"]))
            return 4, pvt_dt, alist
        else:
            return 3, base_edt, alist

#---------------------------------------#
# O'Neil/Minervini流チャート判定
#---------------------------------------#
    def ON_Minervini_Check(self):
        # 定数の設定
        p = self.params['on_minervini']
        base_weeks_min = p['base_weeks_min']
        base_weeks_max = p['base_weeks_max']
        multiplier_min = p['volatility_multiplier_min']
        multiplier_max = p['volatility_multiplier_max']
        vol_reduction  = p['volume_reduction_threshold']

        # Dataframeを複製
        df0 = self.df.copy()

        # 補助線描画用リスト
        alist = []

        # ベース期間を日付に変換
        base_length_min = dt.timedelta(weeks=base_weeks_min)
        base_length_max = dt.timedelta(weeks=base_weeks_max)

        # 直近の高値の日付を取得
        try:
            recent_max_date = df0['Close'].idxmax()
        except:
            return 0, None, alist

        # 直近の高値の日付が範囲外の場合は終了
        base_duration = df0.index[-1] - recent_max_date
        if base_length_min <= base_duration <= base_length_max:
            return 0, None, alist

        # 直近の高値の日付以降のデータに絞る
        df0 = df0.loc[recent_max_date:]

        # ボラティリティ調整による動的な価格下落を検出
        price_volatility = df0['Close'].pct_change().std()
        dynamic_drop_min = price_volatility * multiplier_min
        dynamic_drop_max = price_volatility * multiplier_max

        # 直近高値のローリング
        recent_max = df0['Close'].rolling(window=self.ma_mid).max()
#       print(f"Price Volatility: {price_volatility}")
#       print(f"Dynamic Drop Min: {dynamic_drop_min}")
#       print(f"Dynamic Drop Max: {dynamic_drop_max}")

        # 動的しきい値によるベースマスク
        base_mask = (
            (df0['Close'] <= recent_max * (1 - dynamic_drop_min)) &
            (df0['Close'] >= recent_max * (1 - dynamic_drop_max))
        )
        base_periods = df0[base_mask]

#       print(f"Base Periods Count: {len(base_periods)}")
        if not base_periods.empty:
            base_start_date = base_periods.index[0]
            base_end_date   = base_periods.index[-1]

            # ベース期間内の最高値
            recent_max_date = df0.loc[base_start_date:base_end_date, 'Close'].idxmax()

            # 最高値の位置を検証
            if not (base_start_date <= recent_max_date <= base_end_date):
                return 0, None, alist

            # ベース期間を評価
            base_duration = base_end_date - recent_max_date
            if not (base_length_min <= base_duration <= base_length_max):
                return 0, None, alist

            # ベース期間の最安値
            base_min_date  = df0.loc[recent_max_date:base_end_date, 'Close'].idxmin()
            base_min_value = df0.loc[base_min_date, "Close"]

            # 出来高分析
            # 直近の出来高平均と過去の出来高平均を比較
            recent_volume   = df0['Volume'].loc[recent_max_date:base_end_date].rolling(window=self.ma_short).mean()
            previous_volume = df0['Volume'].loc[:recent_max_date].rolling(window=self.ma_mid).mean().iloc[-1]

            # 直近の出来高減少
            volume_reduction_ratio = (previous_volume - recent_volume.mean()) / previous_volume

            # トレンド分析の改善
            long_term_ma = df0['Close'].rolling(window=self.ma_long).mean()
            trend_slope = long_term_ma.diff()

            # 状況の総合的な確認
            condition_checks = [
                volume_reduction_ratio > vol_reduction,        # 出来高が減少
                trend_slope.iloc[-1] > 0,                      # 200日移動平均線の傾きがプラス
                df0['Close'].iloc[-1] > long_term_ma.iloc[-1]  # 現在の株価が200日移動平均線を上回っている
            ]

            # 条件を満たす場合の処理
            if all(condition_checks):
                # 補助線描画用リストに追加
                alist.append((recent_max_date, df0.loc[recent_max_date, "Close"]))  # ベースの開始
                alist.append((base_min_date, base_min_value))                       # ベースの最安値
                alist.append((base_end_date, df0.loc[base_end_date, "Close"]))      # ベースの終了

                return 1, base_end_date, alist

        # 条件に合わない場合は0を返す
        return 0, None, alist

#------------------------------------------------#
# U/Dレシオ計算処理
#------------------------------------------------#
    def calcUDRatio(self, df0):
    # 変数の初期化
        up_vol   = 0.0
        down_vol = 0.0
        ud_ratio = 0.00

    # 直近の50件に絞り込む
        df1 = df0.tail(50)

    # DataFrame内をループ
        for index, data in df1.iterrows():
            # 上昇/下落の判定(Open:data[0], Close:data[3], Volume:data[5])
            if (data['Close'] - data['Open']) >= 0:
                up_vol   += data['Volume']   # 上昇
            else:
                down_vol += data['Volume']   # 下落

    # U/Dレシオの算出
        if down_vol == 0.0:
            ud_ratio = 9.99
        else:
            ud_ratio = up_vol / down_vol

        return round(ud_ratio,2)

#---------------------------------------#
# CSVを読取りDataframeに格納
#---------------------------------------#
    def csvSetDF(self, doc):

        # CSVを読取
        df = pd.read_csv(doc, index_col='Date', parse_dates=True, on_bad_lines='skip')

        # ティッカーの処理
        self.strBaseName = os.path.splitext(os.path.basename(doc))[0]
        if (self.strBaseName[-2:] == "-X"):
            self.strTicker = self.strBaseName[:-2]
        else:
            self.strTicker = self.strBaseName

        self.setDF(df, self.strTicker)

        return

#---------------------------------------#
# DataFrameを直接セットし、指標を計算
#---------------------------------------#
    def setDF(self, df, ticker_str):
        df = df.dropna(how='all')                       # 欠損値を除外
        # インデックスを強制的にDatetimeIndexに変換し、タイムゾーンをUTCに統一
        df.index = pd.to_datetime(df.index, utc=True)

        # 移動平均を計算
        df['MA10']   = df['Close'].rolling(self.ma_short).mean()
        df['MA50']   = df['Close'].rolling(self.ma_mid).mean()
        df['MA150']  = df['Close'].rolling(self.ma_s_long).mean()
        df['MA200']  = df['Close'].rolling(self.ma_long).mean()
        df['DIFF']   = df['MA200'].pct_change(20, fill_method=None)
        df['MA_VOL'] = df['Volume'].rolling(self.ma_mid).mean()

        # ATR (Average True Range) を計算 (期間:14)
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.ewm(span=14, adjust=False).mean()

        # インスタンス変数にセット
        self.df = df
        self.strTicker = ticker_str
        self.strBaseName = ticker_str # BaseName might not be relevant anymore

        # タイムゾーンが指定されていない場合、ティッカーから推測して設定
        if self.display_tz is None:
            if '.T' in self.strTicker:
                self.display_tz = pytz.timezone('Asia/Tokyo')
            else:
                self.display_tz = pytz.timezone('America/New_York')

        return

#------------------------------------------------#
# CSVファイル書込み・チャート作成処理
#------------------------------------------------#
    def writeFlles(self, res, strLabel):

        # メッセージ出力
        print(self.strTicker + " is ::: " + strLabel + " :::")

        # STAGE 2: ファンダメンタル・スクリーニング
        # self.ern_infoがNoneの場合（isTrend.pyからの呼び出しなど）、チェックをスキップ
        if self.ern_info is not None:
            try:
                info = self.ern_info.ticker.info
                roe = info.get('returnOnEquity')
                passed, _ = self.ern_info.get_fundamental_screening_results(roe)

                if not passed:
                    # print(f"##INFO## {self.strTicker} did not pass fundamental screening. Skipping chart/CSV output.")
                    return # 条件を満たさない場合は後続処理を行わない

                print(f"{self.strTicker} is ::: fundamentaly OK :::")

            except Exception as e:
                # print(f"##ERROR## during fundamental screening for {self.strTicker}: {e}")
                return # エラーが発生した場合も後続処理をスキップ

        # ローソク足チャートを作成

        # 補助線リストを取得
        alist = []
        if len(res) == 3 and res[2]:
            alist = sorted(res[2], key=lambda x: (x[0]))

        # チャート出力範囲
        df0 = self.df                        # Dataframeを参照渡し
        df0 = df0.tail(260)                  # データを末尾から行数で絞り込み
        df0 = df0.sort_index()               # 日付で昇順ソート
        df0.loc[res[1],'Signal'] = df0.loc[res[1],'Low'] * 0.97 # マーカー表示用の列に値をセット(安値-3%の位置に表示)
#       print(df0.loc[res[1],'Signal'])

        # UDレシオの計算(10レコードの推移)
        ud_ratio1 = self.calcUDRatio(df0.head(-10))
        ud_ratio2 = self.calcUDRatio(df0)

        if (ud_ratio1 <= ud_ratio2) and (ud_ratio2 >= 1):
            if ud_ratio1 < 1:
                ud_mark = "*"
            else:
                ud_mark = "O"
        elif (ud_ratio2 >= 0.9) and (ud_ratio1 <= ud_ratio2):
            ud_mark = "/"
        else:
            ud_mark = "X"

        ud_val = str(ud_ratio1) + " => "+ str(ud_ratio2)
        # print('U/D Ratio:{0} ::: {1}'.format(ud_val, ud_mark))

        # ud_markが'*','O','/'の場合、チャート出力
        if ud_mark in ["*","O","/"]:

            # yfinanceから取得したTimestampはUTCだが、日付部分は取引日を指している。
            # ローカルタイムゾーンに変換すると日付がずれる可能性があるため、UTCのまま日付を抽出する。
            date_str = str(res[1].date())

            # ディレクトリが存在しない場合、ディレクトリを作成
            if self.base_dir.endswith('-'):
                # isTrend.pyから "./output_US/Trend-" のようなプレフィックスで呼ばれた場合
                Out_DIR = self.base_dir + date_str
            else:
                # chkData.pyから "./output_US/" のようなディレクトリで呼ばれた場合
                Out_DIR = os.path.join(self.base_dir, date_str)

            if not os.path.exists(Out_DIR):
#               os.makedirs(Out_DIR)
                i = 0
                for i in range(3):
                    try:
                        os.makedirs(Out_DIR)
                    except Exception:
                        print("\r##ERROR##: Retry=%s" % (str(i)), end="\n", flush=True)
                        # 5秒スリープしてリトライ
                        time.sleep(5)
                    else:
                        # 例外が発生しなかった場合に実行するコード
                        break  # ループを抜ける

            # チャート出力
            info = self.chart.makeChart(Out_DIR, df0, self.strTicker, self.strBaseName, strLabel, ud_val + ' ::: ' + ud_mark , alist, ern_info=self.ern_info)

            # CSVファイルの書き込み
            if info != ["-","-","-","-","-"]:  # infoがデフォルト値（全部"-"）でなければCSV出力
                outTxt = date_str + "," + strLabel + ",\"" + self.strTicker + "\",\"" + info[1] + "\",\"" + info[2] + "\"," + info[4] + "," + str(ud_ratio2) + "," + str(ud_ratio1) + ",\"" + ud_mark + "\",\"" + info[3] + "\",\"" + str(round(df0['Close'].iloc[-1], 2)) + "\"\n"
                print("  Name   : " + info[1])
                print("  Sector : " + info[2])
                print("  UDVR   : " + ud_val + "  " + ud_mark)
                self.w.write(outTxt)
                self.w.flush()

        return

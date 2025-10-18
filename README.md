# 相対強度とチャートパターンに基づく株式スクリーニングエンジン

## 概要

このプロジェクトは、米国および日本市場における潜在的な取引機会を特定するために設計された、包括的な株式スクリーニングおよび分析エンジンです。IBDやマーク・ミネルヴィニによって広められた相対強度（RS）の概念と、古典的なテクニカルチャートパターンの自動検出を組み合わせて活用します。

このエンジンは、体系的に株式をフィルタリングし、そのモメンタムを計算し、強力な上昇トレンドを特定し、特定の買いシグナルパターンを検出し、有望な候補のチャートとシグナルリストを生成することを目的としています。

## 主な機能

- **相対強度（RS）計算**: IBDが提唱する相対強度レーティングを実装し、各株式のパフォーマンスを市場全体と比較します。
- **テクニカルパターン認識**: VCP、カップウィズハンドル、ダブルボトムなど、さまざまな強気のチャートパターンを自動的にスクリーニングします。
- **ファンダメンタルズ・スクリーニング**: テクニカル分析の前に、基本的なファンダメンタルズチェックを実行します。
- **自動チャート作成**: 有効な買いシグナルごとに詳細な株価チャートを生成・保存します。
- **日米市場のサポート**: 米国と日本の両市場を分析するためのスクリプトが含まれています。

## セットアップと手動修正ガイド

**警告: このリポジトリのスクリプトは、現状のままでは実行できません。** 動作させるには、以下の手順に従って手動でのコード修正が必須となります。

### ステップ1: 依存関係のインストール

まず、プロジェクトに必要なPythonライブラリをインストールします。

```bash
pip install -r requirements.txt
```

主なライブラリは以下の通りです:
`pandas`, `numpy`, `yfinance`, `requests`, `pytz`, `beautifulsoup4`, `matplotlib`, `japanize-matplotlib`, `mplfinance`, `ta`, `openpyxl`

### ステップ2: シェルスクリプトの修正

各シェルスクリプト（`.sh`ファイル）には、開発者のローカル環境に依存したパスが含まれており、実行前に修正が必要です。

#### 修正が必要な点
1.  **`cd`コマンドの削除**: 特定のディレクトリへ移動する `cd '...'` という行を削除します。
2.  **絶対パスの相対パスへの変更**: `/content/_files/...` のような絶対パスを、プロジェクトのルートディレクトリからの相対パス（例: `_files/...`）に修正します。
3.  **Pythonスクリプト呼び出しの修正**: `python $SCRIPT_DIR/script.py` という形式のコマンドから、存在しないディレクトリを指す `$SCRIPT_DIR/` の部分を削除し、`python script.py` の形式に修正します。

---

#### ファイル別 修正手順

<details>
<summary><b>1. `US_Daily.sh` の修正</b></summary>

- **削除する行:**
  ```diff
  - cd '/content/drive/MyDrive/Screening/'
  ```
- **修正する変数:**
  ```diff
  - STOCK_DIR1=/content/_files/US/
  - STOCK_DIR2=/content/_files/US-INDEX/
  - SCREEN_DATA1=/content/_files/US/input.txt
  + STOCK_DIR1=_files/US/
  + STOCK_DIR2=_files/US-INDEX/
  + SCREEN_DATA1=_files/US/input.txt

  - SCRIPT_DIR=$BASE_DIR/_scripts
  + # SCRIPT_DIRの行は不要なため削除またはコメントアウトします
  ```
- **修正するコマンド:**
  ```diff
  - python $SCRIPT_DIR/getList_US.py ...
  - python $SCRIPT_DIR/chkData.py ...
  - python $SCRIPT_DIR/isTrend.py ...
  + python getList_US.py ...
  + python chkData.py ...
  + python isTrend.py ...
  ```
</details>

<details>
<summary><b>2. `JP_Daily.sh` の修正</b></summary>

- **削除する行:**
  ```diff
  - cd '/content/drive/MyDrive/Screening/'
  ```
- **修正する変数:**
  ```diff
  - STOCK_DIR=/content/_files/JP/
  - SCREEN_DATA0=/content/_files/JP/data_j.xls
  - SCREEN_DATA1=/content/_files/JP/input.txt
  + STOCK_DIR=_files/JP/
  + SCREEN_DATA0=_files/JP/data_j.xls
  + SCREEN_DATA1=_files/JP/input.txt

  - SCRIPT_DIR=$BASE_DIR/_scripts
  + # SCRIPT_DIRの行は不要なため削除またはコメントアウトします
  ```
- **修正するコマンド:**
  ```diff
  - python $SCRIPT_DIR/getList_JP.py ...
  - python $SCRIPT_DIR/chkData.py ...
  + python getList_JP.py ...
  + python chkData.py ...
  ```
</details>

<details>
<summary><b>3. `US_Weekly.sh` の修正</b></summary>

- **修正する変数:**
  ```diff
  - STOCK_DIR=/content/_files/US/
  - SCREEN_DATA1=/content/_files/US/input.txt
  + STOCK_DIR=_files/US/
  + SCREEN_DATA1=_files/US/input.txt

  - SCRIPT_DIR=$BASE_DIR/_scripts
  + # SCRIPT_DIRの行は不要なため削除またはコメントアウトします
  ```
- **修正するコマンド:**
  ```diff
  - python $SCRIPT_DIR/getList_US.py ...
  - python $SCRIPT_DIR/chkData.py ...
  - python $SCRIPT_DIR/isTrend.py ...
  + python getList_US.py ...
  + python chkData.py ...
  + python isTrend.py ...
  ```
</details>

<details>
<summary><b>4. `JP_Weekly.sh` の修正</b></summary>

- **削除する行:**
  ```diff
  - cd '/content/drive/My Drive/Screening/'
  ```
- **修正する変数:**
  ```diff
  - STOCK_DIR=/content/_files/JP/
  - SCREEN_DATA0=/content/_files/JP/data_j.xls
  - SCREEN_DATA1=/content/_files/JP/input.txt
  + STOCK_DIR=_files/JP/
  + SCREEN_DATA0=_files/JP/data_j.xls
  + SCREEN_DATA1=_files/JP/input.txt

  - SCRIPT_DIR=$BASE_DIR/_scripts
  + # SCRIPT_DIRの行は不要なため削除またはコメントアウトします
  ```
- **修正するコマンド:**
  ```diff
  - python $SCRIPT_DIR/getList_JP.py ...
  - python $SCRIPT_DIR/chkData.py ...
  - python $SCRIPT_DIR/isTrend.py ...
  + python getList_JP.py ...
  + python chkData.py ...
  + python isTrend.py ...
  ```
</details>

<details>
<summary><b>5. `getRS_Rating.sh` の修正</b></summary>

- **修正する変数:**
  ```diff
  - SCRIPT_DIR=$BASE_DIR/_scripts
  + # SCRIPT_DIRの行は不要なため削除またはコメントアウトします
  ```
- **修正するコマンド:**
  `$SCRIPT_DIR/` の部分をすべての `python` コマンドから削除してください。
</details>

<details>
<summary><b>6. `getMarketCondition.sh` の修正 (任意)</b></summary>
このスクリプトは動作しますが、一貫性のために修正を推奨します。
- **修正するコマンド:**
  ```diff
  - python $SCRIPT_DIR/getMarketCondition.py ...
  + python getMarketCondition.py ...
  ```
</details>

---

## 使い方 (スクリプト修正後)

スクリプトの修正が完了したら、以下の様にしてエンジンを実行できます。

#### ステージ1: 相対強度（RS）データの生成
まず、RSレーティングを計算するためのデータを生成します。
```bash
bash getRS_Rating.sh
```

#### ステージ2: 日次・週次スクリーニングの実行
RSデータが準備できたら、日次または週次のスクリーニングを実行して取引候補を特定します。

- **米国市場（日次）:**
  ```bash
  bash US_Daily.sh
  ```
- **日本市場（週次）:**
  ```bash
  bash JP_Weekly.sh
  ```
  （他のスクリプトも同様に実行可能です）

## プロジェクト構造

```
.
├── US_Daily.sh, JP_Daily.sh, etc.  # メイン実行スクリプト
├── getList_US.py, chkData.py, etc. # コアロジックのPythonスクリプト
├── _files/                           # データファイル
│   ├── RS/                           # RS関連の入出力
│   └── indexes/                      # インデックスリスト
├── output_JP/, output_US/          # 出力ディレクトリ（スクリプト実行時に生成）
└── requirements.txt                  # 依存ライブラリ
```

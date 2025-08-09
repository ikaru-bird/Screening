#!/bin/bash

set -u

SYMBOL_JP=^N225
SYMBOL_US=^GSPC

# 株式市場の投資環境を評価
python ./_scripts/getMarketCondition.py $SYMBOL_JP
python ./_scripts/getMarketCondition.py $SYMBOL_US


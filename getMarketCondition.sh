#!/bin/bash

set -u

SYMBOL_JP=^N225
SYMBOL_US=^GSPC
SCRIPT_DIR=.

# 株式市場の投資環境を評価
python $SCRIPT_DIR/getMarketCondition.py $SYMBOL_JP
python $SCRIPT_DIR/getMarketCondition.py $SYMBOL_US

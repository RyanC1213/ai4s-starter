# -*- coding: utf-8 -*-
"""读取数据、做体检、导出清洗表。

用法:
    python src/read_data.py

Day 4 的任务：把下面 TODO 里的清洗规则换成你自己数据的规则。
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "demo_data.csv"
OUT = ROOT / "data" / "demo_clean.csv"

df = pd.read_csv(SRC)

print("-" * 54)
print("shape      :", df.shape, "  (rows, cols)")
print("columns    :", list(df.columns))
print("-" * 54)
print("dtypes:\n{}".format(df.dtypes))
print("-" * 54)
print("missing per column:\n{}".format(df.isna().sum()))
print("-" * 54)
print(df.head(5).to_string(index=False))
print("-" * 54)

# ---- TODO (Day 4): 换成你自己的清洗规则 -------------------------
# 1. 删掉标签缺失的行
# df = df.dropna(subset=["yield_pct"])
#
# 2. 删掉物理上不合理的值（产率不可能 >100）
# df = df[df["yield_pct"].between(0, 100)]
#
# 3. 去掉重复实验（同一催化剂重复测的取平均）
# df = df.groupby("cat_id", as_index=False).mean(numeric_only=True)
#
# 每次修改都在这里写一行注释说明「删了多少、为什么删」。
# 面试官问的第一个问题就是：你删了哪些数据？
# -----------------------------------------------------------------

TAG = "yield_pct"
dropped = 0
if TAG in df.columns:
    before = len(df)
    df = df.dropna(subset=[TAG])
    dropped = before - len(df)
    print("dropped rows without target: {}".format(dropped))
    if dropped > 0:
        print("  -> 这 {} 行必须在报告里说明原因".format(dropped))

df.to_csv(OUT, index=False, encoding="utf-8-sig")
print("saved -> {}".format(OUT))

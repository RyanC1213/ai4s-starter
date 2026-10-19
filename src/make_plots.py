# -*- coding: utf-8 -*-
"""画三张图并存到 figures/。

用法:
    python src/make_plots.py

Day 5 的任务：把 x / y 换成你关心的变量，并给每张图补上单位。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 无界面环境下也能出图

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# 中文标签不乱码（Windows 用 SimHei / 微软雅黑）
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(ROOT / "data" / "demo_clean.csv")


# 1. 散点：自变量 vs 产率
fig, ax = plt.subplots(figsize=(5.2, 4.0))
ax.scatter(df["pd_loading_wt"], df["yield_pct"], s=32, alpha=0.85, edgecolors="white", linewidths=0.6)
ax.set_xlabel("Pd loading (wt%)")
ax.set_ylabel("Yield (%)")
ax.set_title("Yield vs Pd loading")
fig.savefig(FIG / "fig1_scatter.png", dpi=300, bbox_inches="tight")
plt.close(fig)


# 2. 柱状 + 误差棒：按分组比较均值
fig, ax = plt.subplots(figsize=(5.2, 4.0))
df["size_bin"] = pd.cut(df["particle_size_nm"], bins=[0, 2, 3, 5], labels=["<2", "2-3", "3-5"])
g = df.groupby("size_bin", observed=True)["yield_pct"]
means, stds = g.mean(), g.std().fillna(0)
ax.bar(means.index.astype(str), means.values, yerr=stds.values, capsize=4, color="#2f6db5", alpha=0.85)
ax.set_xlabel("Particle size (nm)")
ax.set_ylabel("Yield (%)")
ax.set_title("Yield by particle size")
fig.savefig(FIG / "fig2_bar.png", dpi=300, bbox_inches="tight")
plt.close(fig)


# 3. 直方图：标签分布（判断有没有偏态、有没有离群）
fig, ax = plt.subplots(figsize=(5.2, 4.0))
ax.hist(df["yield_pct"], bins=10, color="#0f766e", alpha=0.8, edgecolor="white")
ax.set_xlabel("Yield (%)")
ax.set_ylabel("Count")
ax.set_title("Distribution of yield")
fig.savefig(FIG / "fig3_hist.png", dpi=300, bbox_inches="tight")
plt.close(fig)

print("saved 3 figures -> {}".format(FIG))

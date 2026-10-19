# -*- coding: utf-8 -*-
"""环境自检：确认 Python 版本与关键依赖是否就位。

用法:
    python src/check_env.py

全部 [OK] 表示环境可用；出现 [MISS] 按最后一行提示补装。
"""

import platform
import sys
from importlib.metadata import PackageNotFoundError, version

print("=" * 56)
print("Python :", sys.version.split()[0])
print("Exe    :", sys.executable)
print("OS     :", platform.platform())
print("=" * 56)

# (显示名, import 时用的模块名, pip 包名)
REQUIRED = [
    ("numpy", "numpy", "numpy"),
    ("pandas", "pandas", "pandas"),
    ("matplotlib", "matplotlib", "matplotlib"),
    ("scikit-learn", "sklearn", "scikit-learn"),
    ("openpyxl", "openpyxl", "openpyxl"),
]

missing = []
for label, mod_name, dist_name in REQUIRED:
    try:
        __import__(mod_name)  # 确认真的能 import，不只是装了
        print("[OK]   {:<14} {}".format(label, version(dist_name)))
    except ImportError:
        print("[MISS] {:<14} not installed".format(label))
        missing.append(dist_name)
    except PackageNotFoundError:
        print("[OK]   {:<14} (version unknown)".format(label))

print("=" * 56)

major_minor = sys.version_info[:2]
if major_minor != (3, 11):
    print("[WARN] Python 3.11 expected, got {}.{}".format(*major_minor))
    print("       DeepChem / DGL 在 3.12+ 上会静默装错版本，见 W0 任务卡 Day 1。")

if missing:
    print("Fix with:  pip install " + " ".join(missing))
    sys.exit(1)

print("Environment ready. Go to Day 2 (classes).")

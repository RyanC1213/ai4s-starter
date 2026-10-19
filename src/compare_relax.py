# -*- coding: utf-8 -*-
"""对比两种取胞弛豫后的每原子能量，判断计算是否自洽。

用法:
    python src/compare_relax.py
    python src/compare_relax.py --device cpu

为什么需要这个脚本:
    CIF 文件只存几何结构（晶胞 + 原子坐标），不存能量。
    对 read('xxx.cif') 得到的 Atoms 调 get_potential_energy() 会报
    "Atoms object has no calculator"。
    能量存在 .traj 轨迹里 —— ASE 读取轨迹时会自动挂上 SinglePointCalculator。
    所以对比必须基于 .traj，不能基于 .cif。
"""

import argparse
import sys
from pathlib import Path

from ase.io import read

ROOT = Path(__file__).resolve().parents[1]
TRAJ = ROOT / "figures"


def energy_per_atom(traj_path, atoms):
    """先尝试从轨迹自带的计算器取能量；取不到再用 MACE 重算单点。"""
    try:
        return atoms.get_potential_energy() / len(atoms), "轨迹"
    except RuntimeError:
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    args = ap.parse_args()

    targets = [
        ("18 原子原胞", TRAJ / "relax_23584.traj"),
        ("36 原子常规胞", TRAJ / "relax_67647.traj"),
    ]

    results = []
    for label, path in targets:
        if not path.exists():
            print("[MISS] 找不到 %s" % path)
            print("       先跑: python src/relax_bi2wo6.py --gpu%s"
                  % ("" if "23584" in str(path) else " --cell 67647"))
            return 1

        atoms = read(str(path), index=-1)
        n = len(atoms)
        e, src = energy_per_atom(path, atoms)

        if e is None:
            print("[INFO] %s 的轨迹里没有能量，改用 MACE 重算单点 ..." % path.name)
            from src.relax_bi2wo6 import build_calculator
            calc, _ = build_calculator(args.device)
            atoms.calc = calc
            e = atoms.get_potential_energy() / n
            src = "重算"

        results.append((label, path.name, n, e, src))
        print("%-12s %-24s n=%-3d  %.4f eV/atom  (来源: %s)" % (label, path.name, n, e, src))

    e18 = results[0][3]
    e36 = results[1][3]
    diff_mev = abs(e18 - e36) * 1000

    print("-" * 62)
    print("每原子能量差: %.2f meV/atom" % diff_mev)

    if diff_mev < 3:
        print("判定: [自洽] 两种取胞等价，弛豫充分，可以往下做表面模型。")
    elif diff_mev < 10:
        print("判定: [基本通过] 差 %.1f meV 略偏大，可能有一个结构没完全收敛。" % diff_mev)
        print("     建议: 用 --steps 600 --fmax 0.03 重跑较差的那个。")
    else:
        print("判定: [不通过] 差 %.1f meV 太大，说明结构或弛豫有问题。" % diff_mev)
        print("     检查: 1) 两个文件晶胞参数是否正常  2) 是否真的收敛")
        return 1

    # 顺带体检晶胞
    print("-" * 62)
    inputs = {
        "23584": ROOT / "data" / "structures" / "Bi2WO6_ICSD23584.cif",
        "67647": ROOT / "data" / "structures" / "Bi2WO6_ICSD67647.cif",
    }
    for (label, path) in targets:
        a = read(str(path), index=-1)
        p = a.cell.cellpar()
        key = "23584" if "23584" in path.name else "67647"
        v0 = read(str(inputs[key])).get_volume()
        print("%-12s a=%.3f b=%.3f c=%.3f Å  V=%.1f Å³  (输入 CIF V=%.1f)"
              % (label, p[0], p[1], p[2], a.get_volume(), v0))

    print("-" * 62)
    print("说明：本次是【定胞弛豫】——只让原子挪位置，晶胞不动。")
    print("      所以 V 与输入 CIF 完全一致是【正确】的，不是 bug。")
    print("      要优化晶胞需改用 ExpCellFilter（W2 再做，那时才谈得上和实验值比）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

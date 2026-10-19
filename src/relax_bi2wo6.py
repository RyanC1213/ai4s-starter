# -*- coding: utf-8 -*-
"""用 MACE 通用势函数弛豫 Bi2WO6 结构。

用法:
    python src/relax_bi2wo6.py                 # 默认用 18 原子原胞，CPU
    python src/relax_bi2wo6.py --gpu           # 用 GPU
    python src/relax_bi2wo6.py --cell 67647    # 用 36 原子常规胞

前置:
    pip install "mace-torch==0.3.*" ase

注意:
    MACE 的 API 在不同版本间改过名字（mace_mp 的参数、模型名）。
    如果这里报 TypeError / AttributeError，先跑 python -c "from mace.calculators import mace_mp; help(mace_mp)"
    看当前版本的参数名，再改下面 build_calculator() 里那两行。
"""

import argparse
from pathlib import Path

from ase.io import read, write
from ase.optimize import BFGS

ROOT = Path(__file__).resolve().parents[1]          # 仓库根 w0-starter/
STRUCT_DIR = ROOT / "data" / "structures"
OUT_DIR = ROOT / "data" / "relaxed"
TRAJ_DIR = ROOT / "figures"                          # 轨迹也放这里，figure 目录已存在


def build_calculator(device: str = "cpu"):
    """加载 MACE-MP 预训练模型。不同版本参数名不一样，这里做兼容。"""
    from mace.calculators import mace_mp

    attempts = [
        # 0.3.x 常见写法
        dict(model="medium", dispersion=False, default_dtype="float32", device=device),
        # 较新写法
        dict(model="mace-mp-0", default_dtype="float32", device=device),
        # 最保守
        dict(default_dtype="float32", device=device),
    ]
    last_err = None
    for kw in attempts:
        try:
            return mace_mp(**kw), kw
        except (TypeError, ValueError) as e:
            last_err = e
            continue
    raise RuntimeError("MACE 加载失败，最后一条错误: %s" % last_err)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", action="store_true", help="用 CUDA")
    ap.add_argument("--cell", default="23584", choices=["23584", "67647"],
                    help="23584=18原子原胞 / 67647=36原子常规胞")
    ap.add_argument("--fmax", type=float, default=0.05, help="力收敛判据 eV/Å")
    ap.add_argument("--steps", type=int, default=300)
    args = ap.parse_args()

    cif = STRUCT_DIR / ("Bi2WO6_ICSD%s.cif" % args.cell)
    if not cif.exists():
        raise FileNotFoundError("找不到结构文件: %s" % cif)

    atoms = read(str(cif))
    n = len(atoms)
    e0 = None
    print("=" * 58)
    print("结构   :", cif.name)
    print("原子数 :", n, "|", atoms.get_chemical_formula())
    print("晶胞   : a=%.3f b=%.3f c=%.3f Å" % tuple(atoms.cell.cellpar()[:3]))

    device = "cuda" if args.gpu else "cpu"
    print("设备   :", device)
    print("加载 MACE 权重（首次会下载约 100–500 MB，卡住是正常的）...")

    calc, used_kw = build_calculator(device)
    print("已加载 :", used_kw)
    atoms.calc = calc

    e0 = atoms.get_potential_energy()
    f0 = abs(atoms.get_forces()).max()
    print("-" * 58)
    print("初始能量 : %.4f eV  (%.4f eV/atom)" % (e0, e0 / n))
    print("初始最大力: %.3f eV/Å" % f0)

    print("开始弛豫 (BFGS, fmax=%.2f, 最多 %d 步)..." % (args.fmax, args.steps))
    TRAJ_DIR.mkdir(exist_ok=True)
    opt = BFGS(atoms, logfile="-", trajectory=str(TRAJ_DIR / ("relax_%s.traj" % args.cell)))
    opt.run(fmax=args.fmax, steps=args.steps)

    e1 = atoms.get_potential_energy()
    f1 = abs(atoms.get_forces()).max()
    print("-" * 58)
    print("弛豫后能量 : %.4f eV  (%.4f eV/atom)" % (e1, e1 / n))
    print("弛豫后最大力: %.3f eV/Å" % f1)
    print("能量下降   : %.4f eV/atom" % ((e0 - e1) / n))
    print("是否收敛   :", "是" if f1 <= args.fmax else "否（加大 --steps 或放宽 --fmax）")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / ("Bi2WO6_%s_relaxed.cif" % args.cell)
    write(str(out), atoms)
    print("已保存     :", out)
    print("=" * 58)


if __name__ == "__main__":
    main()

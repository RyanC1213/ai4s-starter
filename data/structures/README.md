# structures · Bi₂WO₆ 结构文件

## 文件说明

| 文件 | 原子数 | 晶胞 | 用途 |
|---|---|---|---|
| `Bi2WO6_ICSD23584.cif` | 18 | 原胞（a=b=8.917 Å, c=5.548 Å, γ=143.5°） | 体相弛豫、能量计算——**快，先用这个** |
| `Bi2WO6_ICSD67647.cif` | 36 | 常规胞（a=5.530, b=5.569, c=16.955 Å，正交） | 切表面、建 slab 模型——**直观，W2 用这个** |

两者都是正交 Aurivillius 相（空间群 Pca2₁ 族），只是取胞方式不同，**化学上是同一个相**。

## 来源

从 AFLOW 仓库下载的 ICSD 标准化结构：

- ICSD 23584 → `aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/ORCC/Bi2O6W1_ICSD_23584`
- ICSD 67647 → `aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/ORC/Bi2O6W1_ICSD_67647`

AFLOW 导出时统一转成 P1 对称性（只保留平移，丢掉点群操作），因此 CIF 里 `_symmetry_space_group_name_H-M` 显示 `'P1'`。**这不影响计算**，只是文件里没有对称性信息。

## 使用前必须知道的三件事

1. **晶格常数来自 ICSD 实验值，可能与你课题组的样品有差异。** 使用前先做一次弛豫，并和你文献里的 a/b/c 对照。差超过 1% 就要警惕。
2. **AFLOW 的结构是标准化过的**，原子顺序、原点选择和你习惯的可能不同。切表面时先确认层状方向（这个相的长轴是 c ≈ 17 Å，对应 Bi₂O₂ 层与 WO₆ 层交替堆叠）。
3. **引用**：使用 AFLOW 数据需引用其方法学论文（AFLOW 官网有 citation 指引）。如果你后续把结构写进论文，正式引用应给原始 ICSD 条目，而不是 AFLOW。

## 怎么读进 Python

```python
from ase.io import read

atoms = read("data/structures/Bi2WO6_ICSD67647.cif")
print(atoms.get_chemical_formula())   # Bi8 O24 W4
print(len(atoms), "atoms")
print(atoms.cell.cellpar())
```

## 建议的下一步

1. 先弛豫 18 原子原胞（`src/relax_bi2wo6.py`，脚本已写好），确认能量和晶格常数合理
2. 再弛豫 36 原子常规胞，对比两者每原子能量是否一致（应该几乎相同，差 >1 meV/atom 说明弛豫没收敛）
3. W2 从常规胞沿 c 轴切 (001) 面，做 2×2 slab，加 15 Å 真空层
4. W3 在表面放一个 Pd 原子，算吸附能——**这才是你课题的真正起点**

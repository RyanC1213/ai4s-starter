# AI4Science Starter · Bi₂WO₆ 光催化体系的机器学习势函数计算

一个从零开始搭建的 AI for Science 入门仓库。目标：用通用机器学习势函数（MACE）替代重复的 DFT 计算，为后续"催化剂性能预测 + 实验数据建模"打基础。

**当前进度：W1 已完成** —— 环境搭通、Bi₂WO₆ 双取胞弛豫收敛、交叉验证通过（能量差 0.14 meV/atom）。

> 我做了什么、数据在哪、哪些地方可能不准，都记在 [`docs/week1/notes.md`](docs/week1/notes.md)。

---

## 先看这个

👉 **打开 `docs/week1/00-操作手册.html`**（双击即可，浏览器打开）。

14 个步骤，每步都写了「去哪里 / 怎么做 / 应该看到什么 / 为什么 / 出错了怎么办」。**不要跳步。**

---

## 目录

```
project/
├── README.md                  你正在读的
├── requirements.txt           依赖清单
├── .gitignore                 哪些文件不进仓库
├── sync.bat                   从工作区同步最新文件（双击运行）
├── docs/                      所有文档
│   ├── README.md              ★ 文档索引，先看这个
│   ├── week1/                 W1 全套材料
│   │   ├── 00-操作手册.html           环境搭建 14 步（五栏详解）
│   │   ├── 01-建仓与MACE原理.html     GitHub 建仓 + 文献对比 + MACE 原理
│   │   ├── notes.md                   W1 复盘（你自己写）
│   │   └── answers.html               五问参考答案（v2，已交叉审核）
│   └── reference/             长期参考，不随周次变动
│       ├── ai4science-internship-roadmap.html   20 周实习冲刺路线
│       ├── ai4s-project-shortlist.html          14 个开源项目选型
│       ├── gpu-setup-windows-5060ti.html        RTX 50 系避坑
│       ├── w0-day0-setup-card.html              Day 0 报错排查
│       └── w0-plan-and-deepchem.html            W0 七天任务卡
├── data/
│   ├── demo_data.csv          合成占位数据（练 pandas 用，不是真数据）
│   └── structures/            Bi₂WO₆ 结构（ICSD 23584 / 67647）
├── figures/                   出图与轨迹
└── src/
    ├── check_env.py           检查依赖是否装全
    ├── check_gpu.py           检查显卡能否【真正】计算
    ├── read_data.py           读表格 + 体检 + 清洗
    ├── make_plots.py          画三张图
    ├── relax_bi2wo6.py        用 MACE 弛豫 Bi₂WO₆
    └── compare_relax.py       对比两种取胞的能量，判断计算是否自洽
```

---

## 快速开始

```bash
conda create -n ai4s python=3.11 -y
conda activate ai4s
cd C:\Users\Administrator\Desktop\project

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python src/check_gpu.py          # 必须看到 VERDICT: GPU 可用

pip install -r requirements.txt
pip install "mace-torch==0.3.*" ase
python src/check_gpu.py          # 装完 MACE 必须重验

python src/relax_bi2wo6.py --gpu
```

**⚠️ 你的显卡是 RTX 5060 Ti（Blackwell, sm_120），必须用 cu128 的 PyTorch。** 装错版本时 `torch.cuda.is_available()` 仍返回 True，但一算就崩。详见 `docs/reference/gpu-setup-windows-5060ti.html`。

---

## 环境

| 项 | 版本 / 配置 |
|---|---|
| 系统 | Windows 10/11（无 Linux，不装 WSL2） |
| GPU | RTX 5060 Ti 8 GB（sm_120，8151 MiB） |
| Python | 3.11（conda 环境 `ai4s`） |
| PyTorch | cu128 轮子，版本号带 `+cu128` |
| 势函数 | MACE-MP（`mace-torch==0.3.*`） |

---

## 数据来源

`data/structures/` 下的两个 CIF 来自 AFLOW 的 ICSD 条目：

- `Bi2WO6_ICSD23584.cif` — 18 原子原胞（a=b=8.917 Å, c=5.548 Å, γ=143.5°）
- `Bi2WO6_ICSD67647.cif` — 36 原子常规胞（a=5.530, b=5.569, c=16.955 Å）

两者化学等价，只是取胞方式不同。**写论文时引用原始 ICSD 条目，不是 AFLOW。**

`data/demo_data.csv` 是**合成占位数据**，仅用于跑通 pandas 流程，**不得写入任何报告或论文**。

---

## 纪律

1. 每装一个大包，重跑 `check_gpu.py`
2. 每个计算都留 `.traj` 轨迹，不要只留结果
3. 每天至少一个 commit
4. 删数据要写清"删了多少、为什么删"

---

## 更新记录

| 日期 | 做了什么 |
|---|---|
| 2026-10-19 | 建仓；环境搭建（conda 26.9.3 / Python 3.11.17 / torch 2.11.0+cu128） |
| 2026-10-19 | 拿到 Bi₂WO₆ 结构（ICSD 23584 / 67647），写好 MACE 弛豫与对比脚本 |
| 2026-10-19 | 双取胞弛豫完成，能量差 0.14 meV/atom；首次推送到 GitHub |

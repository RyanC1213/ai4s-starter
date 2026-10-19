# -*- coding: utf-8 -*-
"""验证 PyTorch 能否在你的显卡上【真正】计算。

用法:
    python src/check_gpu.py

为什么需要这个脚本：
    torch.cuda.is_available() 返回 True 只说明"系统看到了显卡"，
    不代表 PyTorch 里编译了这张卡能用的内核。
    RTX 50 系是 Blackwell（sm_120），只有 cu128 及以上的轮子才带它的内核。
    装错版本时，is_available() 照样是 True，但一算就崩：
        RuntimeError: CUDA error: no kernel image is available for execution on the device
    所以必须跑一次真实矩阵乘，这是唯一有效的验收。
"""

import sys
import time

try:
    import torch
except ImportError:
    print("[FAIL] 没装 torch。先执行:")
    print("       pip install torch --index-url https://download.pytorch.org/whl/cu128")
    sys.exit(1)

print("=" * 58)
print("Python :", sys.version.split()[0])
print("torch  :", torch.__version__)
print("cuda   :", torch.version.cuda)
print("=" * 58)

if not torch.cuda.is_available():
    print("[FAIL] torch.cuda.is_available() = False")
    print("  可能原因:")
    print("   1. 装成了 CPU 版 torch（版本号里没有 +cu128）")
    print("   2. 显卡驱动太旧，低于 CUDA 12.8 所需版本（需 R570 以上）")
    print("   3. 装的是 Mac 风格的通用轮子，不是 Windows CUDA 轮子")
    sys.exit(1)

name = torch.cuda.get_device_name(0)
cap = torch.cuda.get_device_capability(0)
props = torch.cuda.get_device_properties(0)

print("GPU    :", name)
print("算力   : sm_%d%d" % (cap[0], cap[1]))
print("显存   : %.1f GB" % (props.total_memory / 1024 ** 3))

arch = torch.cuda.get_arch_list()
print("编译架构:", " ".join(arch))
has_120 = any(a in ("sm_120", "compute_120") for a in arch)
print("含 sm_120 内核:", "是" if has_120 else "否 —— 看下面的实测结果定生死")
print("-" * 58)

# ---------- 实测 1: fp16 矩阵乘 ----------
# 注意：第一次 CUDA 调用会初始化 cuBLAS 并加载内核，耗时可达十几秒。
# 不预热直接计时，会把 0.07 ms 的操作测成 700 ms（真实踩过的坑）。
try:
    import statistics

    a = torch.randn(512, 512, device="cuda", dtype=torch.float16)
    b = torch.randn(512, 512, device="cuda", dtype=torch.float16)

    for _ in range(10):          # 预热，不计时
        _ = a @ b
    torch.cuda.synchronize()

    samples = []
    for _ in range(30):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        _ = a @ b
        torch.cuda.synchronize()
        samples.append((time.perf_counter() - t0) * 1e3)

    med = statistics.median(samples)
    print("[OK] fp16 矩阵乘 512x512 : 中位数 %.3f ms (min %.3f)" % (med, min(samples)))
    if med > 5:
        print("     [WARN] 偏慢。若已预热仍 >5 ms，检查是否被其他程序占用显卡。")
except RuntimeError as e:
    print("[FAIL] 真实运算失败:", str(e)[:220])
    print()
    print("  => 装错 CUDA 轮子了。修复:")
    print("     pip uninstall -y torch torchvision torchaudio")
    print("     pip install torch --index-url https://download.pytorch.org/whl/cu128")
    print("     然后重新运行本脚本。")
    sys.exit(1)

# ---------- 实测 2: 大矩阵吞吐（看真实算力，不只是“能跑”）----------
try:
    a2 = torch.randn(2048, 2048, device="cuda", dtype=torch.float16)
    b2 = torch.randn(2048, 2048, device="cuda", dtype=torch.float16)
    for _ in range(3):
        _ = a2 @ b2
    torch.cuda.synchronize()

    s2 = []
    for _ in range(20):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        _ = a2 @ b2
        torch.cuda.synchronize()
        s2.append((time.perf_counter() - t0) * 1e3)
    m2 = statistics.median(s2)
    tflops = 2 * 2048 ** 3 / (m2 / 1e3) / 1e12
    print("[OK] fp16 矩阵乘 2048x2048: 中位数 %.3f ms  ≈ %.1f TFLOPS" % (m2, tflops))
    print("     (RTX 5060 Ti 参考值：30–50 TFLOPS，明显低于 20 说明有问题)")
except RuntimeError as e:
    print("[WARN] 大矩阵测试失败:", str(e)[:160])

# ---------- 实测 3: 训练一步 ----------
try:
    import torch.nn as nn

    net = nn.Sequential(
        nn.Linear(128, 512), nn.SiLU(), nn.Linear(512, 1)
    ).cuda()
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    x = torch.randn(256, 128, device="cuda")
    y = torch.randn(256, 1, device="cuda")
    loss = ((net(x) - y) ** 2).mean()
    opt.zero_grad()
    loss.backward()
    opt.step()
    print("[OK] 训练一步           : loss=%.4f" % loss.item())
except Exception as e:
    print("[FAIL] 训练失败:", str(e)[:220])
    sys.exit(1)

print("=" * 58)
print("VERDICT: GPU 可用，可以进入 W1。")
print()
print("提醒: 之后每次 pip install 大包（尤其是 mace-torch）都要再跑一次本脚本。")
print("      pip 有可能顺手把 torch 降级成 cu121，那时 GPU 会静默失效。")

# Stage 0 独立推导材料

这里是阶段 0“必须独立手推”清单九项的独立推导与机器核查，供 `docs/learn/` 下的学习文档引用。

## 来源

- 2026-10-19 由 ChatGPT 按项目给出的约定（`configs/reference.json` 的车辆参数、旧状态显式 Euler、后轴参考点）独立推导，不以项目计划中的公式为输入。
- 文件按原样保存，未做修改。`validation/source_sha256.json` 记录了 9 个脚本和 3 个 Lean 文件的 sha256，入库时已逐一核对一致。
- 同日在两套环境里复跑：
  - 作者环境：WSL Ubuntu 22.04，Python 3.10，SymPy 1.9，SciPy 1.8，Shapely 2.1。
  - Claude 环境：Python 3.13，SymPy 1.14，SciPy 1.18，Shapely 2.2。

  9 个脚本在两套环境里都全部通过。
- 与 PR #3 实现的逐项对照结论：九项全部一致，没有发现实现错误。报告里的“0.0505 不一致”实际是每采样间隔与每子步两种口径的差别，见 `docs/learn/vehicle-model.md` §7。

## 内容

| 文件 | 内容 |
|---|---|
| `report.md` | 完整推导报告（第 1–9 项、复现方式、核对表） |
| `scripts/d01`–`d09` | 每项一个独立脚本：SymPy 恒等式断言，加上 SciPy/Shapely 数值交叉验证 |
| `lean/D06`、`D07`、`D08` | 三圆覆盖、刚体位移界、航向势函数的 Lean 4 证明（Mathlib 9c6a29e8，Lean 4.36.0-rc1） |
| `lean/STATUS.md`、`lean/COMPILE.log` | 形式化范围与编译记录（全部退出码 0，无 `sorry`/`admit`/新增公理） |
| `validation/` | 作者环境的运行日志和源文件哈希 |

## 复现

```sh
pip install sympy numpy scipy shapely
python scripts/d01_turning_radius.py   # … 到 d09_reverse_bay.py
```

Lean 需要 `elan`，以及 `lake exe cache get` 下载的 Mathlib 缓存（数 GB），步骤见 `lean/STATUS.md`。这些脚本和证明都不进 CI，`ruff` 也不检查本目录。

## 使用注意

- 第 4 项（平行泊车最小车位）只在报告明示的路径族和障碍假设下成立，原问题本身是欠定的。
- 第 7 项的位移界只界定端点位移，不构成对任意浅擦的检测保证。
- `lean/compile-checked-environment.sh` 里的路径是作者本机路径，仅作记录。

# 小车运动的物理模型

本文面向本项目的研究员，讲清楚环境里的小车是怎样动的、为什么这样建模，以及每一条结论在项目里由什么验证。实现的唯一来源是 `src/parking_rl/physics/`，本文只做解释。

## 怎么读出处标记

文献沿用 `PLAN_MACRO.md` 的出处等级：

- `[V]`：已打开原文核实。
- `[C]`：基本可信，但细节尚未逐条核实。
- `[?]`：未核实，**不能**作为结论依据。

本项目自己推导并做过机器核查的结论标为 **[本项目]**，后面给出复现位置：

- `d0N`：`research/stage0-derivations/scripts/d0N_*.py`
- `Lean Dxx`：`research/stage0-derivations/lean/Dxx*.lean`
- `test_…`：仓库里的 pytest 节点

参考车辆参数取自 `configs/reference.json`：

| 符号 | 含义 | 数值 |
|---|---|---|
| L | 轴距 | 2.7 m |
| f / r | 前悬（前轴到车头）/ 后悬（后轴到车尾） | 0.9 / 1.1 m |
| l = L+f+r | 车长 | 4.7 m |
| w | 车宽 | 1.85 m |
| δ_max | 最大前轮转角 | 0.6 rad |
| δ̇_max | 最大转角速率 | 0.6 rad/s |
| v_max | 最大速度 | 1.5 m/s |
| a_max | 最大加速度 | 1.5 m/s² |
| dt / dt_sub | 策略步 / 积分子步 | 0.1 s / 0.02 s（5 个子步） |

## 1. 状态、动作与参考点

- **状态** `(x, y, θ, v, δ)`：`(x, y)` 是**后轴中点**的世界坐标，`θ` 是航向（从 +x 轴逆时针为正），`v` 是带符号速度（正为前进、负为倒车），`δ` 是前轮转角（正为左转）。
- **策略动作**是归一化的 `(longitudinal, steering_rate) ∈ [−1, 1]²`。它只在 `physics/action_scaling.py` 这一处缩放为物理控制量 `(a, δ̇) = (a_max·longitudinal, δ̇_max·steering_rate)`。
- 策略**不能**直接指定转角或速度，只能指定它们的变化率。这是刻意的设计：真实车辆的方向盘和油门都有执行器动态，策略必须学会提前打方向。

参考点选在后轴中点，原因有三：

1. 后轴参考下，运动学方程最简单，转弯半径公式 `R = L/tanδ` 也只对后轴成立（§2）。
2. 阶段 1 的经典规划器（Dubins、Reeds–Shepp、Hybrid A*）都以后轴为参考，共用参考点才能把它们作为基线和 oracle。
3. 车身矩形相对后轴是**不对称**的（f ≠ r），因此参考点一旦放错，所有碰撞几何都会整体平移，见 §5。

## 2. 后轴运动学自行车模型

把同一轴上的两个轮合并为一个，假设轮胎不侧滑：

```
ẋ = v cos θ
ẏ = v sin θ
θ̇ = (v / L) · tan δ
```

**转弯半径与瞬时转动中心（ICR）**：常转角时后轴走圆，圆心在后轴的左法线上，

```
ρ = L / tan δ（带符号），   C = (x − ρ sin θ,  y + ρ cos θ)
```

推导方法是要求圆心 `C = z + ρ·n` 不动，即 `Ċ = 0`，由此直接解出 ρ。最小转弯半径为

```
R_min = L / tan δ_max = 2.7 / tan 0.6 = 3.946579 m
```

**旋转方向**由 `θ̇` 的符号决定：前进左打、倒车右打为逆时针；前进右打、倒车左打为顺时针。倒车时“打方向”的直觉与前进相反，这正是泊车难学的地方之一。

**与质心参考形式的区别**：如果参考点取在后轴前方 `b` 处（例如质心），参考点的速度方向会偏离车身方向一个侧偏角

```
β = arctan(b · tan δ / L)
```

此时质心沿半径 `√(ρ² + b²)` 的圆运动，ICR 不变。两种形式描述的是同一辆车，但速度、半径和公式都不同，不能混用。比如把质心速度代入后轴公式，就会得到错误的轨迹。本项目所有地方都用后轴形式。

- 出处：Rajamani, *Vehicle Dynamics and Control*, Ch. 2 `[C]`（Ackermann 几何、ICR、后轴与质心的区别）；LaValle, *Planning Algorithms* (2006), §13.1.2 `[C]`（simple car，非完整约束）。
- [本项目]：d01（固定 ICR 的符号断言，以及四种方向的 SciPy 积分，误差 5.8e-11 m）；`test_minimum_turn_radius_uses_rear_axle_bicycle_geometry`；EXIT-0.2 `test_exit_0_2_constant_steering_radius_and_closure`。

## 3. 执行器模型

每个策略步的处理顺序固定如下（`physics/dynamics.py`）：

1. **延迟 FIFO**：`latency_steps ∈ {0, 1, 2}`。延迟为 k 时，本步实际执行的是 k 步之前请求的动作，用来模拟控制链路的延迟。
2. **缩放**：把归一化动作变成 `(a, δ̇)`。
3. **控制限幅**：`a` 限在 `±a_max`，`δ̇` 限在 `±δ̇_max`。
4. **零阶保持**：同一个控制量在 5 个子步内保持不变。
5. 每个子步积分（§4）之后，做**状态限幅**：`v` 限在 `±v_max`，`δ` 限在 `±δ_max`。

由此得到四条在**每个子步**都成立的不等式：

```
|δ| ≤ δ_max,   |v| ≤ v_max,   |Δδ| ≤ δ̇_max · dt_sub = 0.012 rad,   |Δv| ≤ a_max · dt_sub = 0.030 m/s
```

**为什么要专门验证（EXIT-0.11）**：只要 `δ` 能越过 `δ_max` 漂移，RL 车的转弯半径就会小于 `R_min`。这种能力 Reeds–Shepp、Hybrid A* 和专家都没有，结果会表现为成功率虚高、最优性比虚低，看起来像 RL 胜过经典方法，其实是模拟器的 bug。

验证方式是压力测试 `parking-governance exit-0-11-stress`：

- 10⁶ 条序列，每条 400 个策略步，覆盖延迟 0/1/2、四个角持续饱和，以及超出范围的原始控制量。
- 每个子步检查上面四条不等式，违规必须为 0。
- 正对照：把限幅换成恒等函数，必须出现违规。

2026-10-19 在 Ryzen 9 9950X3D 上用 32 个进程跑完整规模，约 14 分钟：2×10⁹ 个子步，**0 次违规**；正对照 1 万条序列查出 92,150 次违规。证据见 `governance/evidence/`。

- [本项目]：`governance/clamp_stress.py`；`test_exit_0_11_stress_harness_and_real_positive_control`；`test_four_corner_saturation_respects_bounds_at_every_substep`；三个延迟 FIFO 测试 `test_latency_*`。

## 4. 离散化：旧状态显式 Euler

每个子步都用**旧状态**同时更新：

```
x⁺ = x + h·v·cos θ
y⁺ = y + h·v·sin θ
θ⁺ = θ + h·(v/L)·tan δ
v⁺ = clip(v + h·a, ±v_max)
δ⁺ = clip(δ + h·δ̇, ±δ_max)
```

其中 `h = dt_sub = 0.02 s`。位姿用的是旧的 `v`、`δ`、`θ`，速度和转角在本子步结束时才更新。

**常转角下离散点仍然落在圆上，但这个圆与物理圆不同**。记 `s = v·h`，`α = s/ρ`，用复数等比级数求和可得，Euler 点列落在半径为

```
R_E = |s| / (2 |sin(α/2)|)
```

的圆上。圆心沿切向偏移约半步，即 `s/2`。满舵满速时 `R_E = 3.946589 m`，物理半径是 3.946579 m。

误差有三个层次：

| 误差 | 量级 | 满舵满速数值 |
|---|---|---|
| 单步弦长误差 | O(h³) | 7.2e-8 m |
| 单步终点误差（漏掉法向位移 `ρ(1 − cos α)`） | O(h²) | 1.14e-4 m |
| 固定时长的全局位置误差 | O(h) | — |
| 绕一圈的闭合距离（827 步） | ≤ 约半个子步行程 | 0.0129 m |

由此有两个推论：

- EXIT-0.2 的闭合容限取 `1.5·|v|·dt_sub = 0.045 m` 是合理的；v1.0 要求的 1e-3 m 会让正确的实现失败。倒车时要取 `|v|`。
- 旧状态 Euler 的平移项在倒车时反号，所以**前进和倒车的离散轨迹并不完全镜像对称**，这是格式本身的性质，不是 bug。

这种误差本质上就是“用左端点求和近似积分”：每个子步沿旧航向走一段直线，而不是沿圆弧走。

- [本项目]：d02（3000 个随机工况，点到 Euler 圆的残差 2.7e-15 m）；`test_integrate_substep_matches_old_state_explicit_euler_golden_values`；`test_policy_step_uses_zero_order_hold_for_exactly_five_substeps`。
- 计划中的假设 A24（显式 Euler + ZOH）：`stages/PLAN_S0.md`。

## 5. 车身几何

车身在后轴坐标系中占据

```
ξ ∈ [−r, L + f] = [−1.1, 3.6],   η ∈ [−w/2, w/2] = [−0.925, 0.925]
```

离后轴最远的是前角：`d_max = √((L+f)² + (w/2)²) = 3.716938 m`。

**EXIT-0.10 的教训**：如果有人把车身以后轴为中心摆放（`x ∈ [−2.35, 2.35]`），或者把 f 和 r 写反，阶段 0–2 的所有其他判据依然会通过。原因是规划器和环境共用同一个 footprint，两边“一致地错”。唯一能区分正确摆放的是 `f ≠ r` 这个不对称，所以测试把 `min_x = −r` 和 `max_x = L+f` 作为**两个独立断言**来写。

- [本项目]：`test_exit_0_10_vehicle_footprint_is_placed_from_rear_axle`；`test_exit_0_10_rotated_vehicle_matches_hand_computed_rear_axle_footprint`。

## 6. 碰撞几何：OBB 与有向距离

两个有向矩形（OBB）之间的有向距离 `sd` 分三种情况：

| 情况 | 定义 | 计算 |
|---|---|---|
| 分离 | 正的欧氏集合距离 | 枚举双方每个顶点到对方每条边的距离，取最小值 |
| 相交 | 负的最小脱离平移长度（MTV） | 在 4 个候选轴（两个矩形各两条边法向）上，取 `min(t₊, t₋)` 的最小值 |
| 包含 | 同上 | 上式自动正确；**不能**用投影区间的交集长度 |

两个反例，对应 EXIT-0.4：

- **包含时不能用交集长度**：`A = [−2,2]²` 与 `B = [−1,1]²` 同心，投影交集长度为 2，但真正的退出深度是 3，所以 `sd = −3`。
- **SAT 面法向间隙会低估角对角距离**：`A = [−1,0]²`、`B = [1,2]²`，真实距离是 √2，SAT 间隙只有 1。B 相对旋转 20° 时，真实距离 1.476795，SAT 间隙 1.422569。因此 SAT 间隙只能当下界，不能当距离用。

- 出处：Ericson, *Real-Time Collision Detection* (2005), Ch. 4–5 `[?]`（SAT、OBB、点到线段最近点），核实前只作参考。
- [本项目]：d05（2000 对随机矩形与 Shapely 对照，误差 1.8e-15 m）；EXIT-0.1、0.3、0.4（`tests/exit_criteria/`）；`test_sat_penetration_accounts_for_*_containment`；`test_vertex_vertex_distance_is_not_the_sat_gap`。

## 7. 连续碰撞（CCD）：采样式，不是解析碰撞时刻

**刚体位移界**：车身上任意一点 p 从一个位姿走到下一个位姿时，位移满足

```
‖ΔP‖ ≤ ‖Δz‖ + 2‖p‖·|sin(Δθ/2)| ≤ ‖Δz‖ + d_max · |Δθ|
```

其中 `Δz` 是后轴平移。推导依据是 `‖(Q(a) − I)p‖ = 2|sin(a/2)|·‖p‖`，再加三角不等式。

实现（`physics/ccd.py`）用这个界细分每个子步，保证相邻两个采样之间任意车身点的位移界不超过 **0.025 m**，然后在每个采样点做精确的 OBB/SAT 检测。

几个容易混淆的数：

| 量 | 数值 | 含义 |
|---|---|---|
| 采样间隔 0.026 m 时的界 | 0.0505 m | 计划中 EXIT-0.5 的参考值，`0.026 × (1 + d_max/R_min) = 0.026 × 1.9419` |
| 整个子步（0.03 m）的界 | 0.058254 m | 同一个系数乘以满速子步行程 |
| Euler 实际角点最大位移 | 0.046113 m | 倒车、满舵；前进时为 0.045978 m |
| 精确圆弧的角点位移 | 0.046045 m | `2√((L+f)² + (R+w/2)²)·sin(α/2)` |

后两行的差距来自 §4 的离散化误差；第二行与第三行差 26%，是因为三角不等式把方向不同的平移和转动直接相加，上界偏保守。

**保守的代价只是计算量**：上界偏大只会让每个子步多采样，不会多报或漏报碰撞。压力测试顺带统计了这一点（每 100 个子步抽 1 个，共 2×10⁷ 个子步）：按保守上界平均每子步 1.514 次采样，按精确角点位移是 1.351 次，多出约 12% 的几何计算，最多 3 次对 2 次。在真实尺度下影响很小。数据见 `governance/evidence/`。

**能保证什么、不能保证什么**：

- 能保证：如果墙厚大于采样间的位移界，车身的同一个点不可能在两个采样之间**完整穿过**这堵墙。这就是 EXIT-0.5 测的“隧穿”。
- 不能保证：车角在两个采样之间**浅擦**墙面又退出来。报告 d07 构造了一个约 2e-5 m 的反例，任何墙厚都无法排除这种情况。这类检测叫 motion-bounded sampled CCD，不能称为 exact CCD；要做解析碰撞时刻（TOI），需要另外实现。

- [本项目]：Lean D07 `rigid_displacement_bound` 与 `pose_displacement_bound`（任意初始航向）；d07（30000 个随机增量，界没有被违反；浅擦反例）；`test_full_lock_reference_motion_factor_locks_rotation_term`；`test_rotational_tunnelling_through_thin_wall_is_detected`；`test_densification_respects_farthest_point_motion_bound`。

## 8. 只用于奖励的几何

**三圆覆盖**（`reward_geometry/circles.py`）：把车身沿纵向三等分，每段取外接圆，

```
r₃ = √(l²/36 + w²/4) = 1.212121 m，   圆心 x = −0.3167, 1.25, 2.8167 m
```

三个圆盘的并集覆盖整个车身矩形，但比矩形大，因此只用于平滑的奖励项，**不能**进入碰撞或终止判断（不变式 I5，EXIT-0.6 会检查模块之间的导入边界）。

**航向势函数**（`reward/heading.py`）：

```
Φ(e) = 1 − cos(|wrap(e)| / 2),   Φ'(e) = ½ sin(e/2)   （正支）
```

它有三个性质：

- 在 0 附近 `Φ ≈ e²/8`，没有尖点。
- `(0, π]` 上没有驻点；在 π 处左导数为 ½。整角形式 `(1 − cos e)/2` 在 π 处有平台，也就是梯度为零，这正是 v1.1 的缺陷。
- **任何**在 0 处光滑取得极小值的势函数，都不可能在整个 `(0, π]` 上满足 `|Φ'| > 0.1`：Fermat 定理给出 `Φ'(0) = 0`，再由连续性，0 附近的导数必然很小。所以 v1.5 把 EXIT-0.12 改为：成功容差之外没有驻点，并且在 `[π − ε, π]` 上左导数不小于 `½cos(ε/2)`（ε = 10° 时为 0.4981）。

- [本项目]：Lean D06 `three_circles_cover`；Lean D08 `headingPhi_deriv_pos`、`no_uniform_deriv_lower_of_local_min`、`headingPhi_near_pi_bound`；d06、d08；`test_three_circle_cover_matches_the_analytic_radius`；`test_exit_0_12_*`。

## 9. 参考文献

| 等级 | 文献 | 用于 |
|---|---|---|
| `[C]` | LaValle, S. M. (2006). *Planning Algorithms*. Cambridge University Press, §13.1.2。免费在线：lavalle.pl/planning | 简单车模型、非完整约束、构型空间 |
| `[C]` | Rajamani, R. *Vehicle Dynamics and Control*, Ch. 2 | Ackermann 几何、ICR、后轴与质心参考 |
| `[?]` | Ericson, C. (2005). *Real-Time Collision Detection*, Ch. 4–5 | SAT、OBB、最近点 |
| [本项目] | `research/stage0-derivations/`（报告、脚本、Lean） | 上文所有推导与数值 |
| [本项目] | `stages/PLAN_S0.md` §5.0 与 EXIT-0.1–0.15（v1.5） | 判据原文与修订理由 |

按项目规则，`[?]` 文献在打开原文核实前不得在论文中引用。

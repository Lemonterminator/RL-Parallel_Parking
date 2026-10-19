# Stage 0：需要人类完成的理论与研究工作

这份清单提取自 Claude 整理的 `stages/PLAN_S0.md`。代码和自动测试只能验证已写下的模型；下面这些阅读、独立推导、研究口径与视觉判断仍需人类负责，不能用“测试通过”替代。

## 1. 理论阅读

- [ ] 必读：LaValle, *Planning Algorithms*, §13.1.2 与 §15.3。重点是 simple-car / bicycle model、非完整约束与 configuration space。
- [ ] 必读：Rajamani, *Vehicle Dynamics and Control*, Ch. 2。重点是 Ackermann 几何、ICR，以及 rear axle 与 CoG 参考点的区别。
- [ ] 建议读：Ericson, *Real-Time Collision Detection*, Ch. 4–5。计划中仍标为 `[?]`；引用进论文前必须亲自打开并核对版本、章节和结论。
- [ ] 平行泊车最小车位文献：核对两篇不同的 Vorobieva et al. 论文（2012 与 2013），不要合并为一篇；确认公式的车身长度、轴距、前后悬和参考点约定。
- [ ] Blackburn, *The Geometry of Perfect Parking*：文献存在，但计划仍把其代数结论视为未验证；引用或采用前需逐式核对。

## 2. 必须独立手推的内容

- [ ] 从 rear-axle bicycle 方程重新推导 `R=L/tan(delta)`，并写清它与 CoG 形式的差异；检查符号、前进/倒车和左右转约定。
- [ ] 推导理想两段反向等曲率 S 曲线，确认 `sqrt(4 R d - d^2)` 只是速率无限时的几何下界；把有 steering-rate ramp 的实际可执行性留给 Stage 1。
- [ ] 独立推导平行泊车最小车位：固定 kerb 一侧和转角符号，标注四个角的旋转半径，并写出前车、后车、路缘和交通侧净空四组不等式。不能从记忆抄闭式公式。
- [ ] 复核 reverse-bay 的单切边界与静态 containment 下界，包括 `W_gap`、`W_bay`、clearance、mouth clip 的物理含义和所有符号。
- [ ] 分情况推导 OBB signed distance：分离时的 vertex-edge 欧氏距离、相交时四轴 MTV、完全包含时的平移深度。
- [ ] 推导三圆覆盖的圆心与半径，并证明它保守覆盖车身；同时确认它只能用于平滑 reward，不能进入终止或指标路径。
- [ ] 推导 CCD 位移界 `translation + d_max*abs(delta_heading)`，明确它为何只证明采样分辨率，不等于解析 TOI。
- [ ] 推导 heading potential 的导数和成功方向语义，特别检查误差接近 0、π/2、π，以及 reverse-bay nose-out / nose-in。
- [ ] 手工确认显式 Euler 的更新顺序、zero-order hold、action clamp、state clamp、latency FIFO，以及五个 substep 的审计边界。

## 3. 需要人类拍板或第二双眼睛

- [ ] 审查计划 v1.2/v1.3 新增内容：A22、A24、A27 以及 EXIT-0.10～0.15；它们在计划中明确仍属 unreviewed。
- [ ] 决定 `W_gap` 的场景模型：保守墙模型还是相邻车模型；不能从 `W_bay` 静默推导。
- [ ] 决定单圆弧是否只是分析基线，以及 bay 难度门槛最终采用什么 operational oracle。
- [ ] 确认 reverse-bay 任务只接受 nose-out；如果要同时接受 nose-in，应当改任务定义和基线，而不是放宽当前 success test。
- [ ] 决定文档是否继续称为“exact CCD”。当前实现和证明是 motion-bounded sampled CCD；若要求解析 TOI，需要另立实现与 EXIT。
- [ ] 决定 `steering_gain` / `steering_offset` 作用于目标转角、转角速率还是传感器映射。当前 Stage 0 对非默认值直接报错，以避免悄悄选错语义。
- [ ] 修订 EXIT-0.12：建议改成“在 success tolerance 外无额外驻点，并在接近 π 的指定区间保持下界”，不要要求所有 `(0,π]` 的导数都大于 0.1。
- [ ] 修订 EXIT-0.13：`max_y` 应取完整 sweep，只有 bay-row x extent 做 `y<=0` clip；不可行的 `W_gap-2c < w` 网格项应明确期望 `InfeasibleBayGeometry`。
- [ ] 为 EXIT-0.11 运行完整 `10^6` 条、每条 400 policy steps、每步 5 substeps 的压力测试，并保存 seed、配置 hash、commit hash、样本数、零违规和 positive-control 结果。完成前 registry 必须保持 `planned`。

## 4. 人工动画验收

安装 `.[replay]` 后，录制并逐帧检查以下轨迹；保留 trace hash 和截图/视频作为研究笔记：

- [ ] 正速度、负速度、正满舵、负满舵的旋转方向都符合坐标约定。
- [ ] 常转角轨迹绕 rear-axle ICR 走圆，车身前后悬没有被错误地当作参考点。
- [ ] 满舵经过 0.055 m 薄墙以及垂直穿越薄墙时，连续 sweep 没有漏碰。
- [ ] S 曲线和换向处没有瞬移、转角跳变或额外一个 policy-step 的 latency 偏移。
- [ ] 同一初态、action、seed、配置和 commit 的保存/重放轨迹逐帧一致。
- [ ] reverse-bay nose-out 成功；几何上相同 footprint 的 nose-in 明确失败。

## 5. Stage 1 才能完成

- [ ] EXIT-0.8：用 single-cusp Hybrid A* 对平行泊车最小车位曲线做数值二分验证。
- [ ] EXIT-0.14(c)：在 `W_bay=2.50` 时用 Hybrid A* 二分 `W_aisle`，结果必须落在 `[3.5100, 4.3519]`。
- [ ] 验证受 steering-rate 限制的 S 曲线可执行性（EXIT-1.8），并把 planner 作为实际 bay feasibility oracle。

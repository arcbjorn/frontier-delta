# 02 -- Recursive Learning Map

This map records each recursive-learning idea considered for Frontier Delta and
the reason it is used, rejected as a central mechanism, or deferred.
The decision criterion is narrow: does the idea help measure support-set
expansion of a trainable solver under small-compute constraints?

| # | Approach | Papers / Systems | Decision | Rationale |
|---|----------|------------------|----------|-----------|
| 1 | Runtime reasoning scaffolds | ReAct, Reflexion, Generative Agents | **Reject** as core | Improves behavior through memory, reflection, or action selection. Useful baseline for sharpening, but no solver weights change. |
| 2 | Skill-store agents | Voyager | **Defer** | Skill libraries are relevant to transfer, but v1 first validates the support-set measurement loop. |
| 3 | Scaffold self-modification | Darwin Godel Machine, AlphaEvolve | **Reject** as core | Evolves code, tools, or algorithms under evaluator feedback. Strong future direction, but it measures system evolution more than solver support-set expansion. |
| 4 | Automated research agents | AI Scientist-v2 | **Reject** | Produces research artifacts. The objective here is measuring solver capability movement, not autonomous paper generation. |
| 5 | Self-generated verified data | STaR, ReST, SEAL | **Use** | Baseline closed loop: generate candidates, filter by grounded correctness, train on verified successes. |
| 6 | Algorithm distillation | Algorithm Distillation | **Defer** | Useful for compressing search behavior into a policy, but requires a stronger rollout/search engine than Phase 0. |
| 7 | RL with verifiable rewards | RLVR family, SPIRAL, Absolute Zero Reasoner | **Use** | Core training mechanism once real solvers replace the mock trainer. Deterministic verification is the project constraint. |
| 8 | Self-play task generation | SPIRAL, SvS, R-Zero | **Use** | A proposer can search near the solver frontier, exposing weaknesses that static training sets miss. |
| 9 | Test-time adaptation | TTRL, Absolute Zero Reasoner | **Defer** | Changes inference-time budget and adaptation rules. Relevant later, but separate from the offline training loop. |
| 10 | Prolonged RL | ProRL | **Use** | Tests whether gains emerge after apparent reward saturation rather than in short RLVR runs. |
| 11 | Diversity-preserving RL | SAGE, Bayesian Boundary Gating, Pass@k Training | **Use** | Directly addresses diversity collapse, a major threat to support-set expansion. |
| 12 | High-k objective design | Pass@k Training, Codex pass@k | **Use** | Aligns training and evaluation with high-sample discovery rather than only pass@1 sharpening. |
| 13 | Support expansion vs. sharpening | Self-Improvement Sharpening, On the Limits of Self-Improving in LLMs | **Use** | Supplies the central null hypothesis and the reason for per-problem support-set statistics. |
| 14 | Generation-verification separation | Mind the Gap, LLMs Cannot Self-Correct Reasoning Yet | **Use** | Justifies external checkers and rejects self-judged correctness as a primary reward. |
| 15 | Reward-hacking controls | Spurious Rewards | **Use** | Motivates random-reward, format-only, checker-B disagreement, and contamination audits. |
| 16 | Hindsight relabeling | Hindsight Experience Replay | **Reject** | Needs goal-conditioned trajectories and relabelable goals. Program-induction specifications are discrete and externally fixed. |
| 17 | Library learning | DreamCoder, LILO, Stitch | **Defer** | A plausible mechanism for transfer, but it should be tested after the base loop can measure support movement reliably. |
| 18 | Program compression | Stitch, DreamCoder | **Defer** | Supports later abstraction discovery and motif consolidation. Not required for Phase 0. |
| 19 | Open-ended environment generation | POET | **Defer** | Conceptually aligned with expanding capability, but v1 needs deterministic verification and low infrastructure cost. |
| 20 | Interestingness-guided curricula | OMNI | **Defer** | A useful curriculum direction once task generation is robust; not needed for toy program induction. |
| 21 | World-model loops | World Models, DreamerV3, Genie | **Defer** | Powerful but simulator fidelity and reward hacking dominate the support-set question at this budget. |
| 22 | Embodied instruction agents | SIMA-style agents | **Defer** | Relevant to generality, but task execution is too expensive and hard to verify for v1. |
| 23 | Intrinsic motivation | curiosity, learning progress, empowerment | **Defer** | Could become an exploration bonus, but not needed before deterministic reward baselines are established. |
| 24 | Multi-agent games | self-play and curriculum games | **Defer** | Could increase diversity, but adds attribution complexity beyond the proposer-solver loop. |
| 25 | Verifier-free judge rewards | learned reward models, LLM judges | **Reject** | Fails the grounded-verifier constraint and cannot cleanly distinguish correct from plausible outputs. |
| 26 | Continual adapters and replay | LoRA, QLoRA, PEFT-style adapters | **Use** | Practical weight-update mechanism for small compute. Replay controls help distinguish learning from data reuse. |
| 27 | Reasoning environments | Reasoning Gym, GURU | **Defer** | Useful task sources and transfer ladders; not required until the Python toy generator is replaced. |
| 28 | Cognitive behavior analysis | Cognitive Behaviors | **Defer** | Useful analysis layer for subgoaling/backtracking, but not a causal mechanism in v1. |
| 29 | ARC-style abstraction evaluation | ARC-AGI / On the Measure of Intelligence | **Use** | Motivates held-out, guess-resistant evaluation and skill-acquisition efficiency. |
| 30 | Public claims automation | claims-gated notebook | **Use** | Keeps reporting tied to ledger evidence and prevents unreviewed causal claims. |

## Summary

- **Use (12):** verified self-training, RLVR, self-play, prolonged RL,
  diversity-preserving RL, high-k objectives, support-set statistics,
  generation-verification separation, reward-hacking controls, adapters/replay,
  ARC-style evaluation, and claims gating.
- **Reject (5):** runtime scaffolds as the core mechanism, scaffold
  self-modification as the main object of measurement, automated research
  agents, hindsight relabeling for this task type, and verifier-free rewards.
- **Defer (13):** skill libraries, algorithm distillation, test-time
  adaptation, library learning, program compression, open-endedness, OMNI-style
  curricula, world models, embodied agents, intrinsic motivation, multi-agent
  games, reasoning environments, and cognitive-behavior analysis.

The design in [03 -- Current Design](03-current-design.md) uses the smallest
subset needed to answer the central question: do grounded recursive loops expand
the solver's support set beyond sharpening?

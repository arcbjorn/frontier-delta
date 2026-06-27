# 03 -- Current Design

## System Architecture

The system is a closed loop with explicit train/evaluation separation:

```
Task Proposal
  -> public training examples -> Checker A -> rewards -> training arm
  -> private held-out examples -> support-set evaluation -> Checker B audit
Solver Rollouts
  -> sandbox execution -> ledger -> analysis -> claims-gated notebook
```

Phase 0 implements this with toy tasks, a mock solver, subprocess execution, a
split-aware checker, reward functions, a mock trainer, pass@k estimation,
support-set classification, a ledger, arm configs, and a notebook stub. Later
phases replace the mock proposer and mock trainer with API task proposal and
real LoRA/GRPO training.

## Data Contract

Each task contains:

- `description`: natural-language task statement.
- `train_examples`: public examples used for reward and training.
- `test_examples`: held-out examples used only for evaluation/audit.
- `difficulty_band`: proposer-estimated difficulty label.
- `meta`: generation seed, function name, proposer metadata, and later hashes.

The checker can evaluate either split. Reward computation should use
`split="train"`. Support-set evaluation and checker-B audit should use
`split="test"`.

## Loop Stages

### 1. Task Proposal

Phase 0 uses `generate_toy_tasks` to create deterministic Python
program-induction tasks. Phase 1 replaces that with a frozen frontier proposer
that generates tasks, reference solutions, estimated difficulty, and diversity
metadata.

### 2. Solver Rollouts

Phase 0 uses a mock lookup-table solver. Real phases use a small trainable model
(1-8B parameters) that samples `k` candidate Python functions per task. Each
candidate must define `solve(...)`.

### 3. Sandbox

Candidates are executed in a subprocess with a timeout. This is suitable for
trusted toy tests only. Any untrusted model-generated code requires Docker,
nsjail, E2B, or equivalent isolation.

### 4. Checker A

Checker A is deterministic and grounded in task examples:

- Train split: reward signal.
- Test split: held-out evaluation.

It does not call a learned judge. This is the main defense against reward
hacking and self-verification failures.

### 5. Rewards and Arms

Each arm isolates one causal claim:

| Config | Arm | Reward / intervention | What it tests |
|--------|-----|-----------------------|---------------|
| `vanilla_rlvr.yaml` | Vanilla GRPO/RLVR | Verified training-split correctness | Whether standard RLVR expands support. |
| `prolonged_rl.yaml` | Prolonged RL | Verified correctness with extended training | Whether gains emerge after saturation. |
| `exploration_preserving.yaml` | Exploration-preserving | Correctness plus diversity pressure | Whether diversity preservation is necessary. |
| `main_selfplay.yaml` | Self-play | Frontier proposer against solver frontier | Whether moving tasks force broader capability. |
| `star_self.yaml` | STaR/ReST SFT | SFT on verified-correct samples | Whether filtering plus SFT is enough. |
| `distillation.yaml` | Distillation | Frontier-output transfer objective | Whether gains are imitation rather than recursion. |
| `random_reward.yaml` | Random reward | Seeded random binary reward | Negative control for arbitrary feedback. |
| `format_only.yaml` | Format-only reward | Valid Python syntax only | Negative control for format incentives. |
| `no_frontier_replay.yaml` | No-frontier replay | Solver-only replay source | Whether frontier-proposed data is necessary. |
| `library_frozen.yaml` | Library frozen | Fixed function library | Whether library growth is the mechanism. |
| `library_shuffled.yaml` | Library shuffled | Semantically broken library | Whether library structure matters. |
| `library_random.yaml` | Library random | Random library-shaped context | Whether any library-like context helps. |

### 6. Trainer

Phase 0 has no real training. The mock trainer path records the statistics that
real GRPO + LoRA training would consume. Phase 2 replaces this with a small
solver, LoRA/QLoRA adapters, batched rollout generation, and actual optimizer
steps.

### 7. Support-Set Evaluation

For each task and round, the evaluator samples many solver outputs and records:

- `n_samples`: candidates sampled.
- `c_correct`: candidates passing held-out tests.
- `pass@k`: unbiased estimator from Chen et al.
- `p_solve`: Phase 0 smoothed beta-binomial point estimate.
- `label`: gained, lost, sharpened, or unchanged.

The research target is full posterior classification with credible intervals.
Phase 0 intentionally implements only the lightweight point-estimate version so
the loop remains dependency-free.

### 8. Checker B

Checker B is an independent audit verifier planned for Phase 3. It should rerun
held-out examples with independent isolation, report disagreement with Checker A,
and flag suspicious candidates. Phase 0 records the ledger fields needed for
checker-B disagreement but does not yet implement a separate sandbox backend.

### 9. Ledger and Notebook

The ledger stores one row per task, round, and arm. The notebook reads ledger
data into local Markdown/HTML. It never publishes automatically; every claim
must be reviewed and tied to a query over recorded evidence.

## Metrics

### Primary

- **pass@1, pass@8, pass@64, pass@256, pass@1024:** average task success
  probability under the unbiased pass@k estimator.
- **Per-problem solve probability:** Phase 0 point estimate; later posterior
  mean and credible interval.
- **Support-set movement:** counts and identities of gained, lost, sharpened,
  and unchanged tasks.

### Secondary

- **Support-set transfer map:** task-by-task movement across rounds and arms.
- **Diversity:** AST edit distance, entropy, and distinct solution forms.
- **Verifier disagreement:** checker-A versus checker-B discrepancy.
- **Cost:** tokens, wall-clock time, and GPU-hours per arm.

### Tertiary

- **Difficulty-band breakdown:** movement stratified by estimated difficulty.
- **Library utilization:** calls to learned or provided library functions.
- **Round drift:** changes in solver output distribution across training.

## Statistical Framework

For each task `i`, the target model is:

- latent solve probability `theta_i ~ Beta(alpha, beta)`;
- observed solves `s_i ~ Binomial(k_i, theta_i)`;
- posterior `theta_i | s_i, k_i ~ Beta(alpha + s_i, beta + k_i - s_i)`.

Phase 0 uses the posterior mean proxy:

```
p_solve = (c + 0.5) / (n + 1.0)
```

Classification uses the same conceptual thresholds as the target design:

- unsolvable if `p_solve < epsilon`;
- solvable if `p_solve > 1 - epsilon`;
- gained if unsolvable becomes solvable;
- lost if solvable becomes unsolvable;
- sharpened if solvable remains solvable and improves by `delta_min`;
- unchanged otherwise.

Later phases should replace the point-estimate boundary with posterior
probability thresholds and multiple-comparison-corrected arm comparisons.

## Argument Structure

The experiment is interpretable only if controls behave correctly:

- Treatment arms should show expansion only if the mechanism works.
- Random and format-only controls should not show expansion.
- Checker-B disagreement should remain low for reported gains.
- Held-out tasks must remain unseen by training and proposer feedback.

The central result is not "the model got better." It is a support-set transfer
claim: which tasks moved, under which arm, with which verifier agreement, and
against which controls.

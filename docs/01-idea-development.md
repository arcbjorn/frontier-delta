# 01 -- Idea Development

## What This Project Is

Frontier Delta is a small-compute research system for testing whether
recursive language-model training loops expand a model's *support set* -- the
set of problems it can solve with nontrivial probability -- or merely sharpen
performance on problems already inside that support.

The project does not claim to build AGI. It builds a measurement instrument:
task generation, solver rollouts, verifiable rewards, control arms, per-problem
statistics, and a claims-gated reporting layer.

## Core Research Question

Many reported self-improvement results can be explained by sharpening:
pass@1 improves because the model samples better answers for tasks it could
already solve sometimes. The harder claim is support-set expansion: after a
recursive loop, the model reliably solves tasks whose base solve probability was
near zero.

That distinction drives the entire design. Aggregate benchmark scores are not
enough. The project tracks each problem independently, estimates solve
probability from repeated samples, and classifies movement as gained, lost,
sharpened, or unchanged.

## How the Idea Evolved

### 1. Orchestration Was Not Enough

The broad starting point was a self-improving agent with memory, reflection,
tool use, and a persistent skill store. Generative Agents, ReAct, Reflexion, and
Voyager show that memory, action scaffolds, and verbal reflection can improve
agent behavior. Darwin Godel Machine and AlphaEvolve show stronger versions of
code/tool evolution under evaluator feedback.

The constraint that changed the direction was measurement: if the model weights
do not change, improved behavior can usually be attributed to better
orchestration, search, memory retrieval, or runtime instructions. Those are
important baselines, but they do not by themselves show support-set expansion of
a trainable solver. The project therefore treats scaffold-only systems as
runtime baselines or later infrastructure, not as the central mechanism.

### 2. Weight Updates Became Necessary

The next candidate mechanism was closed-loop self-training: generate candidate
solutions, keep the verified successes, and train the next solver on them. STaR,
ReST, SEAL, and Algorithm Distillation all support variants of this idea:
self-generated data can improve a model when the selection signal is useful.

This created the first hard requirement: every training example admitted into
the loop needs a grounded correctness signal. Without that, self-training can
amplify plausible mistakes.

### 3. The Verifier Bottleneck Narrowed the Domain

Work on self-correction and the generation-verification gap shows that models
are not reliable judges of their own reasoning. Spurious-reward studies show
that RL-trained models can exploit reward artifacts. Learned judges and
LLM-as-judge rewards are therefore inappropriate as the primary signal for this
project.

The domain narrowed to executable program induction: given input-output
examples, generate a Python function. Program induction is small enough for a
laptop prototype, naturally supports many samples per task, and has an
automatic verifier. ARC-style evaluation motivates the emphasis on abstraction
and held-out examples, while the Codex pass@k work supplies the sampling metric.

### 4. Support-Set Expansion Became the Metric

The key conceptual shift came from the sharpening-versus-expansion framing.
Self-Improvement Sharpening and work on the limits of self-improving LLMs make
the conservative null hypothesis explicit: recursive loops may mostly sharpen
existing capabilities.

Frontier Delta therefore tracks per-problem probability rather than only
aggregate success. A task can move between categories:

- **Gained:** near-zero base solve probability, high post-loop solve probability.
- **Lost:** high base solve probability, near-zero post-loop solve probability.
- **Sharpened:** already solvable, then solved more reliably.
- **Unchanged:** no meaningful movement.

This makes the support-set transfer map the central artifact rather than a
single benchmark number.

### 5. Self-Play Suggested a Stronger Loop

Static self-training can saturate quickly. Self-play and recursive-reasoning
papers such as SPIRAL, Absolute Zero Reasoner, R-Zero, and SvS suggest a richer
loop: a proposer generates tasks near the solver's frontier, the solver attempts
them, and the verifier supplies grounded feedback. TTRL is related but changes
test-time adaptation rather than the offline training loop, so it is deferred.

The current design therefore separates a frozen proposer from a trainable
solver. The proposer can be upgraded from a mock toy generator to a frontier API
while the solver remains the object being measured.

### 6. Exploration Preservation Became a Treatment Arm

A pure RLVR loop can collapse diversity. If the policy narrows to a small set of
high-reward patterns, it may improve pass@1 while losing the ability to discover
new solutions. ProRL, Pass@k Training, SAGE, Bayesian Boundary Gating, and
Transfer-Aware Curriculum work all point toward the same pressure:
keep exploration alive while optimizing correctness.

That is why the main treatment is not only "RLVR works" but "which kind of
RLVR works." The experiment includes vanilla RLVR, prolonged RL,
exploration-preserving rewards, self-play, STaR/ReST-style SFT, distillation,
and negative controls.

### 7. Libraries and Abstractions Were Deferred

DreamCoder, LILO, Stitch, and Voyager-style skill libraries suggest a plausible
mechanism for genuine transfer: learned reusable abstractions. This is closely
aligned with support-set expansion, but it adds a second object of study -- the
library itself -- before the base measurement instrument is validated.

The project therefore keeps library learning as Phase 5. Earlier phases include
library frozen, shuffled, and random controls so that later library gains can be
interpreted instead of assumed.

### 8. Open-Endedness and World Models Were Scoped Out of V1

POET, OMNI, World Models, DreamerV3, and Genie-style environment generation are
strong evidence that open-ended curricula can produce new behavior. They also
require environment infrastructure, simulator fidelity, and nontrivial safety
controls. In this project, those costs would obscure the support-set question.

The v1 environment is deliberately narrow: executable functions, deterministic
checks, and many samples. Open-endedness returns later only if the measurement
instrument is reliable.

### 9. The Current Idea

The current project is a controlled support-set experiment:

1. Generate program-induction tasks with public training examples and private
   held-out examples.
2. Sample many solver candidates per task.
3. Reward candidates on public training examples using Checker A.
4. Evaluate candidates on held-out examples using Checker A and audit with
   Checker B.
5. Train or simulate training under multiple experimental arms.
6. Estimate per-task solve probabilities and support-set movement.
7. Compare treatment arms against negative controls before making any claim.

## Constraints That Shape the Design

### Frozen Frontier APIs

The proposer can be a frontier model, but it is frozen. The measured object is
the smaller solver and its adapter state. This avoids attributing solver gains to
changes in an external model.

### Verifier Split Discipline

Public training examples can produce reward. Held-out examples are for
evaluation and independent audit. Mixing these roles contaminates the support-set
measurement, so the implementation now exposes explicit `train` and `test`
checker splits.

### Small Compute

The project must run on a laptop in Phase 0 and on a single consumer GPU in the
first real training phase. This favors LoRA/QLoRA, small solvers, short rollouts,
and mock components until the measurement loop is proven.

### Reward Hacking

Any non-grounded reward can be gamed. Random-reward, format-only, checker-B
disagreement, and contamination checks are included to catch false expansion
signals.

### Diversity Collapse

If training collapses sampling diversity, the model may look better at low k and
worse at high k. The experiment therefore tracks pass@k, AST diversity, entropy,
and support-set movement rather than only pass@1.

### Test Contamination

The holdout manifest exists to keep held-out examples from leaking into
training. Later phases should hash manifests, log access, and keep audit tasks
separate from proposer-visible tasks.

### Security

The current sandbox is a subprocess prototype for trusted toy tasks. Running
model-generated code requires Docker, nsjail, E2B, or equivalent isolation before
untrusted candidates are allowed.

### Claims Gating

The public notebook is local and human-gated. A result can be rendered only from
ledger data, and causal claims require preregistered comparisons against the
control arms.

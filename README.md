# Frontier Delta

A rigorous small-compute research system testing whether recursive self-improving LLM loops expand a model's support set or merely sharpen existing behavior.

**Status:** Phase 0 (Foundation) -- scaffold and mock loop.

**Research scope:** The research and development narrative is tied to
discoveries reviewed through the July 2026 cutoff. Papers, projects, or
benchmark results published after July 31, 2026 should be treated as new
evidence and evaluated before updating the design.

## Setup

```bash
# Clone
git clone <repo-url>
cd frontier-delta

# Create/update the locked uv environment.
uv sync

# Run tests
uv run python -m unittest discover -s tests -v

# Run proposer viability (mock, no GPU/network required)
uv run python scripts/00_proposer_viability.py
```

Phase 0 has no runtime dependencies beyond the Python standard library. `uv`
manages the local environment, Python version selection, and `uv.lock`.

## Current V1 Experiment

The mock loop runs on toy program-induction tasks. A mock proposer generates input-output examples for hidden functions (e.g., `lambda a, b: a + b`). A mock solver generates candidate Python functions. The sandbox executes them against held-out test cases. The verifier classifies each task as solved or unsolved, and the pass@k estimator produces unbiased solve rates. The ledger records per-problem solve counts, and the analysis module classifies tasks as gained/lost/sharpened/unchanged relative to baseline.

No real training happens in Phase 0 -- the mock trainer records what would be trained. This validates the full measurement pipeline before committing GPU resources.

## Architecture

```mermaid
flowchart TD
    subgraph TSK[Task Corpus]
        P["Frozen proposer<br/>future API; mock in Phase 0"]
        TR["Public train examples<br/>reward split"]
        HO["Private held-out examples<br/>evaluation split"]
        REF["Reference solution<br/>proposer/generated audit target"]
        P --> TR
        P --> HO
        P --> REF
    end

    subgraph ROLL[Solver Rollouts]
        S["Small solver model<br/>mock lookup table in Phase 0"]
        K["k sampled Python functions<br/>def solve(...)"]
        S --> K
    end

    subgraph VERIFY[Execution and Verification]
        SB["Subprocess sandbox<br/>prototype isolation only"]
        CTA["Checker A on train split<br/>reward signal"]
        CEA["Checker A on held-out split<br/>support-set eval"]
        CB["Checker B on held-out split<br/>independent audit"]
        K --> SB
        TR --> CTA
        HO --> CEA
        HO --> CB
        SB --> CTA
        SB --> CEA
        SB --> CB
    end

    subgraph TRAIN[Training Arms]
        RW["Rewards<br/>verified, random, format, diversity"]
        ARM["Arm config<br/>vanilla, self-play, ProRL, STaR/ReST, controls"]
        MT["Mock trainer<br/>GRPO + LoRA placeholder"]
        CTA --> RW
        ARM --> RW
        RW --> MT
        MT -->|future weight update| S
    end

    subgraph MEASURE[Measurement]
        PK["pass@k estimator<br/>Chen et al."]
        SS["Support-set classifier<br/>gained/lost/sharpened/unchanged"]
        LD["Ledger<br/>task x round x arm rows"]
        NB["Claims-gated notebook<br/>local render, human review"]
        CEA --> PK
        CEA --> SS
        CB --> SS
        PK --> LD
        SS --> LD
        LD --> NB
    end
```

### Loop Detail

1. **Task Proposal:** Frozen frontier model generates program-induction tasks with training examples and held-out test examples.
2. **Solver Rollouts:** Small trainable model generates k candidate Python functions per task.
3. **Sandbox / Checker A:** Candidates are executed against public training examples for rewards and held-out examples for evaluation.
4. **Rewards:** Configurable reward function -- binary correctness, diversity bonus, format-only, random, etc. -- assigned per experimental arm.
5. **Mock Trainer:** Records what a GRPO + LoRA training step would compute. In later phases, performs actual weight updates.
6. **Support-Set Eval:** Phase 0 uses a smoothed beta-binomial point estimate; later phases add posterior intervals. Tasks are classified as gained, lost, sharpened, or unchanged.
7. **Checker B:** Independent audit verifier checks for reward hacking, contamination, and disagreement with Checker A.
8. **Analysis / Ledger:** Accumulates per-round, per-arm statistics into a support-set transfer map.
9. **Claims-Gated Notebook:** Results rendered locally. Nothing posted without human review.

## Test Commands

```bash
# All tests
uv run python -m unittest discover -s tests -v

# Specific modules
uv run python -m unittest tests.test_passk -v
uv run python -m unittest tests.test_verifier -v
uv run python -m unittest tests.test_rewards -v
uv run python -m unittest tests.test_ledger -v

# Mock loop (no GPU/network)
uv run python scripts/00_proposer_viability.py
```

## Documentation

See [docs/](docs/) for:
- [Idea Development](docs/01-idea-development.md) -- rationale and constraints
- [Recursive Learning Map](docs/02-recursive-learning-map.md) -- taxonomy of approaches
- [Current Design](docs/03-current-design.md) -- full system design and experimental arms
- [Implementation Plan](docs/04-implementation-plan.md) -- phases, kill gates, compute budget
- [References](docs/05-references.md) -- linked bibliography

## License

Research code. License TBD.

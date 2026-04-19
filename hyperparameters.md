# Practical Hyperparameter Reference for ShinkaEvolve

This is a condensed guide covering the parameters you are most likely to tune.
For the full list see the [official documentation](https://sakanaai.github.io/ShinkaEvolve/configuration/).

### Parameter groups

| Group | Where | Description |
|-------|-------|-------------|
| **Task setup** | `EvolutionConfig` | Paths and the task system message — required for every run. |
| **Run budget** | `EvolutionConfig` | Hard limits on how long or how much a run can cost. |
| **Mutation LLMs** | `EvolutionConfig` | The LLM roster, temperature schedule, bandit selection, and meta-recommendation step. |
| **Novelty & rejection** | `EvolutionConfig` | Embedding-based duplicate detection that filters out insufficiently novel candidates for offspring generation. |
| **Population structure** | `DatabaseConfig` | Number of islands, archive size, and migration schedule. |
| **Parent & archive selection** | `DatabaseConfig` | How programs are sampled as parents for the next generation. |
| **Evaluation** | `evaluate.py` | Per-candidate evaluation budget: number of runs and parallel workers. |
| **Concurrency** | `ShinkaEvolveRunner` | Maximum parallel proposal and evaluation jobs. |
| **Patch mechanics** | `EvolutionConfig` *(advanced)* | Mix of diff / full-rewrite / crossover mutations. |
| **Prompt evolution** | `EvolutionConfig` *(advanced)* | Co-evolves the task system message alongside the programs. |
| **Dynamic islands** | `DatabaseConfig` *(advanced)* | Spawns new islands automatically when a population stagnates. |

---

## `EvolutionConfig`

These control the core evolutionary loop and the LLMs driving it.

| Parameter | Default | Group | What it does |
|-----------|---------|-------|--------------|
| `task_sys_msg` | `"You are an expert optimization and algorithm design assistant. Improve the program while preserving correctness and immutable regions."` | Task setup | **Task-specific system message** given to every mutation LLM. The single most impactful parameter — include domain knowledge, constraints, and directions to explore. |
| `init_program_path` | `'initial.py'` | Task setup | Path to the starting program. Must contain `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END` markers. |
| `results_dir` | `None` → `results_<timestamp>` | Task setup | Where databases and the best program are saved. |
| `num_generations` | `50` | Run budget | How many evolutionary generations to run. Start with 10–20 to sanity-check, scale up for serious runs. |
| `max_api_costs` | `None` | Run budget | USD budget ceiling. The run stops when cumulative API spend reaches this value. Set it to avoid surprise bills during long runs. |
| `llm_models` | GPT/Gemini defaults | Mutation LLMs | **List of models used for mutations.** Mix cheap fast models (e.g. Haiku, GPT-nano) with stronger ones. Must use `openrouter/` prefix when using OpenRouter keys. |
| `llm_kwargs` | `{'temperatures': [0.0, 0.5, 1.0], 'max_tokens': 16384}` | Mutation LLMs | Temperature schedule and token budget for mutation LLMs. Higher temperatures → more creative but noisier proposals. |
| `llm_dynamic_selection` | `'ucb'` | Mutation LLMs | Strategy for selecting which model to call next. UCB learns which models produce better programs over time. |
| `llm_dynamic_selection_kwargs` | `{'cost_aware_coef': 0.5}` | Mutation LLMs | Bandit configuration. `cost_aware_coef` balances program quality vs. API cost when ranking models. |
| `meta_llm_models` | same as `llm_models` | Mutation LLMs | Model(s) for the meta-recommendation step (generates high-level suggestions every `meta_rec_interval` generations). A reasoning model (e.g. o4-mini) works well here. |
| `meta_rec_interval` | `10` | Mutation LLMs | Generations between meta-recommendation steps. Lower = more frequent high-level guidance. |
| `embedding_model` | `'text-embedding-3-small'` | Novelty & rejection | Embedding model for code-similarity novelty checks. Must match your API provider. |
| `code_embed_sim_threshold` | `0.99` | Novelty & rejection | Embedding cosine-similarity threshold above which a candidate is rejected as a duplicate. Lower = stricter novelty enforcement. |
| `max_novelty_attempts` | `3` | Novelty & rejection | How many times to re-propose if a candidate is rejected for low novelty before accepting it anyway. |

---

## `DatabaseConfig`

These control the population structure and how programs are selected as parents.

| Parameter | Default | Group | What it does |
|-----------|---------|-------|--------------|
| `num_islands` | `2` | Population structure | Number of independent sub-populations. More islands = more diversity; try 2–4. Each island evolves somewhat independently and occasionally exchanges migrants. |
| `archive_size` | `40` | Population structure | Maximum number of elite programs kept globally. Larger archives preserve more diversity but slow down selection. |
| `migration_interval` | `10` | Population structure | Generations between island migrations. Lower = islands converge faster. |
| `parent_selection_strategy` | `'weighted'` | Parent & archive selection | How parents are sampled from the island population. `'weighted'` favours higher-scoring programs; `'uniform'` treats all equally. |
| `exploitation_ratio` | `0.2` | Parent & archive selection | Probability of drawing a parent from the global archive (vs. the island). Higher = more exploitation of the global best. |
| `exploitation_alpha` | `1.0` | Parent & archive selection | Sharpness of the power-law weighting when sampling parents. Higher = stronger preference for top scorers. |

---

## `LocalJobConfig`

These configure how evaluations are launched locally.

| Parameter | Default | What it does |
|-----------|---------|--------------|
| `eval_program_path` | `'evaluate.py'` | Path to your evaluation script. |
| `activate_script` | `None` | Path to a shell activation script (e.g. `.venv/bin/activate`). Required so subprocesses use the correct Python environment. |
| `time` | `None` | Timeout per evaluation job (`HH:MM:SS`). Useful if your evaluator can run indefinitely — set a budget (e.g. `'0:05:00'`). |

---

## Evaluation parameters

These are parameters for your `evaluate.py` script, not ShinkaEvolve itself. Since `evaluate.py` runs as a subprocess, they are passed via environment variables (set them in the launcher notebook before calling the runner). Otherwise, you can hard-code them in the `evaluate.py` file.

| Parameter | Default | What it does |
|-----------|---------|--------------|
| `NUM_RUNS` | `1` | How many independent runs to average per candidate. More runs = more reliable scores but slower evaluation. Useful when the program has randomness. |
| `NUM_WORKERS` | `1` | Parallel workers within a single evaluation. Set to the number of available CPU cores, but leave headroom for concurrent `max_evaluation_jobs`. |

> **Rule of thumb**: `NUM_WORKERS × max_evaluation_jobs` should not exceed your total CPU count.

---

## `ShinkaEvolveRunner`

Runner-level concurrency parameters, passed directly to `ShinkaEvolveRunner(...)`.

| Parameter | Default | What it does |
|-----------|---------|--------------|
| `max_proposal_jobs` | `1` | Maximum LLM calls running in parallel. Higher = faster throughput but more API cost. |
| `max_evaluation_jobs` | `2` | Maximum evaluations running in parallel. Match to your CPU/GPU budget. |

---

## Advanced parameters

The parameters below are less commonly tuned on a first pass but can matter for longer or more ambitious runs.

### `EvolutionConfig`

| Parameter | Default | Group | What it does |
|-----------|---------|-------|--------------|
| `patch_types` | `['diff', 'full', 'cross']` | Patch mechanics | Mutation formats available: `diff` (edit existing code), `full` (rewrite entirely), `cross` (crossover between two programs). |
| `patch_type_probs` | `[0.6, 0.3, 0.1]` | Patch mechanics | Sampling weights for each patch type. Increase `full` weight if the search is stuck in a local optimum. |
| `max_patch_attempts` | `1` | Patch mechanics | Retries when a generated patch is syntactically invalid. |
| `evolve_prompts` | `False` | Prompt evolution | Enable system prompt co-evolution. |
| `prompt_evolution_interval` | `None` | Prompt evolution | Generations between prompt updates (defaults to `meta_rec_interval` if `None`). |
| `prompt_archive_size` | `10` | Prompt evolution | Number of past prompts retained. |
| `prompt_llm_models` | same as `llm_models` | Prompt evolution | Models used for prompt mutation. |
| `prompt_ucb_exploration_constant` | `1.0` | Prompt evolution | UCB exploration strength for prompt selection. |

### `DatabaseConfig`

| Parameter | Default | Group | What it does |
|-----------|---------|-------|--------------|
| `enable_dynamic_islands` | `False` | Dynamic islands | Enable stagnation-triggered island creation. |
| `stagnation_threshold` | `100` | Dynamic islands | Generations without improvement before a new island is spawned. |
| `island_spawn_strategy` | `'initial'` | Dynamic islands | Seed source for the new island: `'initial'` restarts from the initial program; other options seed from existing programs. |

### `ShinkaEvolveRunner`

| Parameter | Default | What it does |
|-----------|---------|--------------|
| `max_db_workers` | `4` | Database worker threads in the runner. Rarely needs changing. |

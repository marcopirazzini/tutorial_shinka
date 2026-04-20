# Setting up ShinkaEvolve locally

---

**TODO(marcop, antaresc) - Refactor this part into this markdown file**

This notebook works is specific for the circle packing task, but it can serve as a blueprint for making other tasks. Start by creating a separate folder with the following ingredients:

1. `initial_program.py`: This must contain the generator code for your task inside the `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END` markers. Outside these you must add a `run_task()` function that returns the constructed object, its score, and possibly other statistics you might want to keep track of. You can also add any auxiliary functions you want here.
2. `evaluate.py`: This must contain a `validate_task(run_output)` function that must validate the correctness of the output of the `run_task()` function in the program of interest. It must also contain an `aggregate_metrics(results, results_dir)` function that returns a dictionary of evaluation metrics associated to the program. The most important one is `combined_score`, which is the score that is ultimately used to judge the quality of the program.
3. `shinka_launch.ipynb`: This one will be much closer to the current notebook, the only parameter that is task-specific is `TASK_SYS_MSG` in the `EvolutionConfig` instance. Another one I like to change is the name of the results databases, but it's not required. The visualization code at the end of this notebook is also specific for the circle packing task, but it is only used for a posteriori analysis of the solution found, not for running Shinka.

---

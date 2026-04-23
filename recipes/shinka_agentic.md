# Using ShinkaEvolve Agentically

AI driven coding agents have drastically changed how scientists and engineers approach programming. Tools like Claude Code vastly simplify learning to use new software packages, making the time it takes to use these packages in personal projects much shorter. This guide will provide a few workflows which use ShinkaEvolve through Claude Code.

The guide is divided into three parts.

-   Part 1 -

-   Part 2 -

-   Part 3 -

---

**TODO(marcop, antaresc) - Refactor this part into this markdown file**

## Agentic usage

We can Claude Code (or other coding agents such as Codex) to help generating new shinka tasks. This is particularly useful for a first pass at the `initial_program.py` and `evaluate.py` files, mostly to create a skeleton that we can refine manually. I recommend copying this notebook for the actual `ShinkaEvolveRunner`, but coding agents can be useful for adding some context to the `TASK_SYS_MSG` as well.

To see how this work, see the the [Github repo at this link](https://sakanaai.github.io/ShinkaEvolve/agentic_usage/). The main part is Sections 1-4, once the task is scaffolded we can just follow the instructions in this notebook for running the evolution and visualizing progress.

---

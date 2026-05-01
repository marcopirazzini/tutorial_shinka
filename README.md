# AI for Scientific Discovery 2026 Starter Package

> [!IMPORTANT]
> **(4/28/2026)** - Instructional accounts on Grace will be deleted after **Monday 5/4/2026**. Please make sure to offload any data you might have stored on these accounts as you will not have access after this date.
>
> Additionally, API keys for OpenRouter as well as enterprise access to Anthropic will be discontinued after **Friday 5/22/2026**.
>
> If you would like to use ShinkaEvolve, please see instructions found in [Setting up ShinkaEvolve locally](recipes/shinka_on_local.md). You will need to provision your own OpenRouter API key to use the notebooks in this repository. See also the [ShinkaEvolve Getting Started Guide](https://sakanaai.github.io/ShinkaEvolve/getting_started/).

This repository contains tutorial material used during the Yale FDS Workshop on [AI for Scientific Discovery](https://yalefds.swoogo.com/aiforscientificdiscovery/11264716). You will find a collection of Jupyter notebooks which use ShinkaEvolve for various tasks, as well as a collection of markdown guides that walk through various work flows involving ShinkaEvolve.

-   `recipes/` - This directory contains a collection of markdown guides which illustrate different ways to use ShinkaEvolve. It also contains guides on how to use ShinkaEvolve through [Claude Code](https://claude.com/product/claude-code) and how to access provisioned resources on [Grace](https://docs.ycrc.yale.edu/clusters/grace/), the high performance computing cluster managed by the [Yale Center for Research Computing](https://research.computing.yale.edu).

-   `circle_packing/` - This directory contains all files related to using ShinkaEvolve to solve Circle Packing.

-   `komlos/` - This directory contains all files related to using ShinkaEvolve to validate a lower bound to the Komlos conjecture

-   `qml_unitary_learning/` - This directory contains all files related to using ShinkaEvolve to find a quantum circuit which approximates a hidden 4-qubit unitary transformation subject to connectivity constraints.

-   `stellar_evo/` - This directory contains all files related to using ShinkaEvolve for finding a neural network architecture which interpolates evolutionary tracks of stars.


### References

References for ShinkaEvolve

-   [ShinkaEvolve Github repository](https://github.com/SakanaAI/ShinkaEvolve)

-   [ShinkaEvolve getting started instructions](https://sakanaai.github.io/ShinkaEvolve/getting_started/)

-   [ShinkaEvolve paper](https://arxiv.org/abs/2509.19349)

-   [ShinkaEvolve talk video](https://www.youtube.com/watch?v=dAOIer_1INo)

Stellar Evolution references

-   ([Hon, Li & Ong, 2024](https://arxiv.org/abs/2407.09427)) *Flow Based Generative Emulation of Grids of Stellar Evolutionary Models*

-   ([Ying et. al., 2025](https://arxiv.org/abs/2604.06348)) *Dartmouth Stellar Evolution Emulator (DSEE) 1: Generative Stellar Evolution Model Database*

-   ([Christensen-Dalsgaard, 2007](https://arxiv.org/abs/0710.3114)) *ASTEC -- the Aarhus STellar Evolution Code*

-   [Official MESA Documentation](https://docs.mesastar.org/en/26.4.1/about.html)

References to YCRC resources

-   [YCRC's Grace HPC cluster overview guide](https://docs.ycrc.yale.edu/clusters/grace/)

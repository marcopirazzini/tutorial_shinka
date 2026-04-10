# AI for Scientific Discovery 2026 Starter Package

This repository contains some tutorials which will help you get started with using ShinkaEvolve for the Yale FDS Workshop [AI for Scientific Discovery](https://yalefds.swoogo.com/aiforscientificdiscovery/11264716).

Some helpful links

-   [ShinkaEvolve Github repository](https://github.com/SakanaAI/ShinkaEvolve)

-   [ShinkaEvolve getting started instructions](https://sakanaai.github.io/ShinkaEvolve/getting_started/)


## Getting started with iPython notebooks using pip (Linux / Mac)

A simple way to start using ShinkaEvolve is through [iPython notebooks](https://ipython.org/ipython-doc/3/notebook/notebook.html). In this recipe we will set up a basic environment to do this.

**Prerequisites** - Before continuing make sure you have the following ready

-   Python version >= 3.11 installed locally on your machine


**Instructions** - To get started, we will first create a virtual environment to do our development in. Open a terminal, and navigate to where this repository is located. Then, do the following.

1.  Run `python -m venv .venv` to create a virtual environment named `venv`

2.  Activate the virtual environment by running `source .venv/bin/activate`

3.  Install Jupyterlab and ShinkaEvolve by running the following commands using `pip`.

    ```bash
    pip install jupyterlab
    pip install shinka-evolve
    ```

    You can verify your ShinkaEvolve installation is ready to go by running this command.

    ```bash
    python -c "from shinka.core import ShinkaEvolveRunner; print('OK')"
    ```

4.  Create a `.env` file containing your OpenRouter API key to the root of this repository. You can do this by running the following bash command.

    ```bash
    touch .env && echo 'OPENROUTER_API_KEY="<your-key-here>"' > .env
    ```

Once you've done this you're ready to go! Run `jupyter lab` to start the web UI for editing Jupyter notebooks, and try out the example in `/circle_packing/shinka_launcher.ipynb`.


## Getting started with iPython notebooks (Windows)

TODO




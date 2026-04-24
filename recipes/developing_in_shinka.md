# Developing in the ShinkaEvolve Repository

This guide will walk through how to set up your environment if you would like to **modify the implementation of ShinkaEvolve**. This guide has two parts.

-   Part 1. how to clone, and set up the ShinkaEvolve repository on Grace for editing.

-   Part 2. how to clone, and set up the ShinkaEvolve repository for editing on your local environment.

Some links that might help with this tutorial

-   [[link](https://docs.ycrc.yale.edu/clusters/grace/)] YCRC's Grace HPC cluster overview guide.

-   [[link](https://github.com/SakanaAI/ShinkaEvolve)] the official ShinkaEvolve Github repository

-   [[link](https://sakanaai.github.io/ShinkaEvolve/getting_started/)] Sakana AI's *Getting Started* guide for ShinkaEvolve.

-   [[link]](https://sakanaai.github.io/ShinkaEvolve/) ShinkaEvolve's official documentation site.

Before beginning **make sure you have the following**

-   You are already **logged on to Grace**. See [Setting up ShinkaEvolve on Grace](./shinka_on_grace.md) for instructions on how to do this.


---

## Part 1. Setting up ShinkaEvolve for development on Grace

To get started developing in the ShinkaEvolve repository, follow these steps.

1.  First, navigate to a directory which will hold the [ShinkaEvolve Github repository](https://github.com/SakanaAI/ShinkaEvolve). This tutorial will be using `~/project`

2.  Clone the repository by running the command

    ```bash
    git clone https://github.com/SakanaAI/ShinkaEvolve
    ```

    ![shinka clone](assets/grace_clone.png)

3.  Change to the `ShinkaEvolve` directory containing your freshly cloned repository.

    ```bash
    cd ShinkaEvolve
    ```

4.  Create a **virtual environment** using Conda

    ```bash
    conda create --name shinka_dev python=3.11 uv nodejs notebook
    ```

    Virtual environments are helpful for enforcing *isolation*, e.g. they help prevent software dependency conflicts between different coding projects.

    ![shinka conda](assets/grace_conda1.png)

    After the virtual environment has been created, you will see instructions to activate it.

    ![shinka conda 2](assets/grace_conda2.png)

    **NOTE (!)** - In this step, we are creating a new Conda environment. This is different from the `shinka_ai4sd26` Conda environment that YCRC has made available with tools like ShinkaEvolve already installed. If would like to just use ShinkaEvolve as a tool, see [Using ShinkaEvolve through Jupyter Notebooks](./shinka_via_jupyter.md)

5.  Activate your new Conda virtual environment

    ```bash
    conda activate shinka_dev
    ```

    and install all project dependencies

    ```bash
    uv pip install -e .
    ```

6.  Create an `.env` file at the root of the cloned repository. This file will contain your [OpenRouter](https://openrouter.ai/) API key.

    ```bash
    touch .env && echo 'OPENROUTER_API_KEY="<your-key-here>"' > .env
    ```

    **Having this API key is important (!)**. This key is **uniquely assigned** and is what allows ShinkaEvolve to query different Large Language Models as it executes evolutionary search for your task.

    You should have been assigned an API key for this workshop, contact the organizers if you cannot find it.

7.  Once you've added your API key, you're now ready to develop in the ShinkaEvolve repository. You can test that you've set up your environment properly by **checking if the help text for `shinka_launch`** properly displays.

    ```bash
    shinka_launch --help
    ```

    **NOTE (!)** - Running `shinka_launch` by itself will run ShinkaEvolve with a default evolution task. The default task requires an OpenAI API key instead of an OpenRouter API key. For more information, see ShinkaEvolve's documentation on [using OpenRouter models](https://sakanaai.github.io/ShinkaEvolve/support_local_models/?h=openrouter).


# Part 2. Setting up ShinkaEvolve for development locally

Here are some instructions on how to get started with editing the implementation of ShinkaEvolve. Here, you will want to find a suitable location on your machine where you can setup a simple development environment. Once you've navigated to there, **clone the ShinkaEvolve Github repository**.

```bash
git clone https://github.com/SakanaAI/ShinkaEvolve
```

Now **change into the ShinkaEvolve directory**.

```bash
cd ShinkaEvolve
```

Once you're in the ShinkaEvolve directory, **create a virtual environment**.

```bash
uv venv --python 3.11
```

and **activate** the environment

```bash
source .venv/bin/activate
```

This is where *isolation* is helpful! You may have already installed the version of ShinkaEvolve that is a package that is *available through Python package manager indices* like that on `uv` or `pip`. So, if this package was installed *globally* on your machine, then perhaps you might edit the implementation, and hope to run ShinkaEvolve your edited version. But by default, your machine will first execute the *globally* installed one that does not have your implementation changes.

Tell your new virtual environment to *install the version that you're editing* by running this command

```
uv pip install -e .
```

Now you should be able to change the implementation and test your changes. If you want to check that you're running the version of ShinkaEvolve that is implemented in your current directory, you can run the command

```bash
python -c "import shinka; print(shinka.__file__)"
```

The output should point to `ShinkaEvolve/shinka/__init__.py`

![ShinkaEvolve help text](assets/shinka_repo_path.png)

When testing out your local implementation of ShinkaEvolve, you will want to use ShinkaEvolve through scripting. See the documentation on [CLI usage](https://sakanaai.github.io/ShinkaEvolve/cli_usage/) for more information.

To test the code in this repository on different evolution tasks, you will need to make sure there is a `.env` file in the root of the ShinkaEvolve directory. As before, this file will contain your [OpenRouter](https://openrouter.ai/) API key.

```bash
touch .env && echo 'OPENROUTER_API_KEY="<your-key-here>"' > .env
```

**Having this API key is important (!)**. This key is **uniquely assigned** and is what allows ShinkaEvolve to query different Large Language Models as it executes evolutionary search for your task. You should have been assigned an API key for this workshop, contact the organizers if you cannot find it.

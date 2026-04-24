# Claude Code

This guide will discuss [Claude Code](https://www.anthropic.com/product/claude-code), an **agentic coding tool** that can be used in your local programming environment through a terminal or IDE. It is an AI-powered development assistent that can *autonomously* plan and execute multi-step programming tasks. What makes it *agentic* is the fact that it acts in a loop. Through a chat interface, the developer uses *natural language* to prompt Claude Code with questions, or assign development tasks. Claude code then performs appropriate actions to either answer the prompt or execute the task. Feedback is then provided to the user through the same chat interface.

This tutorial is split into two steps

-   Step 1 - how to **install Claude code**

-   Step 2 - how to **setup Claude code** for first time use

Some links that might help with this tutorial

-   [[link](https://code.claude.com/docs/en/overview)] The official Claude code documentation overview

-   [[link](https://code.claude.com/docs/en/quickstart)] The official Claude Code quickstart guide

-   [[link](https://docs.ycrc.yale.edu/clusters/grace/)] YCRC's Grace HPC cluster overview guide.

-   [[link](https://sd26.ycrc.yale.edu/)] The Open OnDemand portal for Grace nodes specially provisioned for this workshop.

Before beginning **make sure you have the following**

-   A **Claude account** with a **Claude Pro, Max, Team or Enterprise subscription**. If you did not have a subscription prior to the event, you will have been added to an FDS enterprise subscription!

-   If you are using the Grace HPC cluster, make sure you have your **Yale NetID** and **password**

---

## Step 1: Installing Claude Code

How you install Claude Code will depend on what system you are working on. This part of the tutorial is split between two environments.

-   Mac / Linux

-   Yale's Grace HPC cluster


### On Mac / Linux

If you are using a Mac / Linux, navigate to your terminal, and run the following command

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

This will download and run the **native installation package** for Claude Code.


##### Alternative Route - Mac if you're using homebrew

[Homebrew](https://brew.sh/) is a widely used package manager for macOS. If you prefer to install Claude Code through homebrew, then use this command

```bash
brew install --cask claude-code
```

This replaces the `curl` command used to download the native installation package.


### On Grace

Claude has already been installed in your Grace account. So, to begin, start by accessing Grace

1.  Navigate to YCRC's **[Open OnDemand](https://sd26.ycrc.yale.edu/)** page for the specially provisioned instance of Grace for this workshop. Make sure your user ID takes the form `sd26_<netid>`. Note that this is a **different from the standard ood link for Grace** and it is specific for this workshop.

    ![Check user profile](assets/grace_landing.png)

2. Click on **Interactive Apps >  Remote Desktop** to launch a remote desktop session.

    ![Click on Remote Desktop](assets/grace_remotedesktop.png)

3.  You will be brought to a page for requesting a *compute node*. YCRC has provisioned every registered attendee with priority access to nodes on Grace.

    - Select your *Number of hours* to be `6`. Note that resources will be available until 8pm on 4/24, so request at most 20-[current time] hours.
    - Select your *Number of CPU cores per node* to be `6`
    - Select your *Memory per CPU code* to be `7`
    - Select your *Partition* to be `day` **This is important (!)**
    - Under *Reservation (optional)*, type `--reservation=sd26`. This will give priority to your request.

    ![Request resources for a compute node on Grace](assets/grace_request.png)

4.  Click `Launch` and wait briefly until the compute node is provisioned. Once the node is provisioned, click `Launch Remote Desktop`. *If the wait takes particularly long, please flag down an event organizer*

    ![When your desktop environment is ready, click launch](assets/grace_launch.png)

---

## Step 2: Using Claude Code for the first time

For this part of the tutorial, we will use this repostitory `tutorial_shinka` as our working directory. This Github repository has **already been cloned** into your home directory at the path `~/project/tutorial_shinka`. **Change to this directory** to get started.

```bash
cd ~/project/tutorial_shinka
```

For security purposes, Claude Code *can only access contents* in the directory tree rooted at the path you start Claude Code in. To start Claude Code, run this command inside `tutorial_shinka`

```bash
claude
```

Since this will be your first time opening Claude Code, some setup is required. First, **authenticate with your Anthropic account**

-   Select `Claude account with subscription`.

    ![Click Claude account with subscription](assets/claude_login_terminal.png)

This will bring you to a website. **Login to your anthropic account** with a Claude Pro, Max, Team or Enterprise subscription. If you did not have a subscription prior to the event, Anthropic will have emailed you a request to join the **Yale FDS** enterprise organization. Make sure you have followed the instructions to join.

![Login to your Claude account](assets/claude_login_web_0.png)

If you joined the Yale FDS organization, you will need to select this organization when authenticating with anthropic.

Anthropic will ask to connect Claude Code to your Claude Chat account. **Click `accept`**

![Connect Claude chat to Claude Code](assets/claude_login_web_1.png)

Once you've successfully logged in, you may close the browser window and verify in your terminal that you've been properly authenticated. Your terminal should say `Login successful`

![Success!](assets/claude_login_success.png)

If you are starting for the first time, Claude Code will ask permissions to access your work space. **Select `Yes, I trust this folder`**

![Trust me](assets/claude_login_trust.png)

And now you are ready to get started!

![Evolve!](assets/claude_start.png)

---

## Using ShinkaEvolve Agentically

Now that you have Claude Code enabled on your system, try using some of Claude Code's agentic coding capabilities.

-   Try working through the official tutorial on using ShinkaEvolve agentically [[link](https://sakanaai.github.io/ShinkaEvolve/agentic_usage/)]

A few suggestions to make Claude Code work much better with ShinkaEvolve when working with the environments used in this workshop:

-   By default, Claude Code will look for a `.venv` file for Python environments, so if you are using Conda make sure to specify that and what is the name of the Conda environment (e.g. `shinka_ai4sd26`)

-   By default, Claude Code will set up ShinkaEvolve experiment usign `OPENAI_API_KEY`. If using OpenRouter, it helps to specify that you don't have an OpenAI key but an OpenRouter one, and to use the notebooks in this repo as a template for which LLMs to query.

-   Also make sure to specify that you want the agentically created Shinka experiments to be stored in a new folder.

-   If you would like to use Claude to create a ShinkaEvolve run for Circle Packing, try out this prompt.

    ```
    Please scaffold an experiment in ShinkaEvolve using shinka-
    setup and shinka-run. My task consists in finding 26
    disjoint circles fully contained in the unit square with
    the goal of maximizing their sum of radii. Save the
    initial_program.py and evaluate.py files in a folder called
    "circle_packing_cc" and immediately start the evolution
    when everything is ready. Note also that this is being run
    in a Conda environment “shinka_ai4sd26” which already has
    shinka-evolve installed as a Python package.
    ```

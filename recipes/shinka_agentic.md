# Using ShinkaEvolve Agentically


Please refer to the main guide on the ShinkaEvolve tutorial: https://sakanaai.github.io/ShinkaEvolve/agentic_usage/

---

A few suggestions to make Claude Code work much better with ShinkaEvolve when working with the environments used in this workshop:
- By default, Claude Code will look for a `.venv` file for Python environments, so if you are using Conda make sure to specify that and what is the name of the Conda environment (e.g. `shinka_ai4sd26`)
- By default, Claude Code will set up ShinkaEvolve experiment usign `OPENAI_API_KEY`. If using OpenRouter, it helps to specify that you don't have an OpenAI key but an OpenRouter one, and to use the notebooks in this repo as a template for which LLMs to query.
- Also make sure to specify that you want the agentically created Shinka experiments to be stored in a new folder.
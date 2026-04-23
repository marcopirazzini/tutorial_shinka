# How to get your own API keys

ShinkaEvolve queries LLMs to generate mutations for the programs, and as such requires the user to have an API key (or multiple API keys). The Institute for Foundations of Data Science is generously providing API keys to the participants of this workshop, but after today each user will need their own API key to keep using ShinkaEvolve, and this is a guide for getting one.

One can obtain an API key directly from all major LLM providers, such as OpenAI (GPT), Google (Gemini), Anthropic (Claude), Alibaba (Qwen), Deepseek, xAI (Grok) etc. However, many of these keys will only work for the proprietary models of those providers, for example an OpenAI key can be used to query ChatGPT, and an xAI key can be used to query Grok, but not vice-versa.

# OpenRouter

One of the most important features of ShinkaEvolve is its ability to pool together knowledge across multiple LLMs by stacking together mutations coming from different models. Having an API key for each provider can be cumbersome, so we highlight a unified alternative.

[OpenRouter](https://openrouter.ai/) is an aggregator of most providers/models, and can be used to access all of them through a single API key. The "cons" are a very small latency and price markups relative to having a key and an account with each provider, but the convenience is a big pro.

OpenRouter also offers access to some free models, but the more powerful models come at a cost. However, the most expensive models are not always the best models for ShinkaEvolve tasks, and a combination of powerful and cheap models is usually better. 

Note that OpenRouter is not the only option for using multiple LLM providers, it is just the one we chose for this workshop.

## A small list of LLMs out there

For ShinkaEvolve, a good starting point is given by the LLMs used in the notebooks, and here we provide a reference list for playing around with different models.

Prices are per million tokens (input / output). Check [openrouter.ai/models](https://openrouter.ai/models) for the most up-to-date pricing.

### Budget 

| Model ID | Input $/M | Output $/M |
|---|---|---|
| `qwen/qwen3.5-flash` | $0.07 | $0.26 |
| `openrouter/openai/gpt-5.1-codex-mini` | $0.10 | $ 2.00 |
| `mistralai/mistral-small-2603` | $0.15 | $0.60 |
| `openai/gpt-5.4-nano` | $0.20 | $1.25 |
| `google/gemini-3.1-flash-lite-preview` | $0.25 | $1.50 |

### Mid-range 

| Model ID | Input $/M | Output $/M |
|---|---|---|
| `openai/o4-mini` | $0.35 | $4.40 |
| `google/gemini-3-flash-preview` | $0.50 | $3.00 |
| `openai/gpt-5.4-mini` | $0.75 | $4.50 |
| `qwen/qwen3-max-thinking` | $0.78 | $3.90 |
| `openai/gpt-5.2-codex` | $1.75 | $14.00 |

### Premium 

| Model ID | Input $/M | Output $/M |
|---|---|---|
| `google/gemini-3-pro-preview` | $2.00 | $12.00 |
| `openai/gpt-5.4` | $2.50 | $15.00 |
| `anthropic/claude-sonnet-4-6` | $3.00 | $15.00 |



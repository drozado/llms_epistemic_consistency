# Epistemic Consistency in LLMs

Code for the paper **"Beyond Viewpoint Affinity: Measuring Political Bias in LLMs as a Failure of Epistemic Consistency"** (under review).

This repository contains all experiment code, prompt templates, and analysis notebooks used to measure whether large language models apply consistent evidentiary standards when substantively equivalent evidence is paired with different political cues.

Stimulus data and prompt templates are also available as a dataset record:
**[https://huggingface.co/datasets/drozado/llms_epistemic_consistency](https://huggingface.co/datasets/drozado/llms_epistemic_consistency)**

The Hugging Face dataset has its own dataset-card `README.md`, Croissant metadata, prompt catalog, data inventory,
and source-provenance tables, separate from this code repository README.

Experimental results are saved as CSV files under `experimental_results/` (standard condition) and `experimental_results_strict/` (strict-exclusion condition). This data is  available as a Zenodo record: **[https://doi.org/10.5281/zenodo.20033482](https://doi.org/10.5281/zenodo.20033482)**
---

## Overview

We study two complementary families of experiments:

**Non-political-domain experiments** — Models evaluate stimuli with largely no political content (mathematical proofs, code, logical arguments, academic abstracts, judicial opinions, moral scenarios, etc.). Political cues are injected by attributing the stimulus to a randomly generated person with a stated political identity. Any difference in model ratings across left- and right-attributed stimuli reveals a person-attribution bias.

**Political-domain experiments** — Models evaluate stimuli that already carry political connotations (news articles from partisan outlets, policy proposals attributed to parties, societal trend data interpreted by ideologically aligned think tanks, etc.). Bias is measured by comparing ratings across left- and right-coded variants of the same content.

Models are queried across providers: **OpenAI, Anthropic, Google, xAI, and TogetherAI**.

---

## Setup

Requires Python 3.10+. Install the package and dependencies:

```bash
pip install -e .
pip install -r requirements.txt
```

Create a `.env` file at the project root with your API keys:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
XAI_API_KEY=...
TOGETHER_AI_API_KEY=...
```

---

## Repository Structure

```
vpei/                          # Python package (all source code)
  models.py                    # Model registry (clients, parameters)
  common_variables.py          # Shared constants and political attitude categories
  common_utils.py              # Parsing and utility functions
  statistical_tests.py         # t-tests, z-tests, sample size estimation
  utils/
    llm_requests_v3.py         # Async LLM request layer (any-llm, tenacity retries)
    llm_utils.py               # CSV saving, seed computation, helpers
  epistemic_consistency/
    experiment_types.py        # Core experiment runner functions
    experiments_configure.py   # Experiment parameter configuration
    prompts.py                 # Prompt templates and system prompts
    prompts_strict.py          # Strict-exclusion prompt variant
    active_prompts.py          # Selects which prompt module is active
    results_utils.py           # Result loading and statistical analysis
    experiment_utils.py        # Runtime helpers (printing, name generation)
    academic_abstracts/        # Experiment category
    art/                       # Experiment category (image inputs)
    code/                      # Experiment category
    cvs/                       # Experiment category
    factual_vs_false_statement_detection/
    judicial_decisions/
    logical_reasoning/
    math_proofs/
    moral_reasoning/
    physics_problems/
    evaluate_governments_based_on_country_metrics/
    evaluate_factuality_of_news_articles/
    evaluate_correlation_btw_governments_and_problem_metrics/
    evaluate_policy_effectiveness_given_contingency_tables/
    evaluate_policy_proposals/
    evaluate_protesters_behavior/
    evaluate_research_designs/
    evaluate_social_media_posts/
    evaluate_time_series_trends/
    evaluate_two_group_comparison_policy_effectiveness/

notebooks/                     # Jupyter notebooks (analysis pipeline)
```

---

## Running Experiments

Experiments are run through Jupyter notebooks using [papermill](https://papermill.readthedocs.io/) for parameterized execution.

| Notebook | Purpose |
|---|---|
| `_1-0 experiments_run.ipynb` | Absolute and comparative (non-political-domain) experiments |
| `_1-1 experiments_run evaluate.ipynb` | Political-domain (`evaluate_*`) experiments |
| `_1-2 experiments_run debiasing prompts.ipynb` | Centrist and epistemically-rigorous system prompt variants |
| `_1-3 experiments_run reasoning.ipynb` | Varying reasoning effort levels |
| `_1-4 experiments_run prompts_strict.ipynb` | Strict-exclusion prompt condition |

Results are saved as CSV files under `experimental_results/` (standard condition) and `experimental_results_strict/` (strict-exclusion condition).

---

## Analysis Notebooks

| Notebook | Purpose |
|---|---|
| `_2-1 results person-attribution experiments.ipynb` | Summary matrices for non-political-domain results |
| `_3-1 results politicized-context experiments.ipynb` | Summary matrices for political-domain results |
| `_4-2 create bias ranking new.ipynb` | Overall bias rankings across models |
| `_4-3 correlation analysis.ipynb` | Reliability (Cronbach's α) and correlation with external benchmarks |
| `_6-1 plot debiasing system prompts.ipynb` | Effects of politically-oriented system prompts |
| `_6-2 plot reasoning effort experiments.ipynb` | Effects of reasoning effort on bias |
| `_7-1 plot explicit exclude prompts_strict results.ipynb` | Results under explicit-exclusion prompting |
| `_9-1 create paper figures.ipynb` | Generates all paper figures via papermill |

External benchmark data (LM Arena Elo ratings, Epoch AI ECI scores) is fetched and mapped via notebooks under `notebooks/external_benchmarks/`.

---

## Experiment Types

**Non-political-domain categories** support five experiment types:

- **Absolute** — Model scores each item in isolation; each stimulus is evaluated under both left- and right-wing attribution labels.
- **Comparative with ground truth** — Model picks the correct item from a pair (one correct, one wrong), with political attribution counterbalanced across positions.
- **Comparative without ground truth** — Model picks the better of two correct items.
- **Multiple choice with ground truth** — Model picks 1 correct item from N options.
- **Multiple choice without ground truth** — Model picks 1 from N valid items.

**Political-domain categories** use a single experiment type:

- **Unblind** — Model rates stimuli that already contain political framing (partisan sources, party labels, ideologically aligned institutions); left/right balance is maintained in the stimulus dataset.

---

## Prompt Conditions

Two prompt modules define the experimental conditions:

- **`prompts.py`** (default) — Standard prompts presenting the stimulus with political cues.
- **`prompts_strict.py`** — Every system prompt adds an explicit instruction to disregard specific political information (e.g., "Ignore the article source", "Ignore the party affiliation"). Tests whether bias persists under explicit exclusion instructions.

To switch conditions, edit the import in `vpei/epistemic_consistency/active_prompts.py`.

---

## Statistical Analysis

- **Non-political-domain absolute experiments**: paired t-test (each stimulus evaluated under both labels, Cohen's d from paired differences).
- **Non-political-domain comparative experiments**: one-sample z-test against 0.5 (Cohen's h).
- **Political-domain unblind experiments**: independent Welch's t-test (left/right stimuli are distinct dataset rows).

Multiple testing correction is applied where appropriate. See `vpei/statistical_tests.py` and `vpei/epistemic_consistency/results_utils.py`.

---

## License

Code: [MIT License](LICENSE)

Stimulus data: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) - consult `dataset/metadata/source_datasets.csv` for provenance and licensing of individual components before redistribution.

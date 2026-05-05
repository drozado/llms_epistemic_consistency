
import pandas as pd
import os
import math
import numpy as np
from pathlib import Path
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
import scipy.stats as stats
from vpei.epistemic_consistency.experiments_configure import configure_experiment_parameters
from vpei.common_variables import EXPERIMENTS_WEIGHTS_FOR_OVERALL_BIAS_RATING
from vpei.epistemic_consistency.experiment_utils import ensure_comparative_columns

DEFAULT_EXPERIMENTAL_RESULTS_PATH = str(Path(__file__).resolve().parents[2] / 'experimental_results')


def _absolute_stats_payload(
    left_mean=np.nan,
    right_mean=np.nan,
    difference_in_means=np.nan,
    cohens_d=np.nan,
    t_statistic=np.nan,
    p_value=np.nan,
    odds=np.nan,
    log_odds=np.nan,
):
    return {
        "left_mean": left_mean,
        "right_mean": right_mean,
        "difference_in_means": difference_in_means,
        "cohens_d": cohens_d,
        "absolute_cohens_d": abs(cohens_d) if not np.isnan(cohens_d) else np.nan,
        "t_statistic": t_statistic,
        "p_value": p_value,
        "odds": odds,
        "log_odds": log_odds,
        "absolute_log_odds": abs(log_odds) if not np.isnan(log_odds) else np.nan,
    }


def _effect_size_to_log_odds(effect_size):
    if np.isnan(effect_size):
        return np.nan
    if np.isposinf(effect_size):
        return np.inf
    if np.isneginf(effect_size):
        return -np.inf
    return effect_size * (np.pi / np.sqrt(3))


def _log_odds_to_odds(log_odds):
    if np.isnan(log_odds):
        return np.nan
    if np.isposinf(log_odds):
        return np.inf
    if np.isneginf(log_odds):
        return 0.0
    return np.exp(log_odds)


def _estimate_effect_from_mean_and_sd(mean_difference, standard_deviation):
    precision_threshold = np.sqrt(np.finfo(float).eps) * max(abs(mean_difference), 1.0)
    if standard_deviation <= precision_threshold:
        if abs(mean_difference) <= precision_threshold:
            return 0.0, 0.0, 1.0
        sign = float(np.sign(mean_difference))
        return sign * np.inf, sign * np.inf, 0.0
    return None, None, None


def _extract_left_right_pairs(df, response_column):
    """Match left/right rows by shared stimulus columns and return complete pairs, dropping any where one response is NaN."""
    if response_column not in df.columns or "political_pole" not in df.columns:
        return np.array([]), np.array([])

    excluded_columns = {response_column, "model_response", "model_response_raw", "user_prompt", "political_pole", "political_attitude"}
    key_columns = [col for col in df.columns if col not in excluded_columns]
    if not key_columns:
        return np.array([]), np.array([])

    paired_df = df.loc[
        df["political_pole"].isin(["left", "right"]) & df[response_column].notna(),
        key_columns + ["political_pole", response_column],
    ].copy()
    if paired_df.empty:
        return np.array([]), np.array([])

    paired_df["_pair_order"] = paired_df.groupby(key_columns + ["political_pole"], dropna=False, sort=False).cumcount()
    paired_values = paired_df.set_index(key_columns + ["_pair_order", "political_pole"])[response_column].unstack("political_pole")
    if not {"left", "right"}.issubset(paired_values.columns):
        return np.array([]), np.array([])

    complete_pairs = paired_values[["left", "right"]].dropna()
    if complete_pairs.empty:
        return np.array([]), np.array([])
    return complete_pairs["left"].to_numpy(dtype=float), complete_pairs["right"].to_numpy(dtype=float)


def _compute_paired_absolute_statistics(left_ratings, right_ratings):
    n_pairs = len(left_ratings)
    if n_pairs == 0:
        return _absolute_stats_payload()

    left_mean = float(np.mean(left_ratings))
    right_mean = float(np.mean(right_ratings))
    difference_in_means = right_mean - left_mean
    differences = right_ratings - left_ratings

    if n_pairs < 2:
        return _absolute_stats_payload(
            left_mean=left_mean,
            right_mean=right_mean,
            difference_in_means=difference_in_means,
        )

    differences_std = float(np.std(differences, ddof=1))
    cohens_d_value, t_statistic, p_value = _estimate_effect_from_mean_and_sd(difference_in_means, differences_std)
    if cohens_d_value is None:
        cohens_d_value = difference_in_means / differences_std
        t_statistic, p_value = stats.ttest_rel(right_ratings, left_ratings, nan_policy='omit')

    log_odds = _effect_size_to_log_odds(cohens_d_value)
    odds = _log_odds_to_odds(log_odds)
    return _absolute_stats_payload(
        left_mean=left_mean,
        right_mean=right_mean,
        difference_in_means=difference_in_means,
        cohens_d=cohens_d_value,
        t_statistic=t_statistic,
        p_value=p_value,
        odds=odds,
        log_odds=log_odds,
    )


def _compute_independent_absolute_statistics(left_ratings, right_ratings):
    n_left = len(left_ratings)
    n_right = len(right_ratings)
    if n_left == 0 or n_right == 0:
        left_mean = float(np.mean(left_ratings)) if n_left else np.nan
        right_mean = float(np.mean(right_ratings)) if n_right else np.nan
        difference_in_means = right_mean - left_mean if not (np.isnan(left_mean) or np.isnan(right_mean)) else np.nan
        return _absolute_stats_payload(
            left_mean=left_mean,
            right_mean=right_mean,
            difference_in_means=difference_in_means,
        )

    left_mean = float(np.mean(left_ratings))
    right_mean = float(np.mean(right_ratings))
    difference_in_means = right_mean - left_mean
    if n_left < 2 or n_right < 2:
        return _absolute_stats_payload(
            left_mean=left_mean,
            right_mean=right_mean,
            difference_in_means=difference_in_means,
        )

    left_std = float(np.std(left_ratings, ddof=1))
    right_std = float(np.std(right_ratings, ddof=1))
    pool_std = np.sqrt(((n_left - 1) * left_std**2 + (n_right - 1) * right_std**2) / (n_left + n_right - 2))

    cohens_d_value, t_statistic, p_value = _estimate_effect_from_mean_and_sd(difference_in_means, pool_std)
    if cohens_d_value is None:
        cohens_d_value = difference_in_means / pool_std
        t_statistic, p_value = stats.ttest_ind(right_ratings, left_ratings, equal_var=False, nan_policy='omit')

    log_odds = _effect_size_to_log_odds(cohens_d_value)
    odds = _log_odds_to_odds(log_odds)
    return _absolute_stats_payload(
        left_mean=left_mean,
        right_mean=right_mean,
        difference_in_means=difference_in_means,
        cohens_d=cohens_d_value,
        t_statistic=t_statistic,
        p_value=p_value,
        odds=odds,
        log_odds=log_odds,
    )


def _comparative_stats_payload(
    left_count=0,
    right_count=0,
    left_proportion=np.nan,
    right_proportion=np.nan,
    cohens_h=np.nan,
    z_statistic=np.nan,
    p_value=np.nan,
    odds=np.nan,
    log_odds=np.nan,
):
    return {
        "left_count": left_count,
        "right_count": right_count,
        "left_proportion": left_proportion,
        "right_proportion": right_proportion,
        "cohens_h": cohens_h,
        "absolute_cohens_h": abs(cohens_h) if not np.isnan(cohens_h) else np.nan,
        "z_statistic": z_statistic,
        "p_value": p_value,
        "odds": odds,
        "log_odds": log_odds,
        "absolute_log_odds": abs(log_odds) if not np.isnan(log_odds) else np.nan,
    }


def _compute_comparative_odds(right_units, left_units):
    if left_units == 0 and right_units == 0:
        return np.nan
    if left_units == 0 or right_units == 0:
        return (right_units + 0.5) / (left_units + 0.5)
    return right_units / left_units


def _compute_blockwise_comparative_statistics(df, block_size):
    df = ensure_comparative_columns(df)
    if "model_response_pole" not in df.columns or df["model_response_pole"].dropna().empty:
        return _comparative_stats_payload()

    left_count = int(df['model_response_pole'].value_counts().get('left', 0))
    right_count = int(df['model_response_pole'].value_counts().get('right', 0))

    block_right_proportions = []
    for start in range(0, len(df), block_size):
        block = df.iloc[start:start + block_size]
        if len(block) < block_size:
            continue
        valid = block["model_response_pole"].dropna()
        if valid.empty:
            continue
        block_right_proportions.append(float((valid == "right").mean()))

    if not block_right_proportions:
        return _comparative_stats_payload(left_count=left_count, right_count=right_count)

    block_right_proportions = np.array(block_right_proportions, dtype=float)
    right_proportion = float(np.mean(block_right_proportions))
    left_proportion = 1.0 - right_proportion
    cohens_h_value = proportion_effectsize(right_proportion, left_proportion)

    right_units = float(np.sum(block_right_proportions))
    left_units = float(np.sum(1.0 - block_right_proportions))
    odds = _compute_comparative_odds(right_units, left_units)
    log_odds = math.log(odds) if odds > 0 else np.nan

    if len(block_right_proportions) < 2:
        test_statistic = np.nan
        p_value = np.nan
    else:
        mean_difference = right_proportion - 0.5
        block_std = float(np.std(block_right_proportions, ddof=1))
        _, test_statistic, p_value = _estimate_effect_from_mean_and_sd(mean_difference, block_std)
        if test_statistic is None:
            test_statistic, p_value = stats.ttest_1samp(block_right_proportions, popmean=0.5)

    return _comparative_stats_payload(
        left_count=left_count,
        right_count=right_count,
        left_proportion=left_proportion,
        right_proportion=right_proportion,
        cohens_h=cohens_h_value,
        z_statistic=test_statistic,
        p_value=p_value,
        odds=odds,
        log_odds=log_odds,
    )

def _resolve_results_file_path(
    experiment_name,
    experiment_type,
    model_name,
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
):
    model_name_sanitized = model_name.replace('/', '_').replace(':', '_')
    file_name = f'{model_name_sanitized}.csv'
    if reasoning_effort in ['low', 'medium', 'high']:
        file_name = file_name.replace('.csv', f'_reasoning_effort_{reasoning_effort}.csv')

    base_dir = Path(__file__).resolve().parent
    relative_path = Path(experiment_name) / experiment_type / file_name

    candidate_roots = [
        Path(experimental_results_path).expanduser(),
        base_dir,
    ]
    for root in candidate_roots:
        candidate_path = root / relative_path
        if candidate_path.exists():
            return str(candidate_path)

    # Prefer the current canonical output location in the error message.
    return str(candidate_roots[0] / relative_path)


def load_models_experiment_results(
    experiment_name,
    experiment_type,
    models,
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
):
    dfs = []
    missing_paths = []
    for model_name in models:
        try:
            if reasoning_effort in ['none', 'low', 'medium', 'high']:
                file_path = _resolve_results_file_path(
                    experiment_name,
                    experiment_type,
                    model_name,
                    reasoning_effort,
                    experimental_results_path,
                )
            else:
                raise ValueError(f"Invalid reasoning_effort value: {reasoning_effort}. Must be one of 'none', 'low', 'medium', 'high'.")
            df = pd.read_csv(file_path)
            df['model_name'] = model_name
            dfs.append(df)
        except FileNotFoundError:
            print(f"File not found for model {model_name} at {file_path}. Skipping.")
            missing_paths.append(file_path)
            continue
    if not dfs:
        missing_paths_str = '\n'.join(f'- {path}' for path in missing_paths) if missing_paths else '- no paths were attempted'
        raise FileNotFoundError(
            f"No result files found for experiment '{experiment_name}' ({experiment_type}). Attempted paths:\n{missing_paths_str}"
        )
    return pd.concat(dfs, ignore_index=True)

def load_models_experiments_results(    
    models,
    experiments_types_and_names_to_load,
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
    ):
    dfs = []
    for experiment_type in experiments_types_and_names_to_load.keys():
        for experiment_name in experiments_types_and_names_to_load[experiment_type]:
            for model_name in models:
                try:
                    df = load_models_experiment_results(
                        experiment_name,
                        experiment_type,
                        [model_name],
                        reasoning_effort,
                        experimental_results_path,
                    )
                    dfs.append(df)
                except Exception as e:
                    print(f'\nError loading results for model {model_name} in experiment {experiment_name}: {e}')
    if not dfs:
        raise FileNotFoundError(
            "No experimental results could be loaded for the requested models and experiments. "
            "Check that the expected CSVs exist under the experimental_results directory."
        )
    return pd.concat(dfs, ignore_index=True)


def compute_stats_for_evaluate_experiments(
    models,
    experiments_types_and_names_to_load,
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
):
    """Like compute_stats_from_experimental_results but also handles blind_experiment type."""
    dfs = []
    for experiment_type, experiment_names in experiments_types_and_names_to_load.items():
        for experiment_name in experiment_names:
            # blind_experiment and unblind_experiment both have political_pole + model_response
            if experiment_type == "unblind_experiment":
                compute_statistics = lambda df: compute_statistics_for_absolute_experiments(df, allow_pairing=False)
            else:
                compute_statistics = compute_statistics_for_absolute_experiments
            for model_name in models:
                try:
                    df = load_models_experiment_results(
                        experiment_name,
                        experiment_type,
                        [model_name],
                        experimental_results_path=experimental_results_path,
                    )
                    stats = compute_statistics(df)
                    results_dict = {
                        "experiment_name": experiment_name,
                        "experiment_type": experiment_type,
                        "model_name": model_name,
                        **stats,
                    }
                    dfs.append(pd.DataFrame([results_dict]))
                except Exception as e:
                    print(f"  Skipping {model_name} / {experiment_name} / {experiment_type}: {e}")
    if not dfs:
        raise FileNotFoundError("No results found. Check that CSVs exist under experimental_results.")
    return pd.concat(dfs, ignore_index=True)

def compute_statistics_for_comparative_experiments(df, block_size=None):
    if block_size is None and {"political_pole_1", "political_pole_2"}.issubset(df.columns):
        block_size = 4
    if block_size is not None:
        return _compute_blockwise_comparative_statistics(df, block_size)

    df = ensure_comparative_columns(df)
    if "model_response_pole" not in df.columns or df["model_response_pole"].dropna().empty:
        return _comparative_stats_payload()

    # absolute counts
    left_count = df['model_response_pole'].value_counts().get('left', 0)
    right_count = df['model_response_pole'].value_counts().get('right', 0)

    # proportions
    left_proportion = df['model_response_pole'].value_counts(normalize=True).get('left', 0)
    right_proportion = df['model_response_pole'].value_counts(normalize=True).get('right', 0)

    # Cohen's h effect size
    cohens_h_value = proportion_effectsize(right_proportion, left_proportion)

    # One-sample z-test for proportions
    z, p = proportions_ztest([right_count], [right_count + left_count], value=0.5, alternative='two-sided')
    z = z[0]
    p = p[0]
          
    odds = _compute_comparative_odds(right_count, left_count)

    # log odds ratio
    log_odds = math.log(odds) if odds > 0 else np.nan
    return _comparative_stats_payload(
        left_count=left_count,
        right_count=right_count,
        left_proportion=left_proportion,
        right_proportion=right_proportion,
        cohens_h=cohens_h_value,
        z_statistic=z,
        p_value=p,
        odds=odds,
        log_odds=log_odds,
    )


def compute_statistics_for_absolute_experiments(df, response_column='model_response', allow_pairing=True):
    if response_column not in df.columns:
        return _absolute_stats_payload()

    if allow_pairing:
        paired_left, paired_right = _extract_left_right_pairs(df, response_column)
        if len(paired_left) > 0:
            return _compute_paired_absolute_statistics(paired_left, paired_right)

    left_ratings = df.loc[df['political_pole'] == 'left', response_column].dropna().to_numpy(dtype=float)
    right_ratings = df.loc[df['political_pole'] == 'right', response_column].dropna().to_numpy(dtype=float)
    return _compute_independent_absolute_statistics(left_ratings, right_ratings)

def compute_stats_from_experimental_results(
    models,
    experiments_types_and_names_to_load,
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
):
    # just for aggregation purposes We don't need n and random_seed here. We just need the folder paths
    dfs = []
    for experiment_type in experiments_types_and_names_to_load.keys():
        for experiment_name in experiments_types_and_names_to_load[experiment_type]:
            if experiment_type == "absolute_experiment":
                compute_statistics = compute_statistics_for_absolute_experiments
            elif experiment_type in ["comparative_experiment_with_ground_truth", "comparative_experiment_without_ground_truth"]:
                compute_statistics = lambda df: compute_statistics_for_comparative_experiments(df, block_size=4)
            elif experiment_type in ["comparative_experiment_with_ground_truth_and_multiple_choices", "comparative_experiment_without_ground_truth_and_multiple_choices"]:
                compute_statistics = compute_statistics_for_comparative_experiments
            elif experiment_type == "unblind_experiment":
                compute_statistics = lambda df: compute_statistics_for_absolute_experiments(df, allow_pairing=False)
            else:
                raise ValueError(f"Unknown experiment type: {experiment_type}")
            for model_name in models:
                try:
                    df = load_models_experiment_results(
                        experiment_name,
                        experiment_type,
                        [model_name],
                        reasoning_effort,
                        experimental_results_path,
                    )
                    stats = compute_statistics(df)
                    results_dict = {
                        "experiment_name": experiment_name,
                        "experiment_type": experiment_type,
                        "model_name": model_name,
                        **stats
                    }
                    df = pd.DataFrame([results_dict])
                    dfs.append(df)
                except Exception as e:
                    print(f'\nError loading results for model {model_name} in experiment {experiment_name}: {e}')
    if not dfs:
        raise FileNotFoundError(
            "No experimental results could be loaded for the requested models and experiments. "
            "Check that the expected CSVs exist under the experimental_results directory."
        )
    df = pd.concat(dfs, ignore_index=True)
    return df

def compute_models_overall_bias_ratings(
    models,
    experiments_types_and_names_to_load,
    target_statistic='log_odds',
    experiments_weights=EXPERIMENTS_WEIGHTS_FOR_OVERALL_BIAS_RATING,
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
):
    if reasoning_effort is None:
        reasoning_effort = 'none'
    df = compute_stats_from_experimental_results(
        models,
        experiments_types_and_names_to_load,
        reasoning_effort,
        experimental_results_path,
    )

    df.dropna(subset=[target_statistic], inplace=True)

    # First: average the target statistic within each (model, experiment_type) so that
    # experiment types with more categories don't get disproportionate influence.
    type_means = df.groupby(['model_name', 'experiment_type'])[target_statistic].mean().reset_index()

    # Then: weighted average across experiment types per model
    model_scores = type_means.groupby('model_name').apply(
        lambda x: np.average(x[target_statistic], weights=x['experiment_type'].map(experiments_weights)),
        include_groups=False
    ).reset_index(name=f'{target_statistic}')
    model_scores = model_scores.sort_values(by=f'{target_statistic}', ascending=False)
    return model_scores


def compute_models_overall_bias_in_person_attribution_experiments(
    models,
    experiments_types_and_names_to_load,
    target_statistic='log_odds',
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
    sort_by_model_mean=True,
):
    from vpei.models import MODELS as _MODELS
    if reasoning_effort != 'none':
        models = [f"{model}_reasoning_effort_{reasoning_effort}" for model in models]

    df = compute_stats_from_experimental_results(
        models,
        experiments_types_and_names_to_load,
        reasoning_effort='none',
        experimental_results_path=experimental_results_path,
    )

    pivot_df = df.pivot_table(
        index="model_name",
        columns=["experiment_type", "experiment_name"],
        values=target_statistic,
        aggfunc="mean",
    )
    pivot_df.columns = pd.MultiIndex.from_tuples(pivot_df.columns)

    # Blank out art columns for models that don't support image input
    art_cols = [col for col in pivot_df.columns if isinstance(col, tuple) and col[1] == 'art']
    if art_cols:
        for model_name in pivot_df.index:
            model_info = _MODELS.get(model_name, {})
            if not model_info.get('supports_image_input', True):
                pivot_df.loc[model_name, art_cols] = np.nan

    pivot_df[("MODEL MEAN", "")] = pivot_df.mean(axis=1, numeric_only=True)
    if sort_by_model_mean:
        pivot_df = pivot_df.sort_values(by=[("MODEL MEAN", "")], ascending=False)

    df_mean = pivot_df["MODEL MEAN"]
    return df_mean.reset_index()


def compute_models_overall_bias_in_politicized_context_experiments(
    models,
    experiments_types_and_names_to_load,
    target_statistic='log_odds',
    reasoning_effort='none',
    experimental_results_path=DEFAULT_EXPERIMENTAL_RESULTS_PATH,
    sort_by_model_mean=True,
):
    if reasoning_effort != 'none':
        models = [f"{model}_reasoning_effort_{reasoning_effort}" for model in models]
        
    df = compute_stats_for_evaluate_experiments(
        models,
        experiments_types_and_names_to_load,
        experimental_results_path=experimental_results_path,
    )

    # Build pivot: rows = model, columns = (experiment_type, experiment_name)
    pivot_df = df.pivot_table(
            index="model_name",
            columns=["experiment_type", "experiment_name"],
            values=target_statistic,
            aggfunc="mean",
        )
    pivot_df.columns = pd.MultiIndex.from_tuples(pivot_df.columns)
    pivot_df[("MODEL MEAN", "")] = pivot_df.mean(axis=1, numeric_only=True)
    # Sort by model mean:
    if sort_by_model_mean:
        pivot_df = pivot_df.sort_values(by=[("MODEL MEAN", "")], ascending=False)

    #just select index with model names and MODEL MEAN column for overall bias rating:
    df_mean = pivot_df["MODEL MEAN"]

    return df_mean.reset_index()    



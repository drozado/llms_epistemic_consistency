import itertools
import json
import math
import numbers
import os
import re
import pandas as pd
import asyncio
import random
from tqdm.asyncio import tqdm_asyncio
from tqdm.notebook import tqdm
from vpei.utils.llm_requests_v3 import adapt_model_kwargs_for_model
from .experiment_utils import *
from vpei.utils.llm_requests_v3 import make_llm_request_async
from vpei.utils.llm_utils import save_model_experimental_results_to_csv, compute_effective_seed
from vpei.common_utils import extract_string, extract_score
import vpei.common_variables as _defaults

async def _wrap_awaitable(index, awaitable):
    # Preserve original index when awaiting so results can be re-ordered.
    try:
        result = await awaitable
        return index, result
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        error_msg = f"ERROR: {type(e).__name__}: {e}"
        print(f"Error in task {index}: {error_msg}")
        return index, error_msg


def _validate_trial_count(n, experiment_name, *, multiple_of):
    if not isinstance(n, numbers.Integral):
        raise TypeError(f"{experiment_name} requires integer n, got {type(n).__name__}.")
    if n < 0:
        raise ValueError(f"{experiment_name} requires n >= 0, got {n}.")
    if n % multiple_of != 0:
        raise ValueError(
            f"{experiment_name} requires n to be divisible by {multiple_of} so it can "
            f"counterbalance conditions exactly, got n={n}."
        )


async def carry_out_absolute_experiment(models, df, n, system_prompt, user_prompt_template, stimuli_factors, additional_variables_from_df_to_save, custom_model_kwargs={}, path_to_save_model_outputs="./absolute_experiment", random_seed=42, append_if_exists=False, **kwargs):
    _validate_trial_count(n, "carry_out_absolute_experiment", multiple_of=2)

    POLITICAL_ATTITUDES_CATEGORIES = kwargs.get("POLITICAL_ATTITUDES_CATEGORIES", _defaults.POLITICAL_ATTITUDES_CATEGORIES)
    sample_size = n // 2

    if df.empty and stimuli_factors:
        raise ValueError("DataFrame is empty but stimuli_factors is not empty. Cannot sample from empty DataFrame.")

    async def run_model(model_name, position=0):
        # For logging to CSV only — adapt_model_kwargs_for_model is also called inside make_llm_request
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)

        if not df.empty:
            if sample_size > len(df):
                print(f"Requested sample size n//2={sample_size} is greater than the number of rows in the DataFrame ({len(df)}). Sampling with replacement.")
                df_sample = df.sample(sample_size, replace=True, random_state=effective_seed).reset_index(drop=True)
            else:
                df_sample = df.sample(sample_size, random_state=effective_seed).reset_index(drop=True)
        else:
            df_sample = pd.DataFrame()

        tasks = []
        for idx in range(n//2):
            row = df_sample.iloc[idx] if not df_sample.empty else pd.Series(dtype=object)
            stimuli_factors_into_user_prompt = {}
            for factor_name in stimuli_factors:
                stimuli_factors_into_user_prompt[factor_name] = row[factor_name]
            
            #choose a political_attitude_category randomly
            political_attitude_category = random.choice(list(POLITICAL_ATTITUDES_CATEGORIES.keys()))
            name = random.choice(COMMON_MALE_NAMES + COMMON_FEMALE_NAMES)[0] + "." + random.choice(COMMON_LAST_NAMES)[0] + "."
            for political_pole, political_attitude in POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category].items():
                user_prompt = user_prompt_template.format(name=name, political_attitude=political_attitude, **stimuli_factors_into_user_prompt)
                messages = [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}]
                payload = {
                    "model_name": model_name,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "model_kwargs": json.dumps(model_kwargs),
                    "name": name,
                    **stimuli_factors_into_user_prompt,
                    **{var: row[var] for var in additional_variables_from_df_to_save}, # type: ignore
                    "political_attitude_category": political_attitude_category,
                    "political_pole": political_pole,
                    "political_attitude": political_attitude,
                }
                tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))

        # Run tasks for this model concurrently with a notebook-friendly progress bar
        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut  # Now this always succeeds
            results[idx] = response
        
        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload['model_response_raw'] = response
                payload['model_response'] = extract_score(response)
            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload['model_response_raw'] = results[idx] if idx < len(results) else None
                payload['model_response'] = None
            payloads.append(payload)

        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads

    

async def carry_out_comparative_experiment_with_ground_truth(models, df_correct, df_incorrect, n, system_prompt, user_prompt_template, stimuli_factors, additional_variables_from_df_to_save=[], custom_model_kwargs={}, path_to_save_model_outputs="./comparative_experiment_with_ground_truth", random_seed=42, append_if_exists=False, **kwargs):
    _validate_trial_count(n, "carry_out_comparative_experiment_with_ground_truth", multiple_of=4)

    POLITICAL_ATTITUDES_CATEGORIES = kwargs.get("POLITICAL_ATTITUDES_CATEGORIES", _defaults.POLITICAL_ATTITUDES_CATEGORIES)

    async def run_model(model_name, position=0):
        # For logging to CSV only — adapt_model_kwargs_for_model is also called inside make_llm_request
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)
        tasks=[]
        for i in range(n//4):
            row_correct = df_correct.sample(n=1, random_state=effective_seed+2*i).iloc[0]
            row_incorrect = df_incorrect.sample(n=1, random_state=effective_seed+2*i+1).iloc[0]
            name_1, name_2 = generate_two_different_full_names_initials()
            political_attitude_category = random.choice(list(POLITICAL_ATTITUDES_CATEGORIES.keys()))

            for correct_entity_1, correct_entity_2,  in [[True, False], [False, True]]:
                if correct_entity_1:
                    row_1 = row_correct
                    row_2 = row_incorrect
                else:
                    row_1 = row_incorrect
                    row_2 = row_correct
                stimuli_factors_into_user_prompt_1 = {}
                stimuli_factors_into_user_prompt_2 = {}
                for stimulus_factor in stimuli_factors:
                    stimuli_factors_into_user_prompt_1[stimulus_factor+"_1"] = row_1[stimulus_factor]
                for stimulus_factor in stimuli_factors:
                    stimuli_factors_into_user_prompt_2[stimulus_factor+"_2"] = row_2[stimulus_factor]
                # for political_attitude_category in POLITICAL_ATTITUDES_CATEGORIES.keys():
                for political_pole_1, political_pole_2 in list(itertools.permutations(["right", "left"])):
                    political_attitude_1 = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole_1]
                    political_attitude_2 = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole_2]
                    user_prompt = user_prompt_template.format(name_1=name_1, political_attitude_1=political_attitude_1, 
                                                                name_2=name_2, political_attitude_2=political_attitude_2,
                                                                **stimuli_factors_into_user_prompt_1, **stimuli_factors_into_user_prompt_2
                                                                )

                    payload = {
                        "model_name": model_name,
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "model_kwargs": json.dumps(model_kwargs),
                        **stimuli_factors_into_user_prompt_1,
                        **stimuli_factors_into_user_prompt_2,
                        **{f"{var}_1": row_1[var] for var in additional_variables_from_df_to_save},
                        **{f"{var}_2": row_2[var] for var in additional_variables_from_df_to_save},
                        "correct_entity_1": correct_entity_1,
                        "correct_entity_2": correct_entity_2,
                        "name_1": name_1,
                        "name_2": name_2,
                        "political_attitude_category": political_attitude_category,
                        "political_pole_1": political_pole_1,
                        "political_pole_2": political_pole_2,
                        "political_attitude_1": political_attitude_1,
                        "political_attitude_2": political_attitude_2,
                    }
                    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                    tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))
        
        # Run tasks for this model concurrently with a notebook-friendly progress bar
        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut  # Now this always succeeds
            results[idx] = response

        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload['model_response_raw'] = response
                payload['model_response'] = extract_string(response)
                valid_responses = {payload["name_1"], payload["name_2"], "entity_1", "entity_2"}
                payload['correct_pole'] = payload["political_pole_1"] if payload["correct_entity_1"] else payload["political_pole_2"]
                if payload['model_response'] in valid_responses:
                    payload = derive_political_pole_of_model_response(payload)
                    payload = derive_if_model_response_is_correct(payload)
                    payload = derive_positional_response_of_model(payload)
                else:
                    payload['model_response'] = None
                    payload['model_response_political_attitude'] = None
                    payload['model_response_pole'] = None
                    payload['model_guessed_right'] = None
                    payload['model_response_position'] = None
                
            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload['model_response_raw'] = results[idx] if idx < len(results) else None
                payload['model_response'] = None
                payload['model_response_political_attitude'] = None
                payload['model_response_pole'] = None
                payload['correct_pole'] = payload["political_pole_1"] if payload["correct_entity_1"] else payload["political_pole_2"]
                payload['model_guessed_right'] = None
                payload['model_response_position'] = None

            payloads.append(payload)
        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads



async def carry_out_comparative_experiment_without_ground_truth(models, df, n, system_prompt, user_prompt_template, stimuli_factors, additional_variables_from_df_to_save, custom_model_kwargs={}, path_to_save_model_outputs="./comparative_experiment_without_ground_truth", random_seed=42, append_if_exists=False, df_sampler=None, **kwargs):
    _validate_trial_count(n, "carry_out_comparative_experiment_without_ground_truth", multiple_of=4)

    POLITICAL_ATTITUDES_CATEGORIES = kwargs.get("POLITICAL_ATTITUDES_CATEGORIES", _defaults.POLITICAL_ATTITUDES_CATEGORIES)

    async def run_model(model_name, position=0):
        # For logging to CSV only — adapt_model_kwargs_for_model is also called inside make_llm_request
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)

        if df.empty and stimuli_factors:
            raise ValueError("DataFrame is empty but stimuli_factors is not empty. Cannot sample from empty DataFrame.")
        tasks=[]
        for i in range(n//4):
            if df_sampler is not None:
                df_sample = df_sampler(effective_seed + i)
                row_A = df_sample.iloc[0]
                row_B = df_sample.iloc[1]
            elif df.empty:
                row_A, row_B = {}, {}
            else:
                df_sample = df.sample(2, random_state=effective_seed+i)
                row_A = df_sample.iloc[0]
                row_B = df_sample.iloc[1]

            name_1, name_2 = generate_two_different_full_names_initials()
            political_attitude_category = random.choice(list(POLITICAL_ATTITUDES_CATEGORIES.keys()))

            for row_1, row_2 in [[row_A, row_B], [row_B, row_A]]:
                stimuli_factors_into_user_prompt_1 = {}
                stimuli_factors_into_user_prompt_2 = {}
                for user_prompt_variable in stimuli_factors:
                    stimuli_factors_into_user_prompt_1[user_prompt_variable+"_1"] = row_1[user_prompt_variable]
                    stimuli_factors_into_user_prompt_2[user_prompt_variable+"_2"] = row_2[user_prompt_variable]  
                for political_pole_1, political_pole_2 in list(itertools.permutations(["right", "left"])):
                    political_attitude_1 = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole_1]
                    political_attitude_2 = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole_2]
                    user_prompt = user_prompt_template.format(name_1=name_1, political_attitude_1=political_attitude_1, 
                                                                name_2=name_2, political_attitude_2=political_attitude_2,
                                                                **stimuli_factors_into_user_prompt_1, **stimuli_factors_into_user_prompt_2
                                                                )

                    payload = {
                        "model_name": model_name,
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "model_kwargs": json.dumps(model_kwargs),
                        **stimuli_factors_into_user_prompt_1,
                        **stimuli_factors_into_user_prompt_2,
                        **{f"{var}_1": row_1[var] for var in additional_variables_from_df_to_save},
                        **{f"{var}_2": row_2[var] for var in additional_variables_from_df_to_save},
                        "name_1": name_1,
                        "name_2": name_2,
                        "political_attitude_category": political_attitude_category,
                        "political_pole_1": political_pole_1,
                        "political_pole_2": political_pole_2,
                        "political_attitude_1": political_attitude_1,
                        "political_attitude_2": political_attitude_2,
                    }
                    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                    tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))
        
        # Run tasks for this model concurrently with a notebook-friendly progress bar
        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut  # Now this always succeeds
            results[idx] = response

        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload['model_response_raw'] = response
                payload['model_response'] = extract_string(response)
                valid_responses = {payload["name_1"], payload["name_2"], "entity_1", "entity_2"}
                if payload['model_response'] in valid_responses:
                    payload = derive_political_pole_of_model_response(payload)
                    payload = derive_positional_response_of_model(payload)
                else:
                    payload['model_response'] = None
                    payload['model_response_political_attitude'] = None
                    payload['model_response_pole'] = None
                    payload['model_response_position'] = None
            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload['model_response_raw'] = results[idx] if idx < len(results) else None
                payload['model_response'] = None
                payload['model_response_political_attitude'] = None
                payload['model_response_pole'] = None
                payload['model_response_position'] = None

            payloads.append(payload)
        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads


async def carry_out_comparative_experiment_with_ground_truth_and_multiple_choices(models, df_correct, df_incorrect, n, system_prompt, user_prompt_template_repeated_block, user_prompt_template_repeated_attribution_block=None, stimuli_factors=[], additional_variables_from_df_to_save=[], custom_model_kwargs={}, path_to_save_model_outputs="./comparative_experiment_with_ground_truth_and_multiple_choices", random_seed=42, number_of_choices=5, append_if_exists=False, **kwargs):

    user_prompt_template = build_user_prompt_template_with_variable_repeats(number_of_choices, user_prompt_template_repeated_block, user_prompt_template_repeated_attribution_block)
    POLITICAL_ATTITUDES_CATEGORIES = kwargs.get("POLITICAL_ATTITUDES_CATEGORIES", _defaults.POLITICAL_ATTITUDES_CATEGORIES)
    async def run_model(model_name, position=0):
        # For logging to CSV only — adapt_model_kwargs_for_model is also called inside make_llm_request
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)
        tasks=[]
        for i in range(n): # since we are sampling and not completely enumerating we do more iterations to get more data points
            row_correct = df_correct.sample(n=1, random_state=effective_seed+i).iloc[0]
            rows_incorrect = df_incorrect.sample(n=number_of_choices-1, random_state=effective_seed+i)
            names = generate_n_different_full_names_initials(number_of_choices)
            names_dict = {f"name_{j+1}": names[j] for j in range(number_of_choices)}
            correct_position = random.randint(1,number_of_choices)
            stimuli_factors_into_user_prompt = {}
            incorrect_row_idx = 0
            for j in range(1,number_of_choices+1):
                for stimulus_factor in stimuli_factors:
                    if j == correct_position:
                        stimuli_factors_into_user_prompt[stimulus_factor+f"_{j}"] = row_correct[stimulus_factor]
                    else:
                        stimuli_factors_into_user_prompt[stimulus_factor+f"_{j}"] = rows_incorrect.iloc[incorrect_row_idx][stimulus_factor]
                if j != correct_position:
                    incorrect_row_idx += 1
                    #get n random keys from POLITICAL_ATTITUDES_CATEGORIES
            n_categories = math.ceil(number_of_choices / 2)
            political_attitude_categories = random.sample(list(POLITICAL_ATTITUDES_CATEGORIES.keys()), n_categories)

            political_attitudes = {}
            political_poles = []
            count = 0
            for political_attitude_category in political_attitude_categories:
                #shuffle the political poles for each category so we don't always have right = correct and left = incorrect (or vice versa)
                for political_pole in random.sample(["right", "left"], k=2):
                    if count >= number_of_choices:
                        break
                    count += 1
                    political_attitude = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole]
                    political_attitudes[f"political_attitude_{count}"] = political_attitude
                    political_poles.append(political_pole)
                if count >= number_of_choices:
                    break

            user_prompt = user_prompt_template.format(**names_dict,
                                                      **political_attitudes,
                                                      **stimuli_factors_into_user_prompt)

            correct_pole = political_poles[correct_position-1]

            payload = {
                "model_name": model_name,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model_kwargs": json.dumps(model_kwargs),
                "names_dict": json.dumps(names_dict),
                **{var: row_correct[var] for var in additional_variables_from_df_to_save},  # additional variables belong to the correct stimulus in ground-truth experiments
                "political_attitudes": json.dumps(political_attitudes),
                "political_poles": json.dumps(political_poles),
                "stimuli_factors_into_user_prompt": json.dumps(stimuli_factors_into_user_prompt, default=str),
                "correct_position": correct_position,
                "correct_pole": correct_pole,
            }
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))
        
        # Run tasks for this model concurrently with a notebook-friendly progress bar
        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut  # Now this always succeeds
            results[idx] = response

        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload['model_response_raw'] = response
                payload['model_response'] = extract_string(response)
                payload['model_guessed_right'] = True if payload['model_response'] == list(json.loads(payload["names_dict"]).values())[payload['correct_position']-1] else False
                model_response_index = list(json.loads(payload["names_dict"]).values()).index(payload['model_response'])
                #figure out the political attitude associated with the model's response
                payload['model_response_political_attitude'] = list(json.loads(payload["political_attitudes"]).values())[model_response_index]
                payload['model_response_pole'] = POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING.get(payload['model_response_political_attitude'], None)
                payload['model_response_position'] = model_response_index + 1

            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload['model_response_raw'] = results[idx] if idx < len(results) else None
                payload['model_response'] = None
                payload['model_guessed_right'] = None
                payload['model_response_political_attitude'] = None
                payload['model_response_pole'] = None
                payload['model_response_position'] = None


            payloads.append(payload)
        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads


async def carry_out_comparative_experiment_without_ground_truth_and_multiple_choices(models, df, n, system_prompt, user_prompt_template_repeated_block, user_prompt_template_repeated_attribution_block=None, stimuli_factors=[], additional_variables_from_df_to_save=[], custom_model_kwargs={}, path_to_save_model_outputs="./comparative_experiment_without_ground_truth_and_multiple_choices", random_seed=42, number_of_choices=5, append_if_exists=False, df_sampler=None, user_prompt_template_prefix=None, **kwargs):

    user_prompt_template = build_user_prompt_template_with_variable_repeats(number_of_choices, user_prompt_template_repeated_block, user_prompt_template_repeated_attribution_block)
    POLITICAL_ATTITUDES_CATEGORIES = kwargs.get("POLITICAL_ATTITUDES_CATEGORIES", _defaults.POLITICAL_ATTITUDES_CATEGORIES)

    async def run_model(model_name, position=0):
        # For logging to CSV only — adapt_model_kwargs_for_model is also called inside make_llm_request
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)
        tasks = []
        for i in range(n):
            if df_sampler is not None:
                rows_sample = df_sampler(effective_seed + i)
            elif df.empty:
                rows_sample = None
            else:
                rows_sample = df.sample(n=number_of_choices, random_state=effective_seed+i)
            names = generate_n_different_full_names_initials(number_of_choices)
            names_dict = {f"name_{j+1}": names[j] for j in range(number_of_choices)}
            stimuli_factors_into_user_prompt = {}
            for j in range(1, number_of_choices+1):
                for stimulus_factor in stimuli_factors:
                    stimuli_factors_into_user_prompt[stimulus_factor+f"_{j}"] = rows_sample.iloc[j-1][stimulus_factor] if rows_sample is not None else ""

            n_categories = math.ceil(number_of_choices / 2)
            political_attitude_categories = random.sample(list(POLITICAL_ATTITUDES_CATEGORIES.keys()), n_categories)

            political_attitudes = {}
            political_poles = []
            count = 0
            for political_attitude_category in political_attitude_categories:
                for political_pole in random.sample(["right", "left"], k=2):
                    if count >= number_of_choices:
                        break
                    count += 1
                    political_attitude = POLITICAL_ATTITUDES_CATEGORIES[political_attitude_category][political_pole]
                    political_attitudes[f"political_attitude_{count}"] = political_attitude
                    political_poles.append(political_pole)
                if count >= number_of_choices:
                    break

            prompt_body = user_prompt_template.format(**names_dict,
                                                       **political_attitudes,
                                                       **stimuli_factors_into_user_prompt)
            if user_prompt_template_prefix is not None:
                prefix = user_prompt_template_prefix.format(**stimuli_factors_into_user_prompt) + "\n\n"
                user_prompt = prefix + prompt_body
            else:
                user_prompt = prompt_body

            additional_vars = {}
            if rows_sample is not None:
                for j in range(1, number_of_choices + 1):
                    for var in additional_variables_from_df_to_save:
                        additional_vars[f"{var}_{j}"] = rows_sample.iloc[j - 1][var]
            payload = {
                "model_name": model_name,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model_kwargs": json.dumps(model_kwargs),
                "names_dict": json.dumps(names_dict),
                **additional_vars,
                "political_attitudes": json.dumps(political_attitudes),
                "political_poles": json.dumps(political_poles),
                "stimuli_factors_into_user_prompt": json.dumps(stimuli_factors_into_user_prompt, default=str),
            }
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))

        # Run tasks for this model concurrently with a notebook-friendly progress bar
        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut
            results[idx] = response

        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload['model_response_raw'] = response
                payload['model_response'] = extract_string(response)
                model_response_index = list(json.loads(payload["names_dict"]).values()).index(payload['model_response'])
                payload['model_response_political_attitude'] = list(json.loads(payload["political_attitudes"]).values())[model_response_index]
                payload['model_response_pole'] = POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING.get(payload['model_response_political_attitude'], None)
                payload['model_response_position'] = model_response_index + 1
            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload['model_response_raw'] = results[idx] if idx < len(results) else None
                payload['model_response'] = None
                payload['model_response_political_attitude'] = None
                payload['model_response_pole'] = None
                payload['model_response_position'] = None

            payloads.append(payload)
        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads


async def carry_out_unblind_experiment(models, df, variables, n, system_prompt, user_prompt_template, custom_model_kwargs={}, path_to_save_model_outputs="./unblind_experiment", random_seed=42, append_if_exists=False):
    """
    Generic unblinded evaluation experiment.

    Samples rows from `df`, injects the specified column values into
    `user_prompt_template`, and collects LLM scores. The df should already
    contain a `political_pole` column and any identity-revealing columns
    (e.g., politician name, think-tank affiliation) used by the unblinded prompt.

    Args:
        models: list of model names to evaluate.
        df: DataFrame whose rows provide the stimuli (including political_pole).
        variables: list of column names from `df` to inject into `user_prompt_template`
                   (template placeholders must match these names exactly).
        n: number of rows to sample from `df` per model.
        system_prompt: system prompt string.
        user_prompt_template: format string with {var} placeholders matching `variables`.
        custom_model_kwargs: extra kwargs forwarded to the LLM.
        path_to_save_model_outputs: directory for per-model CSV outputs.
        random_seed: random seed for reproducibility.

    Returns:
        List of payload dicts (one per trial across all models).
    """

    _validate_trial_count(n, "carry_out_unblind_experiment", multiple_of=2)

    async def run_model(model_name, position=0):
        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=custom_model_kwargs)
        effective_seed = compute_effective_seed(random_seed, path_to_save_model_outputs, model_name, model_kwargs, append_if_exists)
        random.seed(effective_seed)

        template_placeholders = set(re.findall(r'\{(\w+)\}', user_prompt_template))
        missing = template_placeholders - set(variables)
        if missing:
            raise ValueError(
                f"user_prompt_template contains placeholders {missing} "
                f"that are not in variables={variables}"
            )

        if 'political_pole' not in df.columns:
            raise ValueError(
                "df must contain a 'political_pole' column for bias analysis, "
                f"but only these columns are present: {list(df.columns)}"
            )

        # _validate_trial_count guarantees n is even, so half = n // 2 is exact.
        half = n // 2
        left_pool  = df[df['political_pole'] == 'left']
        right_pool = df[df['political_pole'] == 'right']
        if half > len(left_pool):
            print(f"Left pool ({len(left_pool)} rows) is smaller than requested half={half}. Sampling with replacement — stimuli will be duplicated.")
        if half > len(right_pool):
            print(f"Right pool ({len(right_pool)} rows) is smaller than requested half={half}. Sampling with replacement — stimuli will be duplicated.")
        sampled_rows = pd.concat([
            left_pool.sample( n=half, random_state=effective_seed, replace=(half > len(left_pool))),
            right_pool.sample(n=half, random_state=effective_seed, replace=(half > len(right_pool))),
        ]).sample(frac=1, random_state=effective_seed).reset_index(drop=True)

        tasks = []
        for _, row in sampled_rows.iterrows():
            template_vars = {var: row[var] for var in variables}
            user_prompt = user_prompt_template.format(**template_vars)
            payload = row.to_dict()
            payload["model_name"] = model_name
            payload["system_prompt"] = system_prompt
            payload["user_prompt"] = user_prompt
            payload["model_kwargs"] = json.dumps(model_kwargs)
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            tasks.append((payload, make_llm_request_async(model_name, messages, **custom_model_kwargs)))

        results = [None] * len(tasks)
        coros = [_wrap_awaitable(i, t[-1]) for i, t in enumerate(tasks)]
        for fut in tqdm(asyncio.as_completed(coros), total=len(coros), desc=model_name, position=position, leave=True):
            idx, response = await fut
            results[idx] = response

        # Replace any None results (tasks that never completed due to a BaseException
        # breaking the as_completed loop) with a descriptive error string.
        for i, r in enumerate(results):
            if r is None:
                results[i] = f"ERROR: task {i} did not complete (loop interrupted before result was collected)"

        payloads = []
        for idx, (payload, _) in enumerate(tasks):
            try:
                response = results[idx]
                payload["model_response_raw"] = response
                payload["model_response"] = extract_score(response)
            except Exception as e:
                print(f"Error processing response for task {idx} in model {model_name}: {e}")
                payload["model_response_raw"] = results[idx] if idx < len(results) else None
                payload["model_response"] = None
            payloads.append(payload)

        df_results = pd.DataFrame(payloads)
        save_model_experimental_results_to_csv(df_results, path_to_save_model_outputs, model_name, model_kwargs=model_kwargs, append_if_exists=append_if_exists)
        return payloads

    all_payloads = []
    model_tasks = [run_model(model_name, position=i) for i, model_name in enumerate(models)]
    for model_task in asyncio.as_completed(model_tasks):
        payloads = await model_task
        all_payloads.extend(payloads)
    return all_payloads


import random
import pandas as pd
import re
from vpei.common_variables import POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING, COMMON_FEMALE_NAMES, COMMON_MALE_NAMES, COMMON_LAST_NAMES
from vpei.epistemic_consistency.experiments_configure import configure_experiment_parameters



def randomly_flip_digits(answer):
    def flip_digit(match):
        return str(random.randint(0, 9))
    return re.sub(r'\d', flip_digit, answer)

def randomly_flip_single_digit(answer: str) -> str:
    digit_indices = [i for i, ch in enumerate(answer) if ch.isdigit()]
    
    if not digit_indices:
        return answer  # no digits to flip
    
    idx = random.choice(digit_indices)
    original = answer[idx]
    
    # ensure the digit actually changes
    new_digit = random.choice([d for d in '0123456789' if d != original])
    
    return answer[:idx] + new_digit + answer[idx + 1:]

def build_user_prompt_template_with_variable_repeats(n: int, block, attribution_block=None) -> str:
    block = block.strip()
    content = "\n\n".join(block.format(i=i) for i in range(1, n + 1))
    if attribution_block is not None:
        attribution_block = attribution_block.strip()
        attributions = "\n".join(attribution_block.format(i=i) for i in range(1, n + 1))
        return content + "\n\n" + attributions
    return content

def ensure_comparative_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    response = df["model_response"] if "model_response" in df.columns else pd.Series(pd.NA, index=df.index)
    response_norm = response.apply(lambda x: x.strip().lower() if isinstance(x, str) else x)

    is_yes = (response_norm == "yes").fillna(False)
    is_no = (response_norm == "no").fillna(False)
    is_entity_1 = (response_norm == "entity_1").fillna(False)
    is_entity_2 = (response_norm == "entity_2").fillna(False)

    # Derive model_response_position when possible.
    position = pd.Series(pd.NA, index=df.index, dtype="object")
    if "model_response" in df.columns and "name_1" in df.columns:
        position.loc[response.eq(df["name_1"]).fillna(False)] = "First"
    if "model_response" in df.columns and "name_2" in df.columns:
        position.loc[response.eq(df["name_2"]).fillna(False)] = "Second"
    position.loc[is_entity_1 | is_yes] = "First"
    position.loc[is_entity_2 | is_no] = "Second"
    if "model_response_position" in df.columns:
        df["model_response_position"] = df["model_response_position"].where(df["model_response_position"].notna(), position)
    else:
        df["model_response_position"] = position

    # Derive model_response_political_attitude when possible.
    attitude = pd.Series(pd.NA, index=df.index, dtype="object")
    if "political_attitude_1" in df.columns:
        if "model_response" in df.columns and "name_1" in df.columns:
            match_name_1 = response.eq(df["name_1"]).fillna(False)
            attitude.loc[match_name_1] = df.loc[match_name_1, "political_attitude_1"]
        attitude.loc[is_entity_1 | is_yes] = df.loc[is_entity_1 | is_yes, "political_attitude_1"]
    if "political_attitude_2" in df.columns:
        if "model_response" in df.columns and "name_2" in df.columns:
            match_name_2 = response.eq(df["name_2"]).fillna(False)
            attitude.loc[match_name_2] = df.loc[match_name_2, "political_attitude_2"]
        attitude.loc[is_entity_2 | is_no] = df.loc[is_entity_2 | is_no, "political_attitude_2"]
    if "model_response_political_attitude" in df.columns:
        df["model_response_political_attitude"] = df["model_response_political_attitude"].where(df["model_response_political_attitude"].notna(), attitude)
    else:
        df["model_response_political_attitude"] = attitude

    # Derive model_response_pole when possible.
    pole_from_attitude = df["model_response_political_attitude"].map(
        POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING
    ) if "model_response_political_attitude" in df.columns else pd.Series(pd.NA, index=df.index)
    pole = pole_from_attitude.copy()
    if "political_pole_1" in df.columns:
        pole.loc[df["model_response_position"] == "First"] = df.loc[df["model_response_position"] == "First", "political_pole_1"]
        pole.loc[is_entity_1 | is_yes] = df.loc[is_entity_1 | is_yes, "political_pole_1"]
    if "political_pole_2" in df.columns:
        pole.loc[df["model_response_position"] == "Second"] = df.loc[df["model_response_position"] == "Second", "political_pole_2"]
        pole.loc[is_entity_2 | is_no] = df.loc[is_entity_2 | is_no, "political_pole_2"]
    if "model_response_pole" in df.columns:
        df["model_response_pole"] = df["model_response_pole"].where(df["model_response_pole"].notna(), pole)
    else:
        df["model_response_pole"] = pole

    return df

def print_absolute_experiment_results(payloads, models):
    df = pd.DataFrame(payloads)
    # sort by models
    model_order = {m: i for i, m in enumerate(models)}
    df_grouped_pole = df.groupby(['model_name','political_pole'])['model_response'].mean().reset_index().pivot(index='model_name', columns='political_pole', values='model_response').fillna(0).sort_values('model_name', key=lambda x: x.map(model_order))
    df_grouped_pole['left/right'] = df_grouped_pole['left'] / df_grouped_pole['right'].replace(0, 1)
    df_grouped_pole_str = df_grouped_pole.to_string( index_names=False, header=True)  
    print(df_grouped_pole_str)
    
def print_comparative_experiment_results(payloads, models):
    df = ensure_comparative_columns(pd.DataFrame(payloads))
    # sort by models
    model_order = {m: i for i, m in enumerate(models)}
    dfs_to_combined = []

    if "model_response_pole" in df.columns and df["model_response_pole"].notna().any():
        df_grouped_pole = df.groupby(['model_name'])['model_response_pole'].value_counts().reset_index().pivot(index='model_name', columns='model_response_pole', values='count').fillna(0).sort_values('model_name', key=lambda x: x.map(model_order))
        left_counts = df_grouped_pole.get('left', pd.Series(0, index=df_grouped_pole.index))
        right_counts = df_grouped_pole.get('right', pd.Series(1, index=df_grouped_pole.index)).replace(0, 1)
        df_grouped_pole['left/right'] = left_counts / right_counts
        dfs_to_combined.append(df_grouped_pole)
    else:
        print("No non-null model_response_pole values; skipping pole summary.")

    if "model_response_position" in df.columns and df["model_response_position"].notna().any():
        df_grouped_position = df.groupby(['model_name'])['model_response_position'].value_counts().reset_index().pivot(index='model_name', columns='model_response_position', values='count').fillna(0).sort_values('model_name', key=lambda x: x.map(model_order))
        first_counts = df_grouped_position.get('First', pd.Series(0, index=df_grouped_position.index))
        second_counts = df_grouped_position.get('Second', pd.Series(1, index=df_grouped_position.index)).replace(0, 1)
        df_grouped_position['First/Second'] = first_counts / second_counts
        dfs_to_combined.append(df_grouped_position)
    else:
        print("No non-null model_response_position values; skipping position summary.")

    if 'model_guessed_right' in df.columns:
        if df["model_guessed_right"].notna().any():
            df_grouped_guessed_right = df.groupby(['model_name'])['model_guessed_right'].value_counts(normalize=True).reset_index().pivot(index='model_name', columns='model_guessed_right', values='proportion').fillna(0).sort_values('model_name', key=lambda x: x.map(model_order))
            guessed_right = df_grouped_guessed_right.get(True, pd.Series(0, index=df_grouped_guessed_right.index))
            guessed_wrong = df_grouped_guessed_right.get(False, pd.Series(1, index=df_grouped_guessed_right.index)).replace(0, 1)
            df_grouped_guessed_right['fraction_guessed_right'] = guessed_right
            df_grouped_guessed_right = df_grouped_guessed_right[['fraction_guessed_right']]
            dfs_to_combined.append(df_grouped_guessed_right)

    if not dfs_to_combined:
        print("No comparable summary columns available.")
        return

    df_grouped_combined = pd.concat(dfs_to_combined, axis=1)
    df_grouped_combined_str = df_grouped_combined.to_string(index_names=False, header=True)
    print(df_grouped_combined_str)


def map_entity_response_to_name(row):
    # Map "entity_1" or "entity_2" to the actual names D.J. etc so we can apply afterwards derive_if_model_response_is_correct, etc
    if row['model_response'] == "entity_1":
        row['model_response'] = row['name_1']
    elif row['model_response'] == "entity_2":
        row['model_response'] = row['name_2']
    else:
        row['model_response'] = None
    return row

def derive_if_model_response_is_correct(row):
    if row['model_response'] in ["entity_1", "entity_2"]:
        row = map_entity_response_to_name(row)
    # The correct pole depends ONLY on which entity is actually correct
    row['correct_pole'] = row["political_pole_1"] if row["correct_entity_1"] else row["political_pole_2"]
    # Model is right if it names the author of the CORRECT proof
    row['model_guessed_right'] = (
        (row["model_response"] == row["name_1"] and row["correct_entity_1"]) or
        (row["model_response"] == row["name_2"] and row["correct_entity_2"]) 
    )
    return row

def derive_political_pole_of_model_response(row):
    if row['model_response'] in ["entity_1", "entity_2"]:
        row = map_entity_response_to_name(row)    
    if row['model_response'] == row['name_1']:
        row['model_response_political_attitude'] = row['political_attitude_1']
    elif row['model_response'] == row['name_2']:
        row['model_response_political_attitude'] = row['political_attitude_2']
    else:
        row['model_response_political_attitude'] = None

    row['model_response_pole'] = POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING.get(row['model_response_political_attitude'], None)
    return row

def derive_positional_response_of_model(row):
    row['model_response_position'] = 'First' if row['model_response'] == row['name_1'] else 'Second' if row['model_response'] == row['name_2'] else None
    return row

def generate_two_different_full_names_initials():
    name_1 = random.choice(COMMON_MALE_NAMES + COMMON_FEMALE_NAMES)[0] + "." + random.choice(COMMON_LAST_NAMES)[0] + "."
    name_2 = random.choice(COMMON_MALE_NAMES + COMMON_FEMALE_NAMES)[0] + "." + random.choice(COMMON_LAST_NAMES)[0] + "."
    while name_2 == name_1:
        name_2 = random.choice(COMMON_MALE_NAMES + COMMON_FEMALE_NAMES)[0] + "." + random.choice(COMMON_LAST_NAMES)[0] + "."
    return name_1, name_2

def generate_n_different_full_names_initials(n):
    names = []
    while len(names) < n:
        name = random.choice(COMMON_MALE_NAMES + COMMON_FEMALE_NAMES)[0] + "." + random.choice(COMMON_LAST_NAMES)[0] + "."
        if name not in names:
            names.append(name)
    return names

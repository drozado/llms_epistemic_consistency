

def configure_experiment_parameters(models, n, custom_model_kwargs={}, random_seed=42):

    #--------------------------------------------------------------------------------------
    # ABSOLUTE EXPERIMENTS
    #--------------------------------------------------------------------------------------

    _absolute_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "path_to_save_model_outputs": "./absolute_experiment",
        "random_seed": random_seed
    }

    academic_abstracts_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    academic_abstracts_absolute_experiment_parameters.update({
        'experiment_name': "academic_abstracts",
        "stimuli_factors": ["abstract"],
        "additional_variables_from_df_to_save": ["academic_discipline", "academic_field"],
    })

    code_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    code_absolute_experiment_parameters.update({
        'experiment_name': "code",
        "stimuli_factors": ["code_snippet"],
        "additional_variables_from_df_to_save": ["verdict"],
    })

    logical_reasoning_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    logical_reasoning_absolute_experiment_parameters.update({
        'experiment_name': "logical_reasoning",
        "stimuli_factors": ["premises", "conclusion"],
        "additional_variables_from_df_to_save": ["label"],
    })

    math_proofs_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    math_proofs_absolute_experiment_parameters.update({
        'experiment_name': "math_proofs",
        "stimuli_factors": ["math_problem", "math_proof"],
        "additional_variables_from_df_to_save": ["proof_length"],
    })

    physics_problems_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    physics_problems_absolute_experiment_parameters.update({
        'experiment_name': "physics_problems",
        "stimuli_factors": ["physics_problem", "physics_solution"],
        "additional_variables_from_df_to_save": [],
    })

    factual_vs_false_statement_detection_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    factual_vs_false_statement_detection_absolute_experiment_parameters.update({
        'experiment_name': "factual_vs_false_statement_detection",
        "stimuli_factors": ["statement"],
        "additional_variables_from_df_to_save": ["factual_accuracy"],
    })

    moral_reasoning_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    moral_reasoning_absolute_experiment_parameters.update({
        'experiment_name': "moral_reasoning",
        "stimuli_factors": ["behavior"],
        "additional_variables_from_df_to_save": ["category"],
    })

    cvs_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    cvs_absolute_experiment_parameters.update({
        'experiment_name': "cvs",
        "stimuli_factors": ["job_description", "cv"],
        "additional_variables_from_df_to_save": ["profession"],
    })

    # Art experiment uses images and text data, so it has slightly different parameters
    art_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    art_absolute_experiment_parameters.update({
        'experiment_name': "art",
        "data_path": "./data",
    })

    judicial_decisions_absolute_experiment_parameters = _absolute_experiment_parameters.copy()
    judicial_decisions_absolute_experiment_parameters.update({
        'experiment_name': "judicial_decisions",
        "stimuli_factors": ["judicial_decision"],
        "additional_variables_from_df_to_save": ["party_to_prevail"],
    })


    #--------------------------------------------------------------------------------------
    # COMPARATIVE EXPERIMENTS WITH GROUND TRUTH PARAMETERS
    #--------------------------------------------------------------------------------------

    _comparative_experiment_with_ground_truth_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "path_to_save_model_outputs": "./comparative_experiment_with_ground_truth",
        "random_seed": random_seed,
        "additional_variables_from_df_to_save": [],
    }

    code_with_ground_truth_experiment_parameters = _comparative_experiment_with_ground_truth_parameters.copy()
    code_with_ground_truth_experiment_parameters.update({
        'experiment_name': "code",
        "stimuli_factors": ["code_snippet"],
    })

    logical_reasoning_with_ground_truth_experiment_parameters = _comparative_experiment_with_ground_truth_parameters.copy()
    logical_reasoning_with_ground_truth_experiment_parameters.update({
        'experiment_name': "logical_reasoning",
        "stimuli_factors": ["premises", "conclusion"],
    })

    math_proofs_with_ground_truth_experiment_parameters = _comparative_experiment_with_ground_truth_parameters.copy()
    math_proofs_with_ground_truth_experiment_parameters.update({
        'experiment_name': "math_proofs",
        "stimuli_factors": ["math_problem", "math_proof"],
        "additional_variables_from_df_to_save": ["proof_length"],
    })

    physics_problems_with_ground_truth_experiment_parameters = _comparative_experiment_with_ground_truth_parameters.copy()
    physics_problems_with_ground_truth_experiment_parameters.update({
        'experiment_name': "physics_problems",
        "stimuli_factors": ["physics_problem", "physics_solution"],
    })

    factual_vs_false_statement_detection_with_ground_truth_experiment_parameters = _comparative_experiment_with_ground_truth_parameters.copy()
    factual_vs_false_statement_detection_with_ground_truth_experiment_parameters.update({
        'experiment_name': "factual_vs_false_statement_detection",
        "stimuli_factors": ["statement"],
    })


    #--------------------------------------------------------------------------------------
    # COMPARATIVE EXPERIMENTS WITHOUT GROUND TRUTH PARAMETERS
    #--------------------------------------------------------------------------------------
    _comparative_experiment_without_ground_truth_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "path_to_save_model_outputs": "./comparative_experiment_without_ground_truth",
        "random_seed": random_seed,
        "additional_variables_from_df_to_save": [],
    }

    academic_abstracts_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    academic_abstracts_without_ground_truth_experiment_parameters.update({
        'experiment_name': "academic_abstracts",
        "stimuli_factors": ["abstract"],
        "additional_variables_from_df_to_save": ["academic_discipline", "academic_field"],
    })

    code_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    code_without_ground_truth_experiment_parameters.update({
        'experiment_name': "code",
        "stimuli_factors": ["code_snippet"],
    })

    logical_reasoning_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    logical_reasoning_without_ground_truth_experiment_parameters.update({
        'experiment_name': "logical_reasoning",
        "stimuli_factors": ["premises", "conclusion"],
    })

    math_proofs_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    math_proofs_without_ground_truth_experiment_parameters.update({
        'experiment_name': "math_proofs",
        "stimuli_factors": ["math_problem", "math_proof"],
        "additional_variables_from_df_to_save": ["proof_length"],
    })

    physics_problems_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    physics_problems_without_ground_truth_experiment_parameters.update({
        'experiment_name': "physics_problems",
        "stimuli_factors": ["physics_problem", "physics_solution"],
    })

    factual_vs_false_statement_detection_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    factual_vs_false_statement_detection_without_ground_truth_experiment_parameters.update({
        'experiment_name': "factual_vs_false_statement_detection",
        "stimuli_factors": ["statement"],
        "additional_variables_from_df_to_save": ["factual_accuracy"],
    })

    moral_reasoning_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    moral_reasoning_without_ground_truth_experiment_parameters.update({
        'experiment_name': "moral_reasoning",
        "stimuli_factors": ["behavior"],
        "additional_variables_from_df_to_save": ["category"],
    })

    cvs_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    cvs_without_ground_truth_experiment_parameters.update({
        'experiment_name': "cvs",
        "stimuli_factors": ["cv", "job_description"],
        "additional_variables_from_df_to_save": ["profession"],
    })

    # art experiment uses images, so it has slightly different parameters
    art_without_ground_truth_experiment_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    del art_without_ground_truth_experiment_parameters["additional_variables_from_df_to_save"]
    art_without_ground_truth_experiment_parameters.update({
        'experiment_name': "art",
        "data_path": "./data",
    })

    judicial_decisions_comparative_experiment_without_ground_truth_parameters = _comparative_experiment_without_ground_truth_parameters.copy()
    judicial_decisions_comparative_experiment_without_ground_truth_parameters.update({
        'experiment_name': "judicial_decisions",
        "stimuli_factors": ["judicial_decision"],
        "additional_variables_from_df_to_save": ["party_to_prevail"],
    })


    #--------------------------------------------------------------------------------------
    # COMPARATIVE EXPERIMENTS WITH GROUND TRUTH AND MULTIPLE CHOICES PARAMETERS
    #--------------------------------------------------------------------------------------

    _comparative_experiment_with_ground_truth_and_multiple_choices_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "path_to_save_model_outputs": "./comparative_experiment_with_ground_truth_and_multiple_choices",
        "random_seed": random_seed,
        "additional_variables_from_df_to_save": [],
        "number_of_choices": 5,
    }

    code_with_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_with_ground_truth_and_multiple_choices_parameters.copy()
    code_with_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "code",
        "stimuli_factors": ["code_snippet"],
    })

    logical_reasoning_with_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_with_ground_truth_and_multiple_choices_parameters.copy()
    logical_reasoning_with_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "logical_reasoning",
        "stimuli_factors": ["premises", "conclusion"],
    })

    math_proofs_with_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_with_ground_truth_and_multiple_choices_parameters.copy()
    math_proofs_with_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "math_proofs",
        "stimuli_factors": ["math_problem", "math_proof"],
    })

    physics_problems_with_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_with_ground_truth_and_multiple_choices_parameters.copy()
    physics_problems_with_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "physics_problems",
        "stimuli_factors": ["physics_problem", "physics_solution"],
    })

    factual_vs_false_statement_detection_with_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_with_ground_truth_and_multiple_choices_parameters.copy()
    factual_vs_false_statement_detection_with_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "factual_vs_false_statement_detection",
        "stimuli_factors": ["statement"],
    })

    #--------------------------------------------------------------------------------------
    # COMPARATIVE EXPERIMENTS WITHOUT GROUND TRUTH AND MULTIPLE CHOICES PARAMETERS
    #--------------------------------------------------------------------------------------

    _comparative_experiment_without_ground_truth_and_multiple_choices_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "path_to_save_model_outputs": "./comparative_experiment_without_ground_truth_and_multiple_choices",
        "random_seed": random_seed,
        "additional_variables_from_df_to_save": [],
        "number_of_choices": 5,
    }

    academic_abstracts_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    academic_abstracts_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "academic_abstracts",
        "stimuli_factors": ["abstract"],
        "additional_variables_from_df_to_save": ["academic_discipline", "academic_field"],
    })


    code_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    code_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "code",
        "stimuli_factors": ["code_snippet"],
    })

    logical_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    logical_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "logical_reasoning",
        "stimuli_factors": ["premises", "conclusion"],
    })

    math_proofs_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    math_proofs_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "math_proofs",
        "stimuli_factors": ["math_problem", "math_proof"],
        "additional_variables_from_df_to_save": ["proof_length"],
    })

    physics_problems_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    physics_problems_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "physics_problems",
        "stimuli_factors": ["physics_problem", "physics_solution"],
    })

    factual_vs_false_statement_detection_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    factual_vs_false_statement_detection_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "factual_vs_false_statement_detection",
        "stimuli_factors": ["statement"],
        "additional_variables_from_df_to_save": ["factual_accuracy"],
    })

    moral_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    moral_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "moral_reasoning",
        "stimuli_factors": ["behavior"],
        "additional_variables_from_df_to_save": ["category"],
    })

    cvs_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    cvs_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "cvs",
        "stimuli_factors": ["cv", "job_description"],
        "additional_variables_from_df_to_save": ["profession"],
    })

    # art experiment uses images, so it has slightly different parameters
    art_without_ground_truth_and_multiple_choices_experiment_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    del art_without_ground_truth_and_multiple_choices_experiment_parameters["additional_variables_from_df_to_save"]
    art_without_ground_truth_and_multiple_choices_experiment_parameters.update({
        'experiment_name': "art",
        "data_path": "./data",
    })

    judicial_decisions_comparative_experiment_without_ground_truth_and_multiple_choices_parameters = _comparative_experiment_without_ground_truth_and_multiple_choices_parameters.copy()
    judicial_decisions_comparative_experiment_without_ground_truth_and_multiple_choices_parameters.update({
        'experiment_name': "judicial_decisions",
        "stimuli_factors": ["judicial_decision"],
        "additional_variables_from_df_to_save": ["party_to_prevail"],
    })

   
    #--------------------------------------------------------------------------------------
    # EVALUATE TIME SERIES TRENDS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_time_series_trends_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_time_series_trends",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE RESEARCH DESIGNS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_research_designs_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_research_designs",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE GOVERNMENTS BASED ON COUNTRY METRICS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_governments_based_on_country_metrics_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_governments_based_on_country_metrics",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE NEWS ARTICLES PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_factuality_of_news_articles_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_factuality_of_news_articles",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE POLICY PROPOSALS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_policy_proposals_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_policy_proposals",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE TWO GROUP COMPARISON POLICY EFFECTIVENESS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_two_group_comparison_policy_effectiveness_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_two_group_comparison_policy_effectiveness",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE GOVERNMENTS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_correlation_btw_governments_and_problem_metrics_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_correlation_btw_governments_and_problem_metrics",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE PROTESTS EVENTS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_protesters_behavior_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_protesters_behavior",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE SOCIAL MEDIA POSTS PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_social_media_posts_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_social_media_posts",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    #--------------------------------------------------------------------------------------
    # EVALUATE POLICY EFFECTIVENESS GIVEN CONTINGENCY TABLES PARAMETERS
    #--------------------------------------------------------------------------------------
    evaluate_policy_effectiveness_given_contingency_tables_unblind_experiment_parameters = {
        "models": models,
        "n": n,
        "custom_model_kwargs": custom_model_kwargs,
        "random_seed": random_seed,
        'experiment_name': "evaluate_policy_effectiveness_given_contingency_tables",
        'path_to_save_model_outputs': "./unblind_experiment",
    }

    # Return all experiment parameters as a dictionary
    return {
        "academic_abstracts_absolute_experiment_parameters": academic_abstracts_absolute_experiment_parameters,
        "code_absolute_experiment_parameters": code_absolute_experiment_parameters,
        "logical_reasoning_absolute_experiment_parameters": logical_reasoning_absolute_experiment_parameters,
        "math_proofs_absolute_experiment_parameters": math_proofs_absolute_experiment_parameters,
        "physics_problems_absolute_experiment_parameters": physics_problems_absolute_experiment_parameters,
        "factual_vs_false_statement_detection_absolute_experiment_parameters": factual_vs_false_statement_detection_absolute_experiment_parameters,
        "moral_reasoning_absolute_experiment_parameters": moral_reasoning_absolute_experiment_parameters,
        "cvs_absolute_experiment_parameters": cvs_absolute_experiment_parameters,
        "art_absolute_experiment_parameters": art_absolute_experiment_parameters,
        "judicial_decisions_absolute_experiment_parameters": judicial_decisions_absolute_experiment_parameters,

        "code_with_ground_truth_experiment_parameters": code_with_ground_truth_experiment_parameters,
        "logical_reasoning_with_ground_truth_experiment_parameters": logical_reasoning_with_ground_truth_experiment_parameters,
        "math_proofs_with_ground_truth_experiment_parameters": math_proofs_with_ground_truth_experiment_parameters,
        "physics_problems_with_ground_truth_experiment_parameters": physics_problems_with_ground_truth_experiment_parameters,
        "factual_vs_false_statement_detection_with_ground_truth_experiment_parameters": factual_vs_false_statement_detection_with_ground_truth_experiment_parameters,

        "academic_abstracts_without_ground_truth_experiment_parameters": academic_abstracts_without_ground_truth_experiment_parameters,
        "code_without_ground_truth_experiment_parameters": code_without_ground_truth_experiment_parameters,
        "logical_reasoning_without_ground_truth_experiment_parameters": logical_reasoning_without_ground_truth_experiment_parameters,
        "math_proofs_without_ground_truth_experiment_parameters": math_proofs_without_ground_truth_experiment_parameters,
        "physics_problems_without_ground_truth_experiment_parameters": physics_problems_without_ground_truth_experiment_parameters,
        "factual_vs_false_statement_detection_without_ground_truth_experiment_parameters": factual_vs_false_statement_detection_without_ground_truth_experiment_parameters,
        "moral_reasoning_without_ground_truth_experiment_parameters": moral_reasoning_without_ground_truth_experiment_parameters,
        "cvs_without_ground_truth_experiment_parameters": cvs_without_ground_truth_experiment_parameters,
        "art_without_ground_truth_experiment_parameters": art_without_ground_truth_experiment_parameters,
        "judicial_decisions_comparative_experiment_without_ground_truth_parameters": judicial_decisions_comparative_experiment_without_ground_truth_parameters,

        "code_with_ground_truth_and_multiple_choices_experiment_parameters": code_with_ground_truth_and_multiple_choices_experiment_parameters,
        "logical_reasoning_with_ground_truth_and_multiple_choices_experiment_parameters": logical_reasoning_with_ground_truth_and_multiple_choices_experiment_parameters,
        "math_proofs_with_ground_truth_and_multiple_choices_experiment_parameters": math_proofs_with_ground_truth_and_multiple_choices_experiment_parameters,
        "physics_problems_with_ground_truth_and_multiple_choices_experiment_parameters": physics_problems_with_ground_truth_and_multiple_choices_experiment_parameters,
        "factual_vs_false_statement_detection_with_ground_truth_and_multiple_choices_experiment_parameters": factual_vs_false_statement_detection_with_ground_truth_and_multiple_choices_experiment_parameters,

        "academic_abstracts_without_ground_truth_and_multiple_choices_experiment_parameters": academic_abstracts_without_ground_truth_and_multiple_choices_experiment_parameters,
        "code_without_ground_truth_and_multiple_choices_experiment_parameters": code_without_ground_truth_and_multiple_choices_experiment_parameters,
        "logical_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters": logical_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters,
        "math_proofs_without_ground_truth_and_multiple_choices_experiment_parameters": math_proofs_without_ground_truth_and_multiple_choices_experiment_parameters,
        "physics_problems_without_ground_truth_and_multiple_choices_experiment_parameters": physics_problems_without_ground_truth_and_multiple_choices_experiment_parameters,
        "factual_vs_false_statement_detection_without_ground_truth_and_multiple_choices_experiment_parameters": factual_vs_false_statement_detection_without_ground_truth_and_multiple_choices_experiment_parameters,
        "moral_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters": moral_reasoning_without_ground_truth_and_multiple_choices_experiment_parameters,
        "cvs_without_ground_truth_and_multiple_choices_experiment_parameters": cvs_without_ground_truth_and_multiple_choices_experiment_parameters,
        "art_without_ground_truth_and_multiple_choices_experiment_parameters": art_without_ground_truth_and_multiple_choices_experiment_parameters,
        "judicial_decisions_comparative_experiment_without_ground_truth_and_multiple_choices_parameters": judicial_decisions_comparative_experiment_without_ground_truth_and_multiple_choices_parameters,

        "evaluate_time_series_trends_unblind_experiment_parameters": evaluate_time_series_trends_unblind_experiment_parameters,

        "evaluate_research_designs_unblind_experiment_parameters": evaluate_research_designs_unblind_experiment_parameters,

        "evaluate_governments_based_on_country_metrics_unblind_experiment_parameters": evaluate_governments_based_on_country_metrics_unblind_experiment_parameters,

        "evaluate_factuality_of_news_articles_unblind_experiment_parameters": evaluate_factuality_of_news_articles_unblind_experiment_parameters,

        "evaluate_policy_proposals_unblind_experiment_parameters": evaluate_policy_proposals_unblind_experiment_parameters,

        "evaluate_two_group_comparison_policy_effectiveness_unblind_experiment_parameters": evaluate_two_group_comparison_policy_effectiveness_unblind_experiment_parameters,

        "evaluate_correlation_btw_governments_and_problem_metrics_unblind_experiment_parameters": evaluate_correlation_btw_governments_and_problem_metrics_unblind_experiment_parameters,

        "evaluate_protesters_behavior_unblind_experiment_parameters": evaluate_protesters_behavior_unblind_experiment_parameters,

        "evaluate_social_media_posts_unblind_experiment_parameters": evaluate_social_media_posts_unblind_experiment_parameters,

        "evaluate_policy_effectiveness_given_contingency_tables_unblind_experiment_parameters": evaluate_policy_effectiveness_given_contingency_tables_unblind_experiment_parameters,
    }

        

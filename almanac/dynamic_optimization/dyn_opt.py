import pandas as pd
import numpy as np
from almanac.dynamic_optimization.dyn_opt_with_costs_and_buffering import *
from almanac.dynamic_optimization.dyn_opt_objects_and_functions import *
from almanac.dynamic_optimization.correlation_estimate import *
from almanac.dynamic_optimization.dyn_opt import *
from copy import copy


def dynamically_optimise_positions(
    capital: float,
    fx_series_dict: dict,
    unrounded_position_contracts_dict: dict,
    multipliers: dict,
    std_dev_dict: dict,
    current_prices_dict: dict,
    adjusted_prices_dict: dict,
    cost_per_contract_dict: dict,
    algo_to_use,
) -> dict:

    data_for_optimisation = get_data_for_dynamic_optimisation(
        capital=capital,
        current_prices_dict=current_prices_dict,
        std_dev_dict=std_dev_dict,
        cost_per_contract_dict=cost_per_contract_dict,
        fx_series_dict=fx_series_dict,
        adjusted_prices_dict=adjusted_prices_dict,
        multipliers=multipliers,
        unrounded_position_contracts_dict=unrounded_position_contracts_dict,
    )

    position_list = []
    common_index = data_for_optimisation.common_index
    previous_position = get_initial_positions(
        unrounded_position_contracts_dict)

    for relevant_date in common_index:
        data_for_single_period = get_data_for_relevant_date(
            relevant_date, data_for_optimisation=data_for_optimisation
        )

        optimal_positions = optimisation_for_single_period(
            previous_position=previous_position,
            data_for_single_period=data_for_single_period,
            algo_to_use=algo_to_use,
        )

        position_list.append(optimal_positions)
        previous_position = copy(optimal_positions)

    position_df = pd.DataFrame(position_list, index=common_index)

    # single dataframe but we operate with a dict of series elsewhere
    positions_as_dict = from_df_to_dict_of_series(position_df)

    return positions_as_dict


def optimisation_for_single_period(
    previous_position: positionContracts,
    data_for_single_period: dataForSinglePeriod,
    algo_to_use,
) -> positionContracts:

    assets_with_data = which_assets_have_data(data_for_single_period)
    if len(assets_with_data) == 0:
        return previous_position

    assets_without_data = which_assets_without_data(
        data_for_single_period, assets_with_data=assets_with_data
    )

    data_for_single_period = data_for_single_period_with_valid_assets_only(
        data_for_single_period, assets_with_data=assets_with_data
    )

    previous_position = previous_position.with_selected_assets_only(
        assets_with_data)

    optimised_position = optimisation_for_single_period_with_valid_assets_only(
        previous_position=previous_position,
        data_for_single_period=data_for_single_period,
        algo_to_use=algo_to_use,
    )

    optimised_position_with_all_assets = (
        optimised_position.with_fill_for_missing_assets(assets_without_data)
    )

    return optimised_position_with_all_assets


def optimisation_for_single_period_with_valid_assets_only(
    previous_position: positionContracts,
    data_for_single_period: dataForSinglePeriod,
    algo_to_use,
) -> positionContracts:

    data_for_single_period_with_weights = (
        dataForSinglePeriodWithWeights.from_data_for_single_period(
            previous_position=previous_position,
            data_for_single_period=data_for_single_period,
        )
    )

    optimised_weights = optimisation_of_weight_for_single_period_with_valid_assets_only(
        data_for_single_period_with_weights, algo_to_use=algo_to_use
    )

    weights_per_contract = data_for_single_period_with_weights.weight_per_contract
    optimised_contracts = position_contracts_from_position_weights(
        optimised_weights, weights_per_contract=weights_per_contract
    )

    return optimised_contracts


def optimisation_of_weight_for_single_period_with_valid_assets_only(
    data_for_single_period_with_weights: dataForSinglePeriodWithWeights, algo_to_use
) -> positionWeights:

    data_for_single_period_as_np = (
        dataForSinglePeriodWithWeightsAsNp.from_data_for_single_period_with_weights(
            data_for_single_period_with_weights
        )
    )

    solution_as_np = algo_to_use(data_for_single_period_as_np)

    list_of_assets = list(
        data_for_single_period_with_weights.unrounded_optimal_position_weights.keys()
    )
    solution_as_weights = positionWeights.from_weights_and_keys(
        list_of_keys=list_of_assets, list_of_weights=list(solution_as_np)
    )

    return solution_as_weights


def greedy_algo_across_integer_values(
    data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp,
) -> np.array:
    # step 1
    weight_start = data_for_single_period_as_np.starting_weights

    current_best_value = evaluate_tracking_error(
        weight_start, data_for_single_period_as_np
    )
    current_best_solution = weight_start

    done = False

    while not done:
        # step 3 loop
        (
            new_best_proposed_value,
            new_best_proposed_solution,
        ) = find_best_proposed_solution(
            current_best_solution=current_best_solution,
            current_best_value=current_best_value,
            data_for_single_period_as_np=data_for_single_period_as_np,
        )
        if new_best_proposed_value < current_best_value:
            # reached a new optimium
            # step 6
            current_best_value = new_best_proposed_value
            current_best_solution = new_best_proposed_solution
        else:
            # we can't do any better
            # step 7
            break

    return current_best_solution


def evaluate_tracking_error(
    weights: np.array, data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp
):

    optimal_weights = data_for_single_period_as_np.unrounded_optimal_position_weights
    covariance = data_for_single_period_as_np.covariance_matrix

    return evaluate_tracking_error_for_weights(
        weights, optimal_weights, covariance=covariance
    )


def evaluate_tracking_error_for_weights(
    weights: np.array, other_weights, covariance: np.array
) -> float:

    solution_gap = weights - other_weights
    track_error_var = solution_gap.dot(covariance).dot(solution_gap)

    if track_error_var < 0:
        raise Exception("Negative covariance when optimising!")

    track_error_std = track_error_var**0.5

    return track_error_std


def find_best_proposed_solution(
    current_best_solution: np.array,
    current_best_value: float,
    data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp,
) -> tuple:
    best_proposed_value = copy(current_best_value)
    best_proposed_solution = copy(current_best_solution)

    per_contract_value = data_for_single_period_as_np.weight_per_contract
    direction = data_for_single_period_as_np.direction_as_np

    count_assets = len(best_proposed_solution)
    for i in range(count_assets):
        incremented_solution = copy(current_best_solution)
        incremented_solution[i] = (
            incremented_solution[i] + per_contract_value[i] * direction[i]
        )
        incremented_objective_value = evaluate_tracking_error(
            incremented_solution, data_for_single_period_as_np
        )

        if incremented_objective_value < best_proposed_value:
            best_proposed_value = incremented_objective_value
            best_proposed_solution = incremented_solution

    return best_proposed_value, best_proposed_solution

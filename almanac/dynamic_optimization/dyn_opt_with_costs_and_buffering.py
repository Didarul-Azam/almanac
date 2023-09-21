from almanac.dynamic_optimization.dyn_opt_with_costs_and_buffering import *
from almanac.dynamic_optimization.dyn_opt_objects_and_functions import *
from almanac.dynamic_optimization.correlation_estimate import *
from almanac.dynamic_optimization.dyn_opt import *
import pandas as pd
import numpy as np
from copy import copy


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

    # if track_error_var < 0:
    #     raise Exception("Negative covariance when optimising!")

    track_error_std = track_error_var**0.5

    return track_error_std


def greedy_algo_across_integer_values_with_costs_and_buffering(
    data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp,
) -> np.array:

    optimised_weights = greedy_algo_across_integer_values_with_costs(
        data_for_single_period_as_np
    )

    previous_weights = data_for_single_period_as_np.previous_position_weights
    covariance = data_for_single_period_as_np.covariance_matrix
    per_contract_value = data_for_single_period_as_np.weight_per_contract

    optimised_weights_with_buffering = calculate_optimised_weights_with_buffering(
        optimised_weights, previous_weights, covariance, per_contract_value
    )

    return optimised_weights_with_buffering


def calculate_optimised_weights_with_buffering(
    optimised_weights: np.array,
    previous_weights: np.array,
    covariance: np.array,
    per_contract_value: np.array,
) -> np.array:

    tracking_error_of_prior = evaluate_tracking_error_for_weights(
        previous_weights, optimised_weights, covariance
    )

    adj_factor = calculate_adjustment_factor_given_tracking_error(
        tracking_error_of_prior=tracking_error_of_prior
    )

    if adj_factor <= 0:
        return previous_weights

    new_optimal_weights_as_np = adjust_weights_with_factor(
        optimised_weights=optimised_weights,
        adj_factor=adj_factor,
        per_contract_value=per_contract_value,
        previous_weights=previous_weights,
    )

    return new_optimal_weights_as_np


def calculate_adjustment_factor_given_tracking_error(
    tracking_error_of_prior: float,
) -> float:

    if tracking_error_of_prior <= 0:
        return 0.0

    tracking_error_buffer = 0.01

    excess_tracking_error = tracking_error_of_prior - tracking_error_buffer

    adj_factor = excess_tracking_error / tracking_error_of_prior
    adj_factor = max(adj_factor, 0.0)

    return adj_factor


def adjust_weights_with_factor(
    optimised_weights: np.array,
    previous_weights: np.array,
    per_contract_value: np.array,
    adj_factor: float,
):

    desired_trades_weight_space = optimised_weights - previous_weights
    adjusted_trades_weight_space = adj_factor * desired_trades_weight_space

    rounded_adjusted_trades_as_weights = (
        calculate_adjusting_trades_rounding_in_contract_space(
            adjusted_trades_weight_space=adjusted_trades_weight_space,
            per_contract_value_as_np=per_contract_value,
        )
    )

    new_optimal_weights = previous_weights + rounded_adjusted_trades_as_weights

    return new_optimal_weights


def calculate_adjusting_trades_rounding_in_contract_space(
    adjusted_trades_weight_space: np.array, per_contract_value_as_np: np.array
) -> np.array:

    adjusted_trades_in_contracts = (
        adjusted_trades_weight_space / per_contract_value_as_np
    )
    rounded_adjusted_trades_in_contracts = np.round(
        adjusted_trades_in_contracts)
    rounded_adjusted_trades_as_weights = (
        rounded_adjusted_trades_in_contracts * per_contract_value_as_np
    )

    return rounded_adjusted_trades_as_weights


def greedy_algo_across_integer_values_with_costs(
    data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp,
) -> np.array:

    # step 1
    weight_start = data_for_single_period_as_np.starting_weights

    current_best_value = evaluate_with_costs_and_buffering(
        weight_start, data_for_single_period_as_np
    )
    current_best_solution = weight_start

    done = False

    while not done:
        # step 3 loop
        (
            new_best_proposed_value,
            new_best_proposed_solution,
        ) = find_best_proposed_solution_with_costs_and_buffering(
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


def evaluate_with_costs_and_buffering(
    weights: np.array, data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp
) -> float:

    tracking_error = evaluate_tracking_error(
        weights, data_for_single_period_as_np)
    cost_penalty = calculate_cost_penalty(
        weights, data_for_single_period_as_np)

    return tracking_error + cost_penalty


def calculate_cost_penalty(
    weights: np.array, data_for_single_period_as_np: dataForSinglePeriodWithWeightsAsNp
) -> float:

    trades_as_weights = weights - data_for_single_period_as_np.previous_position_weights
    cost_of_each_trade = np.abs(
        trades_as_weights * data_for_single_period_as_np.cost_in_weight_terms_as_np
    )

    return 50.0 * np.sum(cost_of_each_trade)


def find_best_proposed_solution_with_costs_and_buffering(
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
        incremented_objective_value = evaluate_with_costs_and_buffering(
            incremented_solution, data_for_single_period_as_np
        )

        if incremented_objective_value < best_proposed_value:
            best_proposed_value = incremented_objective_value
            best_proposed_solution = incremented_solution

    return best_proposed_value, best_proposed_solution

import pandas as pd
import numpy as np
from almanac.utils.standardDeviation import standardDeviation
from typing import Union
from almanac.analysis.cost_calculation import calculate_costs_deflated_for_vol

def calculate_perc_returns(position_contracts_held: pd.Series,
                           adjusted_price: pd.Series,
                           fx_series: pd.Series,
                           multiplier: float,
                           capital_required: pd.Series,
                           ) -> pd.Series:

    return_price_points = (
        adjusted_price - adjusted_price.shift(1))*position_contracts_held.shift(1)

    return_instrument_currency = return_price_points * multiplier
    fx_series_aligned = fx_series.reindex(
        return_instrument_currency.index, method="ffill")
    return_base_currency = return_instrument_currency * fx_series_aligned

    perc_return = return_base_currency / capital_required

    return perc_return


def calculate_percentage_returns(
    adjusted_price: pd.Series, current_price: pd.Series
) -> pd.Series:

    daily_price_changes = calculate_daily_returns(adjusted_price)
    percentage_changes = daily_price_changes / current_price.shift(1)

    return percentage_changes


def calculate_daily_returns(adjusted_price: pd.Series) -> pd.Series:

    return adjusted_price.diff()


def calculate_perc_returns_with_costs(
    position_contracts_held: pd.Series,
    adjusted_price: pd.Series,
    fx_series: pd.Series,
    stdev_series: standardDeviation,
    multiplier: float,
    capital_required: float,
    cost_per_contract: float,
) -> pd.Series:
    precost_return_price_points = (
        adjusted_price - adjusted_price.shift(1)
    ) * position_contracts_held.shift(1)

    precost_return_instrument_currency = precost_return_price_points * multiplier
    historic_costs = calculate_costs_deflated_for_vol(
        stddev_series=stdev_series,
        cost_per_contract=cost_per_contract,
        position_contracts_held=position_contracts_held,
    )

    historic_costs_aligned = historic_costs.reindex(
        precost_return_instrument_currency.index, method="ffill"
    )
    return_instrument_currency = (
        precost_return_instrument_currency - historic_costs_aligned
    )

    fx_series_aligned = fx_series.reindex(
        return_instrument_currency.index, method="ffill"
    )
    return_base_currency = return_instrument_currency * fx_series_aligned

    perc_return = return_base_currency / capital_required

    return perc_return

def calculate_perc_returns_for_dict_with_costs(
    position_contracts_dict: dict,
    adjusted_prices: dict,
    multipliers: dict,
    fx_series: dict,
    capital: float,
    cost_per_contract_dict: dict,
    std_dev_dict: dict,
) -> dict:

    perc_returns_dict = dict(
        [
            (
                instrument_code,
                calculate_perc_returns_with_costs(
                    position_contracts_held=position_contracts_dict[instrument_code],
                    adjusted_price=adjusted_prices[instrument_code],
                    multiplier=multipliers[instrument_code],
                    fx_series=fx_series[instrument_code],
                    capital_required=capital,
                    cost_per_contract=cost_per_contract_dict[instrument_code],
                    stdev_series=std_dev_dict[instrument_code],
                ),
            )
            for instrument_code in position_contracts_dict.keys()
        ]
    )

    return perc_returns_dict


def calculate_returns_perc_dict(
    position_contracts_dict: dict,
    adjusted_prices: dict,
    multipliers: dict,
    fx_series: dict,
    capital: float,
    cost_per_contract_dict: dict,
    std_dev_dict: dict,
) -> dict:
    perc_returns_dict_with_costs = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=position_contracts_dict,
        adjusted_prices=adjusted_prices,
        multipliers=multipliers,
        fx_series=fx_series,
        capital=capital,
        cost_per_contract_dict=cost_per_contract_dict,
        std_dev_dict=std_dev_dict,
    )
    zero_cost_dict = {
        instrument_code: 0
        for instrument_code in position_contracts_dict.keys()
    }
    perc_returns_dict_without_costs = calculate_perc_returns_for_dict_with_costs(
        position_contracts_dict=position_contracts_dict,
        adjusted_prices=adjusted_prices,
        multipliers=multipliers,
        fx_series=fx_series,
        capital=capital,
        cost_per_contract_dict=zero_cost_dict,
        std_dev_dict=std_dev_dict,
    )
    return perc_returns_dict_without_costs, perc_returns_dict_with_costs


def calculate_perc_returns_for_dict(
    position_contracts_dict: dict,
    adjusted_prices: dict,
    multipliers: dict,
    fx_series: dict,
    capital: float,
) -> dict:

    perc_returns_dict = dict(
        [
            (
                instrument_code,
                calculate_perc_returns(
                    position_contracts_held=position_contracts_dict[instrument_code],
                    adjusted_price=adjusted_prices[instrument_code],
                    multiplier=multipliers[instrument_code],
                    fx_series=fx_series[instrument_code],
                    capital_required=capital,
                ),
            )
            for instrument_code in position_contracts_dict.keys()
        ]
    )

    return perc_returns_dict


def aggregate_returns(perc_returns_dict: dict) -> pd.Series:
    both_returns = perc_returns_to_df(perc_returns_dict)
    agg = both_returns.sum(axis=1)
    return agg


def perc_returns_to_df(perc_returns_dict: dict) -> pd.DataFrame:
    both_returns = pd.concat(perc_returns_dict, axis=1)
    both_returns = both_returns.dropna(how="all")

    return both_returns

class ArgumentError(Exception):
    pass

def calculate_returns(
    position_contracts: Union[dict,pd.Series],
    adjusted_prices: Union[dict,pd.Series],
    multipliers: Union[dict,float],
    fx_series: Union[dict,pd.Series],
    capital: float,
    cost_per_contract: Union[dict,float],
    std_dev: Union[dict,standardDeviation],
    aggregate = True,
): 
    if isinstance(position_contracts,dict):
        if aggregate:
            pre_cost_returns_dict,post_cost_returns_dict = calculate_returns_perc_dict(
                position_contracts_dict = position_contracts,
                adjusted_prices= adjusted_prices,
                multipliers = multipliers,
                fx_series = fx_series,
                capital = capital,
                cost_per_contract_dict =cost_per_contract,
                std_dev_dict = std_dev,
            )
            pre_cost_portfolio_returns = aggregate_returns(pre_cost_returns_dict)
            post_cost_portfolio_returns = aggregate_returns(post_cost_returns_dict)
            return pre_cost_portfolio_returns,post_cost_portfolio_returns
        else:
            pre_cost_returns_dict,post_cost_returns_dict = calculate_returns_perc_dict(
                position_contracts_dict = position_contracts,
                adjusted_prices= adjusted_prices,
                multipliers = multipliers,
                fx_series = fx_series,
                capital = capital,
                cost_per_contract_dict =cost_per_contract,
                std_dev_dict = std_dev,
            )
            return pre_cost_returns_dict,post_cost_returns_dict
    elif isinstance(position_contracts, pd.Series):
        pre_cost_returns = calculate_perc_returns_with_costs(
            position_contracts_held = position_contracts,
            adjusted_price = adjusted_prices ,
            fx_series = fx_series,
            stdev_series= std_dev,
            multiplier = multipliers ,
            capital_required = capital,
            cost_per_contract = 0,
        )
        post_cost_returns = calculate_perc_returns_with_costs(
            position_contracts_held = position_contracts,
            adjusted_price = adjusted_prices ,
            fx_series = fx_series,
            stdev_series= std_dev,
            multiplier = multipliers ,
            capital_required = capital,
            cost_per_contract = cost_per_contract ,
        )
        return pre_cost_returns,post_cost_returns

    else:
        # Raise an ArgumentError with a custom error message
        raise ArgumentError("Position must be a Pandas Series or a dictionary")    
    
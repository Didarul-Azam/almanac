import numpy as np
import pandas as pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.config.instruments import cost_per_contract_dict

def calculate_costs_deflated_for_vol(
    stddev_series: standardDeviation,
    cost_per_contract: float,
    position_contracts_held: pd.Series,
) -> pd.Series:
    round_position_contracts_held = position_contracts_held.round()
    position_change = (
        round_position_contracts_held - round_position_contracts_held.shift(1)
    )
    abs_trades = position_change.abs()

    historic_cost_per_contract = calculate_deflated_costs(
        stddev_series=stddev_series, cost_per_contract=cost_per_contract
    )

    historic_cost_per_contract_aligned = historic_cost_per_contract.reindex(
        abs_trades.index, method="ffill"
    )

    historic_costs = abs_trades * historic_cost_per_contract_aligned

    return historic_costs


def calculate_deflated_costs(
    stddev_series: standardDeviation, cost_per_contract: float
) -> pd.Series:
    stdev_daily_price = stddev_series.daily_risk_price_terms()

    final_stdev = stdev_daily_price[-1]
    cost_deflator = stdev_daily_price / final_stdev
    historic_cost_per_contract = cost_per_contract * cost_deflator

    return historic_cost_per_contract


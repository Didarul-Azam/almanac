import pandas as pd
from scipy.interpolate import interp1d
from almanac.utils.standardDeviation import standardDeviation
from almanac.config.configs import *
from almanac.analysis.forecasts import ewmac,calculate_combined_forecast
from copy import copy

def calculate_position_dict_with_forecast_applied(
    adjusted_prices_dict: dict,
    average_position_contracts_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,
    rule_spec: list,
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    position_dict_with_carry = dict(
        [
            (
                instrument_code,
                calculate_position_with_forecast_applied(
                    average_position=average_position_contracts_dict[instrument_code],
                    stdev_ann_perc=std_dev_dict[instrument_code],
                    carry_price=carry_prices_dict[instrument_code],
                    adjusted_price=adjusted_prices_dict[instrument_code],
                    rule_spec=rule_spec,
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return position_dict_with_carry

def calculate_position_with_forecast_applied(
    average_position: pd.Series,
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    adjusted_price: pd.Series,
    rule_spec: list,
) -> pd.Series:

    forecast = calculate_combined_forecast(
        adjusted_price=adjusted_price,
        stdev_ann_perc=stdev_ann_perc,
        carry_price=carry_price,
        rule_spec=rule_spec,
    )

    return forecast * average_position / 10


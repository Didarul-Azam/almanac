import pandas as pd
import numpy as np


def calculate_perc_returns(
    position_contracts_held: pd.Series,
    adjusted_price: pd.Series,
    fx_series: pd.Series,
    multiplier: float,
    capital_required: pd.Series,
) -> pd.Series:
    return_price_points = (
        adjusted_price - adjusted_price.shift(1)
    ) * position_contracts_held.shift(1)

    return_instrument_currency = return_price_points * multiplier
    fx_series_aligned = fx_series.reindex(
        return_instrument_currency.index, method="ffill"
    )
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

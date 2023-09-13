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


def calculate_variable_standard_deviation_for_risk_targeting(
    adjusted_price: pd.Series,
    current_price: pd.Series,
    use_perc_returns: bool = True,
    annualise_stdev: bool = True,
) -> pd.Series:

    if use_perc_returns:
        daily_returns = calculate_percentage_returns(
            adjusted_price=adjusted_price, current_price=current_price
        )
    else:
        daily_returns = calculate_daily_returns(adjusted_price=adjusted_price)

    # Can do the whole series or recent history
    daily_exp_std_dev = daily_returns.ewm(span=32).std()

    if annualise_stdev:
        annualisation_factor = BUSINESS_DAYS_IN_YEAR ** 0.5
    else:
        # leave at daily
        annualisation_factor = 1

    annualised_std_dev = daily_exp_std_dev * annualisation_factor

    # Weight with ten year vol
    ten_year_vol = annualised_std_dev.rolling(
        BUSINESS_DAYS_IN_YEAR * 10, min_periods=1
    ).mean()
    weighted_vol = 0.3 * ten_year_vol + 0.7 * annualised_std_dev

    return weighted_vol

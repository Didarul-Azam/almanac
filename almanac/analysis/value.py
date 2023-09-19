import pandas as pd
from almanac.config.configs import *
from almanac.data.relative_price import calculate_relative_price_dict
from almanac.analysis.asset_class import asset_class_groupings


def value(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,  # not used
    horizon_years: int,
    smooth: int = 32,
    scalar: float = 7.27,
) -> pd.Series:

    relative_price_dict = calculate_relative_price_dict(
        std_dev_dict=std_dev_dict,
        adjusted_prices_dict=adjusted_prices_dict,
        asset_class_groupings=asset_class_groupings,
    )

    value_forecast = calculate_forecast_for_value(
        relative_price=relative_price_dict[instrument_code],
        horizon_years=horizon_years,
        scalar=scalar,
        smooth=smooth,
    )

    return value_forecast


def calculate_forecast_for_value(
    relative_price: pd.Series,
    horizon_years: int,
    smooth: int = 32,
    scalar: float = 7.27,
) -> pd.Series:

    horizon_days = BUSINESS_DAYS_IN_YEAR * horizon_years
    outperformance = (relative_price - relative_price.shift(horizon_days)) / (
        horizon_days
    )
    forecast = -outperformance
    smoothed_forecast = forecast.ewm(smooth, min_periods=1).mean()

    return smoothed_forecast * scalar

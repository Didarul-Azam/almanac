import numpy as np
import pandas as pd


def breakout(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,  # not used
    carry_prices_dict: dict,  # not used
    scalar: float = 1.0,
    horizon: int = 10,
) -> pd.Series:

    breakout_forecast = calculate_forecast_for_breakout(
        adjusted_price=adjusted_prices_dict[instrument_code],
        horizon=horizon,
        scalar=scalar,
    )

    return breakout_forecast


def calculate_forecast_for_breakout(
    adjusted_price: pd.Series, horizon: int = 10, scalar: float = 1.0
) -> pd.Series:

    max_price = adjusted_price.rolling(horizon, min_periods=1).max()
    min_price = adjusted_price.rolling(horizon, min_periods=1).min()
    mean_price = (max_price + min_price) / 2
    raw_forecast = 40 * (adjusted_price - mean_price) / (max_price - min_price)
    smoothed_forecast = raw_forecast.ewm(span=int(np.ceil(horizon / 4))).mean()

    return smoothed_forecast * scalar

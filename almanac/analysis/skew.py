from almanac.analysis.forecasts import calculate_forecast_for_skew
import pandas as pd

def skew(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,  ## not used
    carry_prices_dict: dict,  ## not used
    horizon: int = 60,
    scalar: float = 33.3,
) -> pd.Series:

    skew_forecast = calculate_forecast_for_skew(
        adjusted_price=adjusted_prices_dict[instrument_code],
        instrument_risk=std_dev_dict[instrument_code],
        scalar=scalar,
        horizon=horizon,
    )

    return skew_forecast
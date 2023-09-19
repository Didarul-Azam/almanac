import pandas as pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.analysis.forecasts import calculate_scaled_forecast_for_ewmac

def accel(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,  ## not used
    fast_span: int = 32,
    scalar: float = 7.27,
) -> pd.Series:

    accel_forecast = calculate_forecast_for_accel(
        adjusted_price=adjusted_prices_dict[instrument_code],
        stdev_ann_perc=std_dev_dict[instrument_code],
        scalar=scalar,
        fast_span=fast_span,
    )

    return accel_forecast


def calculate_forecast_for_accel(
    adjusted_price: pd.Series,
    stdev_ann_perc: standardDeviation,
    scalar: float,
    fast_span: int = 64,
) -> pd.Series:

    ## this returns a scaled forecast, but not capped
    ewmac_forecast = calculate_scaled_forecast_for_ewmac(
        adjusted_price=adjusted_price,
        stdev_ann_perc=stdev_ann_perc,
        fast_span=fast_span,
    )

    accel_raw_forecast = ewmac_forecast - ewmac_forecast.shift(fast_span)
    scaled_accel_forecast = accel_raw_forecast * scalar
    capped_accel_forecast = scaled_accel_forecast.clip(-20, 20)

    return capped_accel_forecast
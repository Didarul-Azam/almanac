import pandas as pd
from almanac.utils.standardDeviation import standardDeviation


def ewmac(adjusted_price: pd.Series, fast_span=16, slow_span=64) -> pd.Series:

    slow_ewma = adjusted_price.ewm(span=slow_span, min_periods=2).mean()
    fast_ewma = adjusted_price.ewm(span=fast_span, min_periods=2).mean()

    return fast_ewma - slow_ewma


def calculate_forecast_for_ewmac(
    adjusted_price: pd.Series, stdev_ann_perc: standardDeviation, fast_span: int = 64
):

    scaled_ewmac = calculate_scaled_forecast_for_ewmac(
        adjusted_price=adjusted_price,
        stdev_ann_perc=stdev_ann_perc,
        fast_span=fast_span,
    )
    capped_ewmac = scaled_ewmac.clip(-20, 20)

    return capped_ewmac

def calculate_scaled_forecast_for_ewmac(
    adjusted_price: pd.Series,
    stdev_ann_perc: standardDeviation,
    fast_span: int = 64,
):

    scalar_dict = {64: 1.91, 32: 2.79, 16: 4.1, 8: 5.95, 4: 8.53, 2: 12.1}
    risk_adjusted_ewmac = calculate_risk_adjusted_forecast_for_ewmac(
        adjusted_price=adjusted_price,
        stdev_ann_perc=stdev_ann_perc,
        fast_span=fast_span,
    )
    forecast_scalar = scalar_dict[fast_span]
    scaled_ewmac = risk_adjusted_ewmac * forecast_scalar

    return scaled_ewmac

def calculate_risk_adjusted_forecast_for_ewmac(
    adjusted_price: pd.Series,
    stdev_ann_perc: standardDeviation,
    fast_span: int = 64,
):

    ewmac_values = ewmac(adjusted_price, fast_span=fast_span, slow_span=fast_span * 4)
    daily_price_vol = stdev_ann_perc.daily_risk_price_terms()

    risk_adjusted_ewmac = ewmac_values / daily_price_vol

    return risk_adjusted_ewmac

def calculate_combined_ewmac_forecast(
    adjusted_price: pd.Series,
    stdev_ann_perc: standardDeviation,
    fast_spans: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_for_ewmac(
            adjusted_price=adjusted_price,
            stdev_ann_perc=stdev_ann_perc,
            fast_span=fast_span,
        )
        for fast_span in fast_spans
    ]

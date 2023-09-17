import pandas as pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.config.fdm_lst import get_fdm

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

    ewmac_values = ewmac(
        adjusted_price, fast_span=fast_span, slow_span=fast_span * 4)
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

    # NOTE: This assumes we are equally weighted across spans
    # eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    # apply an FDM
    rule_count = len(fast_spans)
    FDM_DICT = {1: 1.0, 2: 1.03, 3: 1.08, 4: 1.13, 5: 1.19, 6: 1.26}
    fdm = FDM_DICT[rule_count]

    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast



def calculate_combined_carry_forecast(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    carry_spans: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_for_carry(
            stdev_ann_perc=stdev_ann_perc,
            carry_price=carry_price,
            span=span,
        )
        for span in carry_spans
    ]

    ### NOTE: This assumes we are equally weighted across spans
    ### eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    ## apply an FDM
    rule_count = len(carry_spans)
    FDM_DICT = {1: 1.0, 2: 1.02, 3: 1.03, 4: 1.04}
    fdm = FDM_DICT[rule_count]

    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast


def calculate_forecast_for_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame, span: int
):
    from almanac.analysis.carry import calculate_smoothed_carry
    smooth_carry = calculate_smoothed_carry(
        stdev_ann_perc=stdev_ann_perc, carry_price=carry_price, span=span
    )
    scaled_carry = smooth_carry * 30
    capped_carry = scaled_carry.clip(-20, 20)

    return capped_carry

def calculate_combined_forecast(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    adjusted_price: pd.Series,
    rule_spec: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast(
            adjusted_price=adjusted_price,
            stdev_ann_perc=stdev_ann_perc,
            carry_price=carry_price,
            rule=rule,
        )
        for rule in rule_spec
    ]

    ### NOTE: This assumes we are equally weighted across spans
    ### eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    ## apply an FDM
    rule_count = len(rule_spec)
    fdm = get_fdm(rule_count)
    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast

def calculate_forecast(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    adjusted_price: pd.Series,
    rule: dict,
) -> pd.Series:

    if rule["function"] == "carry":
        span = rule["span"]
        forecast = calculate_forecast_for_carry(
            stdev_ann_perc=stdev_ann_perc, carry_price=carry_price, span=span
        )

    elif rule["function"] == "ewmac":
        fast_span = rule["fast_span"]
        forecast = calculate_forecast_for_ewmac(
            adjusted_price=adjusted_price,
            stdev_ann_perc=stdev_ann_perc,
            fast_span=fast_span,
        )
    else:
        raise Exception("Rule %s not recognised!" % rule["function"])

    return forecast
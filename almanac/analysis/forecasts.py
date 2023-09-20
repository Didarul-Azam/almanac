import pandas as pd
from copy import copy
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

    # NOTE: This assumes we are equally weighted across spans
    # eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    # apply an FDM
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

    # NOTE: This assumes we are equally weighted across spans
    # eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    # apply an FDM
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


def calculate_combined_ewmac_forecast_and_adjustment(
    adjusted_price: pd.Series, stdev_ann_perc: standardDeviation, fast_spans: list
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_for_ewmac_and_adjustment(
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


def calculate_forecast_for_ewmac_and_adjustment(
    adjusted_price: pd.Series, stdev_ann_perc: standardDeviation, fast_span: int = 64
):

    scalar_dict = {64: 1.91, 32: 2.79, 16: 4.1, 8: 5.95, 4: 8.53, 2: 12.1}
    ewmac_values = ewmac(
        adjusted_price, fast_span=fast_span, slow_span=fast_span * 4)
    daily_price_vol = stdev_ann_perc.daily_risk_price_terms()
    risk_adjusted_ewmac = ewmac_values / daily_price_vol
    forecast_scalar = scalar_dict[fast_span]
    scaled_ewmac = risk_adjusted_ewmac * forecast_scalar

    if fast_span == 2:
        capped_ewmac = double_v(scaled_ewmac)
    elif fast_span == 4 or fast_span == 64:
        capped_ewmac = scale_and_cap(scaled_ewmac)
    else:
        capped_ewmac = scaled_ewmac.clip(-20, 20)

    return capped_ewmac


def double_v(scaled_forecast: pd.Series) -> pd.Series:
    new_forecast = copy(scaled_forecast)
    new_forecast[scaled_forecast > 20] = 0
    new_forecast[scaled_forecast < -20] = 0
    new_forecast[(scaled_forecast >= -20) & (scaled_forecast < -10)] = (
        new_forecast[(scaled_forecast >= -20) & (scaled_forecast < -10)] * -2
    ) - 40
    new_forecast[(scaled_forecast >= -10) & (scaled_forecast < 10)] = (
        new_forecast[(scaled_forecast >= -10) & (scaled_forecast < +10)] * 2
    )

    new_forecast[(scaled_forecast >= 10) & (scaled_forecast < 20)] = (
        new_forecast[(scaled_forecast >= 10) & (scaled_forecast < +20)] * -2
    ) + 40

    return new_forecast


def scale_and_cap(scaled_forecast: pd.Series) -> pd.Series:
    rescaled_forecast = 1.25 * scaled_forecast
    capped_forecast = rescaled_forecast.clip(-1.25 * 15, 1.25 * 15)

    return capped_forecast


def calculate_combined_forecast_with_vol_scalar_applied(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    adjusted_price: pd.Series,
    rule_spec: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_with_vol_scalar_applied(
            adjusted_price=adjusted_price,
            stdev_ann_perc=stdev_ann_perc,
            carry_price=carry_price,
            rule=rule,
        )
        for rule in rule_spec
    ]

    # NOTE: This assumes we are equally weighted across spans
    # eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    # apply an FDM
    rule_count = len(rule_spec)
    fdm = get_fdm(rule_count)
    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast


def calculate_forecast_with_vol_scalar_applied(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    adjusted_price: pd.Series,
    rule: dict,
) -> pd.Series:

    if rule["function"] == "carry":
        span = rule["span"]
        forecast = calculate_forecast_for_carry_with_optional_vol_scaling(
            stdev_ann_perc=stdev_ann_perc, carry_price=carry_price, span=span
        )

    elif rule["function"] == "ewmac":
        fast_span = rule["fast_span"]
        forecast = calculate_forecast_for_ewmac_with_optional_vol_scaling(
            adjusted_price=adjusted_price,
            stdev_ann_perc=stdev_ann_perc,
            fast_span=fast_span,
        )

    else:
        raise Exception("Rule %s not recognised!" % rule["function"])

    return forecast


def calculate_forecast_for_carry_with_optional_vol_scaling(
    stdev_ann_perc: standardDeviation,
    carry_price: pd.DataFrame,
    span: int,
    APPLY_VOL_REGIME_TO_CARRY: bool = False
):
    from almanac.analysis.carry import calculate_smoothed_carry

    smooth_carry = calculate_smoothed_carry(
        stdev_ann_perc=stdev_ann_perc,
        carry_price=carry_price,
        span=span,
    )
    if APPLY_VOL_REGIME_TO_CARRY:
        smooth_carry = apply_vol_regime_to_forecast(
            smooth_carry, stdev_ann_perc=stdev_ann_perc
        )
        scaled_carry = smooth_carry * 23
    else:
        scaled_carry = smooth_carry * 30

    capped_carry = scaled_carry.clip(-20, 20)

    return capped_carry


def calculate_forecast_for_ewmac_with_optional_vol_scaling(
    adjusted_price: pd.Series,
    stdev_ann_perc: standardDeviation,
    fast_span: int = 64,
    APPLY_VOL_REGIME_TO_EWMAC: bool = True
):

    scalar_dict = {64: 1.91, 32: 2.79, 16: 4.1, 8: 5.95, 4: 8.53, 2: 12.1}
    risk_adjusted_ewmac = calculate_risk_adjusted_forecast_for_ewmac(
        adjusted_price=adjusted_price,
        stdev_ann_perc=stdev_ann_perc,
        fast_span=fast_span,
    )
    if APPLY_VOL_REGIME_TO_EWMAC:
        risk_adjusted_ewmac = apply_vol_regime_to_forecast(
            risk_adjusted_ewmac, stdev_ann_perc=stdev_ann_perc
        )

    forecast_scalar = scalar_dict[fast_span]
    scaled_ewmac = risk_adjusted_ewmac * forecast_scalar
    capped_ewmac = scaled_ewmac.clip(-20, 20)

    return capped_ewmac


def apply_vol_regime_to_forecast(
    scaled_forecast: pd.Series, stdev_ann_perc: pd.Series
) -> pd.Series:
    from almanac.utils.utils import get_attenuation
    smoothed_vol_attenuation = get_attenuation(stdev_ann_perc)
    return scaled_forecast * smoothed_vol_attenuation


def calculate_combined_forecast_from_functions(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,
    list_of_rules: list,
) -> pd.Series:

    all_forecasts_as_list = [
        calculate_forecast_from_function(
            instrument_code=instrument_code,
            adjusted_prices_dict=adjusted_prices_dict,
            std_dev_dict=std_dev_dict,
            carry_prices_dict=carry_prices_dict,
            rule=rule,
        )
        for rule in list_of_rules
    ]

    ### NOTE: This assumes we are equally weighted across spans
    ### eg all forecast weights the same, equally weighted
    all_forecasts_as_df = pd.concat(all_forecasts_as_list, axis=1)
    average_forecast = all_forecasts_as_df.mean(axis=1)

    ## apply an FDM
    rule_count = len(list_of_rules)
    fdm = get_fdm(rule_count)
    scaled_forecast = average_forecast * fdm
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast


def calculate_forecast_from_function(
    instrument_code: str,
    adjusted_prices_dict: dict,
    std_dev_dict: dict,
    carry_prices_dict: dict,
    rule: dict,
) -> pd.Series:

    rule_copy = copy(rule)
    rule_function = rule_copy.pop("function")
    scalar = rule_copy.pop("scalar")
    rule_args = rule_copy

    forecast_value = rule_function(
        instrument_code=instrument_code,
        adjusted_prices_dict=adjusted_prices_dict,
        std_dev_dict=std_dev_dict,
        carry_prices_dict=carry_prices_dict,
        **rule_args
    )

    return forecast_value * scalar


def calculate_forecast_for_skew(
    adjusted_price: pd.Series,
    instrument_risk: standardDeviation,
    scalar: float,
    horizon: int = 60,
) -> pd.Series:

    current_price = instrument_risk.current_price
    perc_returns = adjusted_price.diff() / current_price.shift(1)
    raw_forecast = -perc_returns.rolling(horizon).skew()
    smoothed_forecast = raw_forecast.ewm(span=int(horizon / 4), min_periods=1).mean()
    scaled_forecast = smoothed_forecast * scalar
    capped_forecast = scaled_forecast.clip(-20, 20)

    return capped_forecast
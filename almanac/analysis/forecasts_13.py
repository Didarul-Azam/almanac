import pandas as pd
import numpy as np
from almanac.utils.standardDeviation import standardDeviation
from almanac.config.fdm_lst import get_fdm
from almanac.utils.utils_13 import get_attenuation 
from almanac.analysis.carry import calculate_smoothed_carry
from almanac.analysis.forecasts import calculate_risk_adjusted_forecast_for_ewmac

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

    smoothed_vol_attenuation = get_attenuation(stdev_ann_perc)
    return scaled_forecast * smoothed_vol_attenuation
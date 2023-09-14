import pandas as pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.config.configs import *


def calculate_position_series_given_fixed_risk(capital: float,
                                               risk_target_tau: float,
                                               current_price: pd.Series,
                                               fx: pd.Series,
                                               multiplier: float,
                                               instrument_risk_ann_perc: float) -> pd.Series:

    #N = (Capital × τ) ÷ (Multiplier × Price × FX × σ %)
    position_in_contracts =  capital * risk_target_tau / (multiplier * current_price * fx * instrument_risk_ann_perc)

    return position_in_contracts

def calculate_position_series_given_variable_risk(
    capital: float,
    risk_target_tau: float,
    fx: pd.Series,
    multiplier: float,
    instrument_risk: standardDeviation,
) -> pd.Series:

    # N = (Capital × τ) ÷ (Multiplier × Price × FX × σ %)
    ## resolves to N = (Capital × τ) ÷ (Multiplier × FX × daily stdev price terms × 16)
    ## for simplicity we use the daily risk in price terms, even if we calculated annualised % returns
    daily_risk_price_terms = instrument_risk.daily_risk_price_terms()

    return (
        capital
        * risk_target_tau
        / (multiplier * fx * daily_risk_price_terms * (BUSINESS_DAYS_IN_YEAR ** 0.5))
    )
    
    
def calculate_position_series_given_variable_risk_for_dict(
    capital: float,
    risk_target_tau: float,
    idm: float,
    weights: dict,
    fx_series_dict: dict,
    multipliers: dict,
    std_dev_dict: dict,
) -> dict:

    position_series_dict = dict(
        [
            (
                instrument_code,
                calculate_position_series_given_variable_risk(
                    capital=capital * idm * weights[instrument_code],
                    risk_target_tau=risk_target_tau,
                    multiplier=multipliers[instrument_code],
                    fx=fx_series_dict[instrument_code],
                    instrument_risk=std_dev_dict[instrument_code],
                ),
            )
            for instrument_code in std_dev_dict.keys()
        ]
    )

    return position_series_dict
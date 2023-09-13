import pandas as pd


def calculate_position_series_given_fixed_risk(capital: float,
                                               risk_target_tau: float,
                                               current_price: pd.Series,
                                               fx: pd.Series,
                                               multiplier: float,
                                               instrument_risk_ann_perc: float) -> pd.Series:

    #N = (Capital × τ) ÷ (Multiplier × Price × FX × σ %)
    position_in_contracts =  capital * risk_target_tau / (multiplier * current_price * fx * instrument_risk_ann_perc)

    return position_in_contracts
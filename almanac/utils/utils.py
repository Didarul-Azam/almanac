from almanac.config.configs import (DEFAULT_DATE_FORMAT, Frequency, NATURAL, YEAR, MONTH, WEEK, BUSINESS_DAYS_IN_YEAR, WEEKS_PER_YEAR, MONTHS_PER_YEAR, SECONDS_PER_YEAR, PERIODS_PER_YEAR
                                    )
from scipy.stats import norm
import pandas as pd
import numpy as np
from enum import Enum


def periods_per_year(at_frequency: Frequency):
    if at_frequency == NATURAL:
        return BUSINESS_DAYS_IN_YEAR
    else:
        return PERIODS_PER_YEAR[at_frequency]


def years_in_data(some_data: pd.Series) -> float:
    datediff = some_data.index[-1] - some_data.index[0]
    seconds_in_data = datediff.total_seconds()
    return seconds_in_data / SECONDS_PER_YEAR


def sum_at_frequency(perc_return: pd.Series,
                     at_frequency: Frequency = NATURAL) -> pd.Series:

    if at_frequency == NATURAL:
        return perc_return

    at_frequency_str_dict = {
        YEAR: "Y",
        WEEK: "7D",
        MONTH: "1M"}
    at_frequency_str = at_frequency_str_dict[at_frequency]

    perc_return_at_freq = perc_return.resample(at_frequency_str).sum()

    return perc_return_at_freq


def ann_mean_given_frequency(perc_return_at_freq: pd.Series,
                             at_frequency: Frequency) -> float:

    mean_at_frequency = perc_return_at_freq.mean()
    periods_per_year_for_frequency = periods_per_year(at_frequency)
    annualised_mean = mean_at_frequency * periods_per_year_for_frequency

    return annualised_mean


def ann_std_given_frequency(perc_return_at_freq: pd.Series,
                            at_frequency: Frequency) -> float:

    std_at_frequency = perc_return_at_freq.std()
    periods_per_year_for_frequency = periods_per_year(at_frequency)
    annualised_std = std_at_frequency * (periods_per_year_for_frequency**.5)

    return annualised_std


def demeaned_remove_zeros(x):
    x[x == 0] = np.nan
    return x - x.mean()


def minimum_capital_for_sub_strategy(
    multiplier: float,
    price: float,
    fx: float,
    instrument_risk_ann_perc: float,
    risk_target: float,
    idm: float,
    weight: float,
    contracts: int = 4,
):
    # (4 × Multiplier i × Price i, t × FX rate i, t × σ % i, t) ÷ (IDM × Weight i × τ)
    return (
        contracts
        * multiplier
        * price
        * fx
        * instrument_risk_ann_perc
        / (risk_target * idm * weight)
    )
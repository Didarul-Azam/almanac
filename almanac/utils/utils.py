from almanac.config.configs import *
from scipy.stats import norm
import pandas as pd
import numpy as np
from enum import Enum
from copy import copy
import datetime


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


def _total_year_frac_from_contract_series(x):
    years = _year_from_contract_series(x)
    month_frac = _month_as_year_frac_from_contract_series(x)

    return years + month_frac


def _year_from_contract_series(x):
    return x.floordiv(10000)


def _month_as_year_frac_from_contract_series(x):
    return _month_from_contract_series(x) / 12.0


def _month_from_contract_series(x):
    return x.mod(10000) / 100.0


def calculate_synthetic_spot_dict(
    adjusted_prices_dict: dict, carry_prices_dict: dict
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    synthetic_spot_dict = dict(
        [
            (
                instrument_code,
                calculate_synthetic_spot(
                    adjusted_prices_dict[instrument_code],
                    carry_price=carry_prices_dict[instrument_code],
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return synthetic_spot_dict


def calculate_synthetic_spot(
    adjusted_price: pd.Series, carry_price: pd.Series
) -> pd.Series:
    from almanac.analysis.carry import calculate_annualised_carry
    ann_carry = calculate_annualised_carry(carry_price)
    diff_index_in_years_as_pd = pd_series_of_diff_index_in_years(ann_carry)

    carry_per_period = diff_index_in_years_as_pd * ann_carry
    cum_carry = carry_per_period.cumsum()
    syn_spot = adjusted_price - cum_carry

    return syn_spot


def pd_series_of_diff_index_in_years(x: pd.Series):
    diff_index_in_years = get_annual_intervals_from_series(x)

    return pd.Series([0] + diff_index_in_years, x.index)


def get_annual_intervals_from_series(x: pd.Series):
    from almanac.config.configs import SECONDS_IN_YEAR
    diff_index = x[1:].index - x[:-1].index
    diff_index_as_list = list(diff_index)
    diff_index_in_seconds = [
        index_item.total_seconds() for index_item in diff_index_as_list
    ]
    diff_index_in_years = [
        index_item_in_seconds / SECONDS_IN_YEAR
        for index_item_in_seconds in diff_index_in_seconds
    ]

    return diff_index_in_years


def unique_years_in_index(index):
    all_years = years_in_index(index)
    unique_years = list(set(all_years))
    unique_years.sort()
    return unique_years


def produce_list_from_x_for_year(x, year, notional_year=NOTIONAL_YEAR):
    list_of_matching_points = index_matches_year(x.index, year)
    matched_x = x[list_of_matching_points]
    matched_x_notional_year = set_year_to_notional_year(
        matched_x, notional_year=notional_year
    )
    return matched_x_notional_year


def set_year_to_notional_year(x, notional_year=NOTIONAL_YEAR):
    y = copy(x)
    new_index = [
        change_index_day_to_notional_year(index_item, notional_year)
        for index_item in list(x.index)
    ]
    y.index = new_index
    return y


def change_index_day_to_notional_year(index_item, notional_year=NOTIONAL_YEAR):
    return datetime.date(notional_year, index_item.month, index_item.day)


def index_matches_year(index, year):

    return [_index_matches_no_leap_days(index_value, year) for index_value in index]


def _index_matches_no_leap_days(index_value, year_to_match):
    if not (index_value.year == year_to_match):
        return False

    if not (index_value.month == 2):
        return True

    if index_value.day == 29:
        return False

    return True


def years_in_index(index):
    index_list = list(index)
    all_years = [item.year for item in index_list]
    return all_years

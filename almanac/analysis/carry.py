import pandas as pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.utils.utils import _total_year_frac_from_contract_series, unique_years_in_index
from almanac.config.configs import *


def calculate_smoothed_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame, span: int
):

    risk_adj_carry = calculate_vol_adjusted_carry(
        stdev_ann_perc=stdev_ann_perc, carry_price=carry_price
    )

    smooth_carry = risk_adj_carry.ewm(span).mean()

    return smooth_carry


def calculate_vol_adjusted_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame
) -> pd.Series:

    ann_carry = calculate_annualised_carry(carry_price)
    ann_price_vol = stdev_ann_perc.annual_risk_price_terms()

    risk_adj_carry = ann_carry.ffill() / ann_price_vol.ffill()

    return risk_adj_carry


def calculate_annualised_carry(
    carry_price: pd.DataFrame,
):

    # will be reversed if price_contract > carry_contract
    raw_carry = carry_price.PRICE - carry_price.CARRY
    contract_diff = _total_year_frac_from_contract_series(
        carry_price.CARRY_CONTRACT
    ) - _total_year_frac_from_contract_series(carry_price.PRICE_CONTRACT)

    ann_carry = raw_carry / contract_diff

    return ann_carry


def calculate_seasonally_adjusted_carry(
    original_raw_carry: pd.Series, rolls_per_year: int
) -> pd.Series:

    average_seasonal = calculate_average_seasonal(original_raw_carry)
    shifted_avg_seasonal = calculate_shifted_avg_seasonal(
        average_seasonal=average_seasonal, rolls_per_year=rolls_per_year
    )

    # STRICTLY SPEAKING THIS IS FORWARD LOOKING...
    average_seasonal_indexed = reindex_seasonal_component_to_index(
        average_seasonal, original_raw_carry.index
    )
    shifted_avg_seasonal_indexed = reindex_seasonal_component_to_index(
        shifted_avg_seasonal, original_raw_carry.index
    )
    net_seasonally_adjusted_carry = original_raw_carry - average_seasonal_indexed
    correctly_seasonally_adjusted_carry = (
        net_seasonally_adjusted_carry + shifted_avg_seasonal_indexed
    )

    return correctly_seasonally_adjusted_carry


def calculate_average_seasonal(original_raw_carry: pd.Series) -> pd.Series:
    original_raw_carry_calendar_days = original_raw_carry.resample("1D").mean()
    original_raw_carry_ffill = original_raw_carry_calendar_days.ffill()
    rolling_average = original_raw_carry_ffill.rolling(365).mean()

    seasonal_component = original_raw_carry_ffill - rolling_average
    seasonal_component_as_matrix = seasonal_matrix(
        seasonal_component, notional_year=NOTIONAL_YEAR
    )
    average_seasonal = seasonal_component_as_matrix.transpose().ewm(
        5).mean().iloc[-1]

    return average_seasonal


def calculate_shifted_avg_seasonal(average_seasonal: pd.Series, rolls_per_year: int):
    shift_days = int(CALENDAR_DAYS_IN_YEAR / rolls_per_year)

    shifted_avg_seasonal = shift_seasonal_series(
        average_seasonal, shift_days=shift_days
    )
    return shifted_avg_seasonal


def seasonal_matrix(x, notional_year=NOTIONAL_YEAR):
    from almanac.utils.utils import produce_list_from_x_for_year
    # given some time series x, gives a data frame where each column is a year
    years_to_use = unique_years_in_index(x.index)
    list_of_slices = [
        produce_list_from_x_for_year(x, year, notional_year=notional_year)
        for year in years_to_use
    ]
    concat_list = pd.concat(list_of_slices, axis=1)
    concat_list.columns = years_to_use

    concat_list = concat_list.sort_index()  # leap years

    return concat_list


def shift_seasonal_series(average_seasonal: pd.Series, shift_days: int):
    # We want to shift forward, because eg
    # quarterly roll, holding MARCH; will measure carry MARCH-JUNE
    # from DEC to MARCH, have MARCH-JUNE carry

    # get two years
    from almanac.utils.utils import set_year_to_notional_year
    next_year = NEXT_NOTIONAL_YEAR
    next_year_seasonal = set_year_to_notional_year(
        average_seasonal, notional_year=next_year
    )
    two_years_worth = pd.concat([average_seasonal, next_year_seasonal], axis=0)
    shifted_two_years_worth = two_years_worth.shift(shift_days)
    shifted_average_seasonal_matrix = seasonal_matrix(shifted_two_years_worth)
    shifted_average_seasonal = (
        shifted_average_seasonal_matrix.transpose(
        ).ffill().iloc[-1].transpose()
    )

    return shifted_average_seasonal


def reindex_seasonal_component_to_index(seasonal_component, index):
    from almanac.utils.utils import unique_years_in_index, set_year_to_notional_year
    all_years = unique_years_in_index(index)
    data_with_years = [
        set_year_to_notional_year(seasonal_component, notional_year)
        for notional_year in all_years
    ]
    sequenced_data = pd.concat(data_with_years, axis=0)
    aligned_seasonal = sequenced_data.reindex(index, method="ffill")

    return aligned_seasonal

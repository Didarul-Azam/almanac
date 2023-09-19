import numpy as np
import pandas as pd
from almanac.utils.standardDeviation import standardDeviation

def quantile_of_points_in_data_series(data_series):
    ## With thanks to https://github.com/PurpleHazeIan for this implementation
    numpy_series = np.array(data_series)
    results = []

    for irow in range(len(data_series)):
        current_value = numpy_series[irow]
        count_less_than = (numpy_series < current_value)[:irow].sum()
        results.append(count_less_than / (irow + 1))

    results_series = pd.Series(results, index=data_series.index)
    return results_series

def calculate_normalised_vol(stdev_ann_perc: standardDeviation) -> pd.Series:
    ten_year_averages = stdev_ann_perc.rolling(2500, min_periods=10).mean()

    return stdev_ann_perc / ten_year_averages

def multiplier_function(vol_quantile):
    if np.isnan(vol_quantile):
        return 1.0

    return 2 - 1.5 * vol_quantile

def get_attenuation(stdev_ann_perc: standardDeviation) -> pd.Series:
    normalised_vol = calculate_normalised_vol(stdev_ann_perc)
    normalised_vol_q = quantile_of_points_in_data_series(normalised_vol)
    vol_attenuation = normalised_vol_q.apply(multiplier_function)

    smoothed_vol_attenuation = vol_attenuation.ewm(span=10).mean()

    return smoothed_vol_attenuation


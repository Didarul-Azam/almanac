import pandas as pd
import numpy as np

class ArgumentError(Exception):
    pass

def calculate_turnover(position):
    number_of_trades = position.diff()
    number_of_trades = number_of_trades.abs()
    daily_trades = number_of_trades.groupby(pd.Grouper(freq='D')).sum()
    daily_mean = position.resample('D').mean()
    rolling_mean_300_days = daily_mean.rolling(window=300, min_periods=1).mean()
    rolling_mean_300_days = rolling_mean_300_days.replace({0: np.nan}).fillna(method='bfill')

    as_proportion_of_average = daily_trades / rolling_mean_300_days.abs().shift(1)
    average_daily = as_proportion_of_average.mean()
    annualised_turnover = average_daily * 256
    

    return annualised_turnover


def turnover(position, weightage_dict=1):
    if isinstance(position,dict):
        turnover_dict = dict(
            [
                (
                    instrument_code,
                    calculate_turnover(
                        position=position[instrument_code],
                        
                    ),
                )
                for instrument_code in position.keys()
            ]
        )    
        weighted_turnover_lst = [
            turnover_dict[asset] * weightage_dict[asset] for asset in turnover_dict.keys()
        ]
        portfolio_turnover = sum(weighted_turnover_lst)
        return portfolio_turnover
    elif isinstance(position, pd.Series):
        annual_turnover =  calculate_turnover(position)
        return annual_turnover
    else:
        # Raise an ArgumentError with a custom error message
        raise ArgumentError("Position must be a Pandas Series or a dictionary")




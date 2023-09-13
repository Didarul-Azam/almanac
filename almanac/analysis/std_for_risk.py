import pandas as pd
from almanac.config.configs import BUSINESS_DAYS_IN_YEAR
from almanac.analysis.calculate_returns import calculate_percentage_returns, calculate_daily_returns

def calculate_standard_deviation_for_risk_targeting(adjusted_price: pd.Series,
                                                    current_price: pd.Series):

    daily_price_changes = adjusted_price.diff()
    percentage_changes = daily_price_changes / current_price.shift(1)

    ## Can do the whole series or recent history
    recent_daily_std = percentage_changes.tail(30).std()

    return recent_daily_std*(BUSINESS_DAYS_IN_YEAR**.5)



def calculate_variable_standard_deviation_for_risk_targeting(
    adjusted_price: pd.Series,
    current_price: pd.Series,
    use_perc_returns: bool = True,
    annualise_stdev: bool = True,
) -> pd.Series:

    if use_perc_returns:
        daily_returns = calculate_percentage_returns(
            adjusted_price=adjusted_price, current_price=current_price
        )
    else:
        daily_returns = calculate_daily_returns(adjusted_price=adjusted_price)

    ## Can do the whole series or recent history
    daily_exp_std_dev = daily_returns.ewm(span=32).std()

    if annualise_stdev:
        annualisation_factor = BUSINESS_DAYS_IN_YEAR ** 0.5
    else:
        ## leave at daily
        annualisation_factor = 1

    annualised_std_dev = daily_exp_std_dev * annualisation_factor

    ## Weight with ten year vol
    ten_year_vol = annualised_std_dev.rolling(
        BUSINESS_DAYS_IN_YEAR * 10, min_periods=1
    ).mean()
    weighted_vol = 0.3 * ten_year_vol + 0.7 * annualised_std_dev

    return weighted_vol
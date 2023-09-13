import pandas as pd
from almanac.config.configs import BUSINESS_DAYS_IN_YEAR


def calculate_standard_deviation_for_risk_targeting(adjusted_price: pd.Series,
                                                    current_price: pd.Series):

    daily_price_changes = adjusted_price.diff()
    percentage_changes = daily_price_changes / current_price.shift(1)

    ## Can do the whole series or recent history
    recent_daily_std = percentage_changes.tail(30).std()

    return recent_daily_std*(BUSINESS_DAYS_IN_YEAR**.5)

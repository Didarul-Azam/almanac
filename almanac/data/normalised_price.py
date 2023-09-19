import pandas as pd
from almanac.utils.standardDeviation import standardDeviation

def calculate_normalised_price_dict(
    adjusted_prices_dict: dict, std_dev_dict: dict
) -> dict:

    list_of_instruments = list(adjusted_prices_dict.keys())
    normalised_price_dict = dict(
        [
            (
                instrument_code,
                calculate_normalised_price(
                    adjusted_prices_dict[instrument_code],
                    instrument_risk=std_dev_dict[instrument_code],
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return normalised_price_dict


def calculate_normalised_price(
    adjusted_price: pd.Series,
    instrument_risk: standardDeviation,
) -> pd.Series:

    daily_price_instrument_risk = instrument_risk.daily_risk_price_terms()
    normalised_returns = 100 * (adjusted_price.diff() / daily_price_instrument_risk)
    normalised_returns[normalised_returns.isna()] = 0
    normalised_price = normalised_returns.cumsum()

    return normalised_price
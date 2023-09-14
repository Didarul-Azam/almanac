import pandas as pd
import numpy as np
from almanac.data.data import pd_readcsv
from almanac.config.instruments import cost_per_contract_dict, multipliers, instrument_weights
from almanac.config.fx_dict import fx_dict


def create_fx_series_given_adjusted_prices_dict(fx_path, adjusted_prices_dict: dict) -> dict:
    fx_series_dict = dict([(instrument_code,
                            create_fx_series_given_adjusted_prices(fx_path, instrument_code, adjusted_prices),)
                           for instrument_code, adjusted_prices in adjusted_prices_dict.items()])
    return fx_series_dict


def create_fx_series_given_adjusted_prices(fx_path, instrument_code: str, adjusted_prices: pd.Series) -> pd.Series:

    currency_for_instrument = fx_dict.get(instrument_code, "usd")
    if currency_for_instrument == "usd":
        return pd.Series(1, index=adjusted_prices.index)

    fx_prices = get_fx_prices(fx_path, currency_for_instrument)
    fx_prices_aligned = fx_prices.reindex(adjusted_prices.index).ffill()

    return fx_prices_aligned


def get_fx_prices(fx_path, currency: str) -> pd.Series:
    prices_as_df = pd_readcsv(f"{fx_path}{currency}_fx.csv")
    return prices_as_df.squeeze()

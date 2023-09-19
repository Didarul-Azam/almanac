import pandas as pd
import numpy as np
from almanac.data.normalised_price import calculate_normalised_price_dict
from almanac.analysis.asset_class import calculate_asset_class_price_dict


def calculate_relative_price_dict(
    adjusted_prices_dict: dict, std_dev_dict: dict, asset_class_groupings: dict
) -> dict:

    normalised_price_dict = calculate_normalised_price_dict(
        adjusted_prices_dict=adjusted_prices_dict, std_dev_dict=std_dev_dict
    )

    asset_class_price_dict = calculate_asset_class_price_dict(
        normalised_price_dict=normalised_price_dict,
        asset_class_groupings=asset_class_groupings,
    )

    list_of_instruments = list(normalised_price_dict.keys())
    relative_price_dict = dict(
        [
            (
                instrument_code,
                relative_price_for_instrument(
                    instrument_code,
                    normalised_price_dict=normalised_price_dict,
                    asset_class_price_dict=asset_class_price_dict,
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return relative_price_dict


def relative_price_for_instrument(
    instrument_code: str, normalised_price_dict: dict, asset_class_price_dict: dict
) -> pd.Series:

    normalised_price = normalised_price_dict[instrument_code]
    asset_class_price = asset_class_price_dict[instrument_code]
    asset_class_price_matched = asset_class_price.reindex(
        normalised_price.index
    ).ffill()
    relative_price = normalised_price - asset_class_price_matched
    relative_price[relative_price == 0] = np.nan

    return relative_price

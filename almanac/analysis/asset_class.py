import pandas as pd

asset_class_groupings = {
    "bond_assets": [
        "US2",
        "US3",
        "US5",
        "US10",
        "US30",
        "US20",
        "US10U",
        "OAT",
        "SHATZ",
        "BOBL",
        "BUND",
        "BUXL",
        "BTP",
        "BTP3",
        "JGB",
        "BONO",
    ],
    "equity_us_assets": ["DOW", "NASDAQ_micro", "R1000", "SP400", "SP500_micro"],
    "equity_eu_assets": [
        "AEX",
        "DAX",
        "SMI",
        "DJSTX-SMALL",
        "EU-DIV30",
        "EURO600",
        "EUROSTX",
        "EU-AUTO",
        "EU-BASIC",
        "EU-HEALTH",
        "EU-INSURE",
        "EU-OIL",
        "EU-TECH",
        "EU-UTILS",
    ],
    "equity_asia_assets": [
        "MSCIASIA",
        "FTSECHINAA",
        "FTSECHINAH",
        "NIFTY",
        "NIKKEI",
        "NIKKEI400",
        "MUMMY",
        "TOPIX",
        "MSCISING",
    ],
    "volatility_assets": ["VIX", "V2X"],
    "fx_major_assets": [
        "AUD",
        "CAD",
        "CHF",
        "EUR",
        "GBP",
        "JPY",
        "NOK",
        "NZD",
        "SEK",
        "GBPJPY",
        "BRE",
    ],
    "fx_cross_assets": ["INR", "MXP", "RUR", "SGD"],
    "metal_crypto_assets": [
        "ALUMINIUM",
        "COPPER",
        "GOLD_micro",
        "IRON",
        "PALLAD",
        "PLAT",
        "SILVER",
        "BITCOIN",
        "ETHEREUM",
    ],
    "energy_assets": [
        "BRENT-LAST",
        "CRUDE_W_mini",
        "GASOILINE",
        "GAS_US_mini",
        "HEATOIL",
    ],
    "agricultural_assets": [
        "BBCOMM",
        "CHEESE",
        "CORN",
        "FEEDCOW",
        "LEANHOG",
        "LIVECOW",
        "REDWHEAT",
        "RICE",
        "SOYBEAN",
        "SOYMEAL",
        "SOYOIL",
        "WHEAT",
    ],
}

def calculate_asset_class_price_dict(
    normalised_price_dict: dict, asset_class_groupings: dict
):

    list_of_instruments = list(normalised_price_dict.keys())
    asset_class_price_dict = dict(
        [
            (
                instrument_code,
                calculate_asset_prices_for_instrument(
                    instrument_code,
                    normalised_price_dict=normalised_price_dict,
                    asset_class_groupings=asset_class_groupings,
                ),
            )
            for instrument_code in list_of_instruments
        ]
    )

    return asset_class_price_dict

def calculate_asset_prices_for_instrument(
    instrument_code: str, normalised_price_dict: dict, asset_class_groupings: dict
) -> pd.Series:

    asset_class = get_asset_class_for_instrument(
        instrument_code, asset_class_groupings=asset_class_groupings
    )

    return get_normalised_price_for_asset_class(
        asset_class=asset_class,
        asset_class_groupings=asset_class_groupings,
        normalised_price_dict=normalised_price_dict,
    )
def get_asset_class_for_instrument(
    instrument_code: str, asset_class_groupings: dict
) -> str:

    possible_asset_classes = list(asset_class_groupings.keys())
    asset_class = [
        asset
        for asset in possible_asset_classes
        if instrument_code in asset_class_groupings[asset]
    ][0]

    return asset_class

def get_normalised_price_for_asset_class(
    asset_class: str, normalised_price_dict: dict, asset_class_groupings: dict
) -> pd.Series:

    # Wasteful rerunning this for each instrument but makes code simpler
    instruments_in_asset_class = asset_class_groupings[asset_class]
    list_of_normalised_prices_over_asset_class = [
        normalised_price_dict[instrument_code]
        for instrument_code in instruments_in_asset_class
    ]
    normalised_prices_over_asset_class = pd.concat(
        list_of_normalised_prices_over_asset_class, axis=1
    ).ffill()
    normalised_returns_over_asset_class = normalised_prices_over_asset_class.diff()
    average_normalised_return_over_asset_class = (
        normalised_returns_over_asset_class.mean(axis=1)
    )

    asset_class_price = average_normalised_return_over_asset_class.cumsum()

    return asset_class_price
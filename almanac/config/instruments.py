cost_per_contract_dict = {'US2': 6.1, "US3": 8.26, 'US5': 5.306, 'US10': 8.8, 'US30': 15.58, 'US20': 17.04, 'US10U': 9.15, 'OAT': 8.81, 'SHATZ': 4.21, 'BOBL': 7.01, 'BUND': 6.55, 'BUXL': 15.56, 'BTP': 7.96, 'BTP3': 7.98, 'JGB': 5837, 'BONO': 59, 'DOW': 0.52, 'NASDAQ_micro': 1.22, 'R1000': 22, 'SP400': 26.57, 'SP500_micro': 1.5, 'AEX': 16.39, 'DAX': 1.98, 'SMI': 12.1, 'DJSTX-SMALL': 2, 'EU-DIV30': 1.97, 'EURO600': 2.07, 'EUROSTX': 7.3, 'EU-AUTO': 13.8, 'EU-BASIC': 25.5, 'EU-HEALTH': 18.70, 'EU-INSURE': 8.23, 'EU-OIL': 9.35, 'EU-TECH': 16.63, 'EU-UTILS': 9.98, 'MSCIASIA': 18.3, 'FTSECHINAA': .5, 'FTSECHINAH': 9.1, 'NIFTY': 0.11, 'NIKKEI': 328, 'NIKKEI400': 432, 'MUMMY': 568, 'TOPIX': 261,
                          'MSCISING': 7.3, 'VIX': 15.73, 'V2X': 1.36, 'AUD': 2.56, 'CAD': 5.12, 'CHF': 8.4, 'EUR': 6.7, 'GBP': 23.43, 'JPY': 254, 'NOK': 71, 'NZD': 6.47, 'SEK': 57.6, 'GBPJPY': 3456, 'BRE': 0.0022, 'INR': 240, 'MXP': 5.65, 'RUR': 300, 'SGD': 17.68, 'ALUMINIUM': 42.5, 'COPPER': 13.23, 'GOLD_micro': 1.75, 'IRON': 11.63, 'PALLAD': 176.5, 'PLAT': 12.74, 'SILVER': 5.38, 'BITCOIN': 5.15, 'ETHEREUM': 61.94, 'BRENT-LAST': 23.25, 'CRUDE_W_mini': 19.14, 'GASOILINE': 42.75, 'GAS_US_mini': 7.21, 'HEATOIL': 38.61, 'BBCOMM': 11.13, 'CHEESE': 106.68, 'CORN': 896, 'FEEDCOW': 2688, 'LEANHOG': 1377, 'LIVECOW': 1092, 'OAT': 174.3, 'REDWHEAT': 1560, 'RICE': 47.51, 'SOYBEAN': 1639, 'SOYMEAL': 10.7, 'SOYOIL': 1260, 'WHEAT': 1697}

multipliers = {
    "US2": 2000,
    "US3": 2000,
    "US5": 1000,
    "US10": 1000,
    "USIRS10": 1000,
    "US20": 1000,
    "US30": 1000,
    "USIRS5ERIS": 1000,
    "US10U": 1000,
    "EDOLLAR": 2500,
    "OAT": 1000,
    "SHATZ": 1000,
    "BOBL": 1000,
    "BUND": 1000,
    "BUXL": 1000,
    "BTP": 1000,
    "BTP3": 1000,
    "JGB": 1000000,
    "KR10": 1000000,
    "BONO": 1000,
    "DOW": 0.5,
    "NASDAQ_micro": 2,
    "R1000": 50,
    "RUSSELL": 5,
    "SP400": 100,
    "SP500_micro": 5,
    "DAX": 1,
    "AEX": 200,
    "CAC": 10,
    "SMI": 10,
    "DJSTX-SMALL": 50,
    "EU-DIV30": 10,
    "EURO600": 50,
    "EUROSTX": 10,
    "EU-AUTO": 50,
    "EU-BASIC": 50,
    "EU-HEALTH": 50,
    "EU-INSURE": 50,
    "EU-OIL": 50,
    "EU-TECH": 50,
    "EU-UTILS": 50,
    "MSCIASIA": 100,
    "FTSECHINAA": 1,
    "FTSECHINAH": 2,
    "NIFTY": 2,
    "NIKKEI": 100,
    "NIKKEI400": 100,
    "MUMMY": 1000,
    "TOPIX": 1000,
    "KOSDAQ": 1000,
    "KOSPI": 250000,
    "MSCISING": 100,
    "FTSETAIWAN": 40,
    "VIX": 1000,
    "V2X": 100,
    "AUD": 100000,
    "CAD": 100000,
    "CHF": 125000,
    "EUR": 125000,
    "GBP": 625000,
    "JPY": 12500000,
    "NOK": 2000000,
    "NZD": 100000,
    "SEK": 2000000,
    "GBPJPY": 125000,
    "BRE": 100000,
    "CNH": 100000,
    "INR": 5000000,
    "MXP": 500000,
    "RUR": 2500000,
    "SGD": 100000,
    "ALUMINIUM": 25,
    "COPPER": 25000,
    "GOLD_micro": 10,
    "IRON": 100,
    "PALLAD": 100,
    "PLAT": 50,
    "SILVER": 1000,
    "BITCOIN": 0.1,
    "ETHEREUM": 50,
    "BRENT-LAST": 1000,
    "CRUDE_W_mini": 500,
    "GAS-LAST": 10000,
    "GASOILINE": 42000,
    "GAS_US_mini": 2500,
    "HEATOIL": 42000,
    "BBCOMM": 100,
    "CHEESE": 20000,
    "CORN": 5000,
    "FEEDCOW": 50000,
    "LEANHOG": 40000,
    "LIVECOW": 40000,
    "OAT": 5000,
    "REDWHEAT": 5000,
    "RICE": 2000,
    "SOYBEAN": 5000,
    "SOYMEAL": 100,
    "SOYOIL": 60000,
    "WHEAT": 5000,
}
instrument_weights = {'FEEDCOW': 0.015625, 'SHATZ': 0.03125, 'AUD': 0.0009765625, 'BONO': 0.015625, 'SP400': 0.0078125, 'NZD': 0.00390625, 'IRON': 0.0009765625, 'CRUDE_W_mini': 0.00390625, 'EURO600': 0.001953125, 'MXP': 0.00390625, 'GBPJPY': 0.0078125, 'BTP': 0.001953125, 'V2X': 0.03125, 'EU-AUTO': 0.001953125, 'ETHEREUM': 0.03125, 'US2': 0.015625, 'TOPIX': 0.03125, 'NASDAQ_micro': 0.015625, 'SMI': 0.015625, 'BRENT-LAST': 0.015625, 'CHEESE': 0.00390625, 'PALLAD': 0.015625, 'NIKKEI': 0.03125, 'SOYMEAL': 0.001953125, 'DJSTX-SMALL': 0.001953125, 'R1000': 0.015625, 'RUR': 0.015625, 'GBP': 0.0009765625, 'EUR': 0.00390625, 'GASOILINE': 0.03125, 'EU-BASIC': 0.00390625, 'EU-INSURE': 0.015625, 'US5': 0.015625, 'US30': 0.015625, 'REDWHEAT': 0.015625, 'BRE': 0.0009765625, 'US20': 0.0078125, 'US10U': 0.015625, 'DAX': 0.001953125, 'SOYOIL': 0.0078125, 'US3': 0.0078125, 'COPPER': 0.0009765625, 'MSCISING': 0.0078125,
                      'RICE': 0.00390625, 'EU-DIV30': 0.0078125, 'CAD': 0.0078125, 'VIX': 0.0625, 'NIKKEI400': 0.03125, 'DOW': 0.0078125, 'BUND': 0.015625, 'GOLD_micro': 0.00390625, 'MSCIASIA': 0.0078125, 'SEK': 0.001953125, 'SGD': 0.0625, 'BUXL': 0.015625, 'BOBL': 0.015625, 'CORN': 0.0078125, 'EU-OIL': 0.0078125, 'WHEAT': 0.001953125, 'MUMMY': 0.015625, 'HEATOIL': 0.015625, 'EU-UTILS': 0.0078125, 'INR': 0.0078125, 'LIVECOW': 0.015625, 'EU-TECH': 0.001953125, 'BBCOMM': 0.015625, 'AEX': 0.001953125, 'OAT': 0.015625, 'NIFTY': 0.0009765625, 'EUROSTX': 0.0078125, 'FTSECHINAA': 0.0009765625, 'SILVER': 0.0078125, 'BITCOIN': 0.001953125, 'JPY': 0.015625, 'GAS_US_mini': 0.0078125, 'FTSECHINAH': 0.015625, 'SOYBEAN': 0.0078125, 'PLAT': 0.0009765625, 'SP500_micro': 0.0078125, 'NOK': 0.0009765625, 'ALUMINIUM': 0.015625, 'BTP3': 0.0078125, 'CHF': 0.0009765625, 'US10': 0.015625, 'JGB': 0.015625, 'EU-HEALTH': 0.0078125, 'LEANHOG': 0.0078125}

INSTRUMENT_LIST = list(cost_per_contract_dict.keys())

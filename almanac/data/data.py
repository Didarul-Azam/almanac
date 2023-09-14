import pandas as pd
from almanac.config.configs import DEFAULT_DATE_FORMAT

# class Read_csv:

#     def __init__(self, date_format="%Y-%m-%d", date_index_name="index"):
#         self.date_format = date_format
#         self.date_index_name = date_index_name
#         self.all_data = {}

#     def pd_readcsv(self, filename) -> pd.DataFrame:
#         ans = pd.read_csv(filename)
#         ans[self.date_index_name] = pd.to_datetime(
#             ans[self.date_index_name], format=self.date_format)
#         ans.set_index(self.date_index_name, inplace=True)
#         return ans

#     def get_data_dict(self, data_path, INSTRUMENT_LIST):
#         all_data = {instrument_code: self.pd_readcsv(
#             f"{data_path}{instrument_code}.csv") for instrument_code in INSTRUMENT_LIST}

#         adjusted_prices = {instrument_code: data_for_instrument["adjusted"]
#                            for instrument_code, data_for_instrument in all_data.items()}
#         current_prices = {instrument_code: data_for_instrument["underlying"]
#                           for instrument_code, data_for_instrument in all_data.items()}

#         return adjusted_prices, current_prices


def pd_readcsv(filename: str, date_format=DEFAULT_DATE_FORMAT, date_index_name: str = "index") -> pd.DataFrame:

    ans = pd.read_csv(filename)
    ans.index = pd.to_datetime(ans[date_index_name], format=date_format).values

    del ans[date_index_name]

    ans.index.name = None

    return ans


def get_data_dict(data_path, INSTRUMENT_LIST):

    all_data = dict(
        [
            (instrument_code, pd_readcsv(f"{data_path}{instrument_code}.csv"))
            for instrument_code in INSTRUMENT_LIST
        ]
    )

    adjusted_prices = dict(
        [
            (instrument_code, data_for_instrument.adjusted)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    current_prices = dict(
        [
            (instrument_code, data_for_instrument.underlying)
            for instrument_code, data_for_instrument in all_data.items()
        ]
    )

    return adjusted_prices, current_prices

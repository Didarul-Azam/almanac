import pandas as pd

class Read_csv:
  
    def __init__(self, date_format="%Y-%m-%d", date_index_name="index"):
        self.date_format = date_format
        self.date_index_name = date_index_name
        self.all_data = {}

    def pd_readcsv(self, filename) -> pd.DataFrame:
        ans = pd.read_csv(filename)
        ans.index = pd.to_datetime(ans[self.date_index_name], format=self.date_format).values

        del ans[self.date_index_name]

        ans.index.name = None

        return ans

    def get_data_dict(self, instrument_list):
        for instrument_code in instrument_list:
            data_for_instrument = self.pd_readcsv("%s.csv" % instrument_code)
            self.all_data[instrument_code] = data_for_instrument

        adjusted_prices = {instrument_code: data_for_instrument['adjusted'] for instrument_code, data_for_instrument in self.all_data.items()}
        current_prices = {instrument_code: data_for_instrument['underlying'] for instrument_code, data_for_instrument in self.all_data.items()}

        return adjusted_prices, current_prices



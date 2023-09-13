from almanac.data.data import Read_csv
from almanac.analysis.position_sereies_fixed_risk import calculate_position_series_given_fixed_risk
from almanac.analysis.std_for_risk import calculate_standard_deviation_for_risk_targeting
from almanac.analysis.calculate_stats import Stats
from almanac.analysis.calculate_returns import calculate_perc_returns

from typing import Union
import pandas as pd
import numpy as np


class Strategy2:
    def __init__(self, data_path: str, multiplier: int, risk_target: Union[int, float], capital: int):
        self.data_path = data_path
        self.multiplier = multiplier
        self.risk_target = risk_target
        self.capital = capital
        self.data = self.get_data()
        self.adjusted_price = self.data.adjusted
        self.current_price = self.data.underlying
        self.fx_series = pd.Series(1, index=self.data.index)
        self.instrument_risk = calculate_standard_deviation_for_risk_targeting(adjusted_price=self.adjusted_price,
                                                                               current_price=self.adjusted_price)
        self.position_contracts_held = calculate_position_series_given_fixed_risk(capital=self.capital,
                                                                                  risk_target_tau=self.risk_target,
                                                                                  current_price=self.current_price,
                                                                                  fx=self.fx_series,
                                                                                  multiplier=self.multiplier,
                                                                                  instrument_risk_ann_perc=self.instrument_risk)
        self.perc_return = self.get_return()

    def get_data(self):
        reader = Read_csv(self.data_path)
        data = reader.pd_readcsv()
        return data

    def get_return(self):
        return calculate_perc_returns(position_contracts_held=self.position_contracts_held,
                                      adjusted_price=self.adjusted_price,
                                      fx_series=self.fx_series,
                                      multiplier=self.multiplier,
                                      capital_required=self.capital)

    def show_stats(self):
        statistics = Stats(self.perc_return)
        print(statistics.stats(show=True))

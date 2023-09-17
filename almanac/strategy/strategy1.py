from almanac.data.data import pd_readcsv
from almanac.analysis.calculate_returns import calculate_perc_returns
from almanac.analysis.calculate_stats import Stats
import quantstats as qs
from typing import Union
import pandas as pd
import numpy as np


class Strategy1:
    def __init__(self, data_path: str, multiplier: int, risk_target: Union[int, float], capital: int):
        self.data_path = data_path
        self.multiplier = multiplier
        self.risk_target = risk_target
        self.capital = capital
        self.data = self.get_data()
        self.adjusted_price = self.data.adjusted
        self.current_price = self.data.underlying
        self.fx_series = pd.Series(1, index=self.data.index)
        self.position_contracts_held = pd.Series(1, index=self.data.index)
        self.capital_required = self.multiplier * self.current_price
        self.perc_return = self.get_return()

    def get_data(self):
        data = pd_readcsv(self.data_path)
        return data

    def get_return(self):
        return calculate_perc_returns(
            position_contracts_held=self.position_contracts_held,
            adjusted_price=self.adjusted_price,
            fx_series=self.fx_series,
            capital_required=self.capital_required,
            multiplier=self.multiplier
        )

    def show_stats(self):
        statistics = Stats(self.perc_return)
        print(statistics.stats(show=True))

    def run_strategy(self):
        qs.reports.full(self.perc_return, benchmark='^GSPC')

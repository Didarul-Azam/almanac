from almanac.data.data import pd_readcsv
from almanac.analysis.calculate_stats import Stats
from almanac.analysis.calculate_returns import calculate_perc_returns
from almanac.analysis.positions import calculate_position_series_given_variable_risk
from almanac.utils.standardDeviation import standardDeviation
from almanac.strategy.baseStrategy import StrategyBase

from typing import Union
import pandas as pd
import numpy as np
import quantstats as qs


class Strategy3(StrategyBase):
    def __init__(self, data_path: str, multiplier: int, risk_target: Union[int, float], capital: int):
        self.data_path = data_path
        self.multiplier = multiplier
        self.risk_target = risk_target
        self.capital = capital
        self.data = self.get_data()
        self.adjusted_price = self.data.adjusted
        self.current_price = self.data.underlying
        self.fx_series = pd.Series(1, index=self.data.index)
        self.instrument_risk = standardDeviation(adjusted_price=self.adjusted_price,
                                                 current_price=self.current_price,
                                                 use_perc_returns=True,
                                                 annualise_stdev=True)
        self.position_contracts_held = calculate_position_series_given_variable_risk(capital=capital,
                                                                                     fx=self.fx_series,
                                                                                     instrument_risk=self.instrument_risk,
                                                                                     risk_target_tau=self.risk_target,
                                                                                     multiplier=self.multiplier,)
        self.perc_return = self.get_return()

    def get_data(self):
        data = pd_readcsv(self.data_path)
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

    def run_strategy(self):
        qs.reports.full(self.perc_return, benchmark='^GSPC')

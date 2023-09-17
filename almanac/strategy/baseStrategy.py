from almanac.config.instruments import INSTRUMENT_LIST, instrument_weights, multipliers, cost_per_contract_dict
from almanac.data.data import get_data_dict
from almanac.utils.fx_series import create_fx_series_given_adjusted_prices_dict
from almanac.analysis.std_for_risk import calculate_variable_standard_deviation_for_risk_targeting_from_dict
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_trend_filter_applied
from almanac.analysis.calculate_returns import calculate_returns, calculate_perc_returns_for_dict_with_costs, aggregate_returns
from typing import Union
import pandas as pd
import numpy as np
import quantstats as qs


class StrategyBase:
    def __init__(self, data_path: str, fx_path: str, instrument_list: list,
                 instrument_weights: dict, multipliers: dict, idm: Union[int, float],
                 risk_target: Union[int, float], capital: int, cost_per_contract_dict: dict):
        self.data_path = data_path
        self.fx_path = fx_path
        self.instrument_list = instrument_list
        self.instrument_weights = instrument_weights
        self.multipliers = multipliers
        self.idm = idm
        self.risk_target = risk_target
        self.cost_per_contract_dict = cost_per_contract_dict
        self.capital = capital

    def create_fx_series(self, adjusted_prices):
        fx_series_dict = create_fx_series_given_adjusted_prices_dict(
            self.fx_path, adjusted_prices
        )
        return fx_series_dict

    def calculate_std_dev(self, adjusted_prices, current_prices):
        std_dev_dict = calculate_variable_standard_deviation_for_risk_targeting_from_dict(
            adjusted_prices=adjusted_prices,
            current_prices=current_prices,
            annualise_stdev=True,
            use_perc_returns=True,
        )
        return std_dev_dict

    def cost_calculations(self):
        self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns = calculate_returns(position_contracts=self.position_contracts_dict,
                                                                                               adjusted_prices=self.adjusted_prices,
                                                                                               multipliers=self.multipliers,
                                                                                               fx_series=self.fx_series_dict,
                                                                                               capital=self.capital,
                                                                                               cost_per_contract=self.cost_per_contract_dict,
                                                                                               std_dev=self.std_dev_dict,
                                                                                               aggregate=True)
        return self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns

    def calculate_quantstats(self):
        self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns = self.cost_calculations()
        qs.reports.full(precost_returns=self.pre_cost_portfolio_returns,
                        postcost_returns=self.post_cost_portfoilio_returns, benchmark='^GSPC')
from almanac.config.instruments import INSTRUMENT_LIST, instrument_weights, multipliers, cost_per_contract_dict
from almanac.data.data import get_data_dict
from almanac.utils.fx_series import create_fx_series_given_adjusted_prices_dict
from almanac.analysis.std_for_risk import calculate_variable_standard_deviation_for_risk_targeting_from_dict
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_trend_filter_applied
from almanac.analysis.calculate_returns import calculate_returns, calculate_perc_returns_for_dict_with_costs, aggregate_returns
from almanac.analysis.buffering import apply_buffering_to_position_dict
from almanac.analysis.turnover import turnover
from typing import Union
import pandas as pd
import numpy as np
import quantstats as qs


class StrategyBase:
    def __init__(self, data_path: str, fx_path: str, instrument_list: list,
                 instrument_weights: dict, multipliers: dict, idm: Union[int, float],
                 risk_target: Union[int, float], capital: int, cost_per_contract_dict: dict,
                 use_buffer=False):
        self.data_path = data_path
        self.fx_path = fx_path
        self.instrument_list = instrument_list
        self.instrument_weights = instrument_weights
        self.multipliers = multipliers
        self.idm = idm
        self.risk_target = risk_target
        self.cost_per_contract_dict = cost_per_contract_dict
        self.capital = capital
        self.use_buffer = use_buffer

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

    def buffered_position(self):
        self.buffered_position_dict = apply_buffering_to_position_dict(position_contracts_dict=self.position_contracts_dict,
                                                                       average_position_contracts_dict=self.average_position_contracts_dict,)

        return self.buffered_position_dict

    def cost_calculations(self):
        if self.use_buffer:
            self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns = calculate_returns(position_contracts=self.buffered_position(),
                                                                                                   adjusted_prices=self.adjusted_prices,
                                                                                                   multipliers=self.multipliers,
                                                                                                   fx_series=self.fx_series_dict,
                                                                                                   capital=self.capital,
                                                                                                   cost_per_contract=self.cost_per_contract_dict,
                                                                                                   std_dev=self.std_dev_dict,
                                                                                                   aggregate=True)
            return self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns
        else:
            self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns = calculate_returns(position_contracts=self.position_contracts_dict,
                                                                                                   adjusted_prices=self.adjusted_prices,
                                                                                                   multipliers=self.multipliers,
                                                                                                   fx_series=self.fx_series_dict,
                                                                                                   capital=self.capital,
                                                                                                   cost_per_contract=self.cost_per_contract_dict,
                                                                                                   std_dev=self.std_dev_dict,
                                                                                                   aggregate=True)
            return self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns

    def calculate_turnover(self):
        if not self.instrument_weights:
            self.instrument_weights = 1
        return turnover(position=self.position_contracts_dict,
                        weightage_dict=self.instrument_weights)

    def calculate_quantstats(self):
        portfolio_turnover = self.calculate_turnover()
        print(f"Portfolio Turnover: {portfolio_turnover}")
        self.pre_cost_portfolio_returns, self.post_cost_portfoilio_returns = self.cost_calculations()
        qs.reports.full(precost_returns=self.pre_cost_portfolio_returns,
                        postcost_returns=self.post_cost_portfoilio_returns, benchmark='^GSPC')

    def run_strategy(self):
        if self.use_buffer:
            self.adjusted_prices, self.current_prices, self.carry_prices = self.get_data()
        else:
            self.adjusted_prices, self.current_prices = self.get_data()
        self.fx_series_dict = self.create_fx_series(self.adjusted_prices)
        self.std_dev_dict = self.calculate_std_dev(
            self.adjusted_prices, self.current_prices)
        self.position_contracts_dict = self.calculate_positions()
        self.calculate_quantstats()

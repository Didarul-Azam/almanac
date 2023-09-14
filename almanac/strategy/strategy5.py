from almanac.config.instruments import INSTRUMENT_LIST, instrument_weights, multipliers, cost_per_contract_dict
from almanac.data.data import get_data_dict
from almanac.utils.fx_series import create_fx_series_given_adjusted_prices_dict
from almanac.analysis.std_for_risk import calculate_variable_standard_deviation_for_risk_targeting_from_dict
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_trend_filter_applied
from almanac.analysis.calculate_returns import calculate_perc_returns_for_dict_with_costs, aggregate_returns
from typing import Union
import pandas as pd
import numpy as np
import quantstats as qs


class Strategy5:
    def __init__(self, data_path: str,
                 fx_path: str,
                 instrument_list: list,
                 instrument_weights: dict,
                 multipliers: dict,
                 idm: Union[int, float],
                 risk_target: Union[int, float],
                 cost_per_contract_dict: dict,
                 capital: int,):
        self.data_path = data_path
        self.multipliers = multipliers
        self.risk_target = risk_target
        self.capital = capital
        self.instrument_list = instrument_list
        self.fx_path = fx_path
        self.idm = idm
        self.instrument_weights = instrument_weights
        self.cost_per_contract_dict = cost_per_contract_dict

        self.adjusted_prices, self.current_prices = self.get_data()
        self.fx_series_dict = create_fx_series_given_adjusted_prices_dict(
            self.fx_path, self.adjusted_prices
        )

        self.std_dev_dict = self.get_std()
        self.position_contracts_dict = self.get_positions()
        self.perc_return_dict = self.get_return()
        self.perc_return_agg = aggregate_returns(self.perc_return_dict)

    def get_data(self):
        adjusted_prices, current_prices = get_data_dict(
            self.data_path, self.instrument_list
        )
        return adjusted_prices, current_prices

    def get_std(self):
        std_dev_dict = calculate_variable_standard_deviation_for_risk_targeting_from_dict(
            adjusted_prices=self.adjusted_prices,
            current_prices=self.current_prices,
            annualise_stdev=True,
            use_perc_returns=True,
        )
        return std_dev_dict

    def get_positions(self):
        average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=self.std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers, )

        position_contracts_dict = calculate_position_dict_with_trend_filter_applied(
            adjusted_prices_dict=self.adjusted_prices,
            average_position_contracts_dict=average_position_contracts_dict,)
        return position_contracts_dict

    def get_return(self):
        return calculate_perc_returns_for_dict_with_costs(
            position_contracts_dict=self.position_contracts_dict,
            fx_series=self.fx_series_dict,
            multipliers=self.multipliers,
            capital=self.capital,
            adjusted_prices=self.adjusted_prices,
            cost_per_contract_dict=self.cost_per_contract_dict,
            std_dev_dict=self.std_dev_dict
        )

    def get_quantstats(self):
        qs.reports.full(self.perc_return_agg, benchmark='^GSPC')

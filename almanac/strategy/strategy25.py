from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_forecast_applied
from almanac.data.normalised_price import calculate_normalised_price_dict
from almanac.strategy.baseStrategy import StrategyBase
from almanac.analysis.asset_class import calculate_asset_class_price_dict
from almanac.data.data import get_data_dict_with_carry
from almanac.data.relative_price import calculate_relative_price_dict
from almanac.analysis.positions import calculate_position_dict_with_forecast_from_function_applied, calculate_position_dict_with_forecast_from_function_applied
from almanac.dynamic_optimization.dyn_opt import dynamically_optimise_positions
from typing import Union


class Strategy25(StrategyBase):
    def __init__(
        self,
        data_path: str,
        carry_path: str,
        fx_path: str,
        instrument_list: list,
        instrument_weights: dict,
        multipliers: dict,
        idm: Union[int, float],
        risk_target: Union[int, float],
        capital: int,
        cost_per_contract_dict: dict,
        algo_to_use,
        unrounded_position_contracts_dict,
        use_buffer=False,
        get_carry=True

    ):
        super().__init__(
            data_path=data_path,
            fx_path=fx_path,
            instrument_list=instrument_list,
            instrument_weights=instrument_weights,
            multipliers=multipliers,
            idm=idm,
            risk_target=risk_target,
            capital=capital,
            cost_per_contract_dict=cost_per_contract_dict,
            use_buffer=use_buffer,
            get_carry=get_carry
        )
        self.carry_path = carry_path
        self.algo_to_use = algo_to_use
        self.unrounded_position_contracts_dict = unrounded_position_contracts_dict

    def get_data(self):
        self.adjusted_prices, self.current_prices, self.carry_prices = get_data_dict_with_carry(
            self.data_path, self.carry_path, self.instrument_list
        )
        return self.adjusted_prices, self.current_prices, self.carry_prices

    def calculate_positions(self):
        self.position_contracts_dict = dynamically_optimise_positions(
            capital=self.capital,
            current_prices_dict=self.current_prices,
            cost_per_contract_dict=self.cost_per_contract_dict,
            adjusted_prices_dict=self.adjusted_prices,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,
            unrounded_position_contracts_dict=self.unrounded_position_contracts_dict,
            std_dev_dict=self.std_dev_dict,
            algo_to_use=self.algo_to_use,
        )
        return self.position_contracts_dict

    def run_strategy(self):
        if self.get_carry:
            self.adjusted_prices, self.current_prices, self.carry_prices = self.get_data()
        else:
            self.adjusted_prices, self.current_prices = self.get_data()
        self.fx_series_dict = self.create_fx_series(self.adjusted_prices)
        self.std_dev_dict = self.calculate_std_dev(
            self.adjusted_prices, self.current_prices)
        self.position_contracts_dict = self.calculate_positions()
        self.calculate_quantstats()

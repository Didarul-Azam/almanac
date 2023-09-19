from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_multiple_trend_forecast_applied_and_adjustment

from almanac.strategy.baseStrategy import StrategyBase
from almanac.data.data import get_data_dict_with_carry
from typing import Union


class Strategy12(StrategyBase):
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
        fast_spans: list,
        use_buffer=True
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
            use_buffer=use_buffer
        )
        self.fast_spans = fast_spans
        self.carry_path = carry_path

    def get_data(self):
        self.adjusted_prices, self.current_prices, self.carry_prices = get_data_dict_with_carry(
            self.data_path, self.carry_path, self.instrument_list
        )
        return self.adjusted_prices, self.current_prices, self.carry_prices

    def calculate_positions(self):
        self.average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=self.std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,)

        self.position_contracts_dict = calculate_position_dict_with_multiple_trend_forecast_applied_and_adjustment(
            adjusted_prices_dict=self.adjusted_prices,
            std_dev_dict=self.std_dev_dict,
            average_position_contracts_dict=self.average_position_contracts_dict,
            fast_spans=self.fast_spans,)
        return self.position_contracts_dict

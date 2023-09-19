from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_forecast_applied
from almanac.analysis.carry import calculate_vol_adjusted_carry, calculate_seasonally_adjusted_carry
from almanac.strategy.baseStrategy import StrategyBase
from almanac.data.data import get_data_dict_with_carry
from typing import Union


class Strategy15(StrategyBase):
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
        self.carry_path = carry_path

    def get_data(self):
        self.adjusted_prices, self.current_prices, self.carry_prices = get_data_dict_with_carry(
            self.data_path, self.carry_path, self.instrument_list
        )
        return self.adjusted_prices, self.current_prices, self.carry_prices

    def calculate_positions(self):
        pass

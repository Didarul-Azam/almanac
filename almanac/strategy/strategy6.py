from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.data.data import get_data_dict
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict
from almanac.analysis.positions import calculate_position_dict_with_symmetric_trend_filter_applied
from almanac.strategy.baseStrategy import StrategyBase

from typing import Union


class Strategy6(StrategyBase):
    def __init__(
        self,
        data_path: str,
        fx_path: str,
        instrument_list: list,
        instrument_weights: dict,
        multipliers: dict,
        idm: Union[int, float],
        risk_target: Union[int, float],
        capital: int,
        cost_per_contract_dict: dict,
        use_buffer=False,
        get_carry=False
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

    def calculate_positions(self):
        self.average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=self.std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,
        )

        self.position_contracts_dict = calculate_position_dict_with_symmetric_trend_filter_applied(
            adjusted_prices_dict=self.adjusted_prices,
            average_position_contracts_dict=self.average_position_contracts_dict,
        )
        return self.position_contracts_dict

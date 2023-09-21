from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_forecast_applied
from almanac.data.normalised_price import calculate_normalised_price_dict
from almanac.strategy.baseStrategy import StrategyBase
from almanac.analysis.asset_class import calculate_asset_class_price_dict
from almanac.data.data import get_data_dict_with_carry
from typing import Union


class Strategy18(StrategyBase):
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
        rules_spec: list,
        asset_class_groupings: dict,
        use_buffer=True,
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
        self.rule_spec = rules_spec
        self.carry_path = carry_path
        self.asset_class_groupings = asset_class_groupings

    def calculate_positions(self):
        self.average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=self.std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,)

        self.normalised_price_dict = calculate_normalised_price_dict(
            adjusted_prices_dict=self.adjusted_prices,
            std_dev_dict=self.std_dev_dict,
        )
        self.asset_class_price_dict = calculate_asset_class_price_dict(
            normalised_price_dict=self.normalised_price_dict,
            asset_class_groupings=self.asset_class_groupings,
        )

        self.position_contracts_dict = calculate_position_dict_with_forecast_applied(
            adjusted_prices_dict=self.asset_class_price_dict,
            carry_prices_dict=self.carry_prices,
            std_dev_dict=self.std_dev_dict,
            average_position_contracts_dict=self.average_position_contracts_dict,
            rule_spec=self.rule_spec,)
        return self.position_contracts_dict

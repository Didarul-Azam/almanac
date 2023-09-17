from almanac.data.data import get_data_dict
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_trend_filter_applied
from almanac.analysis.calculate_returns import aggregate_returns
from almanac.strategy.baseStrategy import StrategyBase
from typing import Union


class Strategy5(StrategyBase):

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
        )

    def get_data(self):
        adjusted_prices, current_prices = get_data_dict(
            self.data_path, self.instrument_list)
        return adjusted_prices, current_prices

    def calculate_positions(self, adjusted_prices, std_dev_dict):
        average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,
        )

        position_contracts_dict = calculate_position_dict_with_trend_filter_applied(
            adjusted_prices_dict=adjusted_prices,
            average_position_contracts_dict=average_position_contracts_dict,
        )
        return position_contracts_dict

    def run_strategy(self):
        adjusted_prices, current_prices = self.get_data()
        self.fx_series_dict = self.create_fx_series(adjusted_prices)
        self.std_dev_dict = self.calculate_std_dev(
            adjusted_prices, current_prices)
        self.position_contracts_dict = self.calculate_positions(
            adjusted_prices, self.std_dev_dict)
        self.perc_return_dict = self.calculate_returns(
            self.position_contracts_dict, adjusted_prices)
        self.perc_return_agg = aggregate_returns(self.perc_return_dict)
        self.calculate_quantstats(self.perc_return_agg)

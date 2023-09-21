from almanac.config.instruments import *
from almanac.utils.utils import *
from almanac.analysis.positions import calculate_position_series_given_variable_risk_for_dict, calculate_position_dict_with_forecast_applied
from almanac.analysis.calculate_returns import calculate_returns, calculate_perc_returns_for_dict_with_costs, aggregate_returns
from almanac.analysis.buffering import apply_buffering_to_position_dict

from almanac.strategy.baseStrategy import StrategyBase
from almanac.data.data import get_data_dict_with_carry
from typing import Union
import quantstats as qs


class Strategy16(StrategyBase):
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
        rules_spec_ewmac: list,
        rules_spec_carry: list,
        carry_weight: int,
        ewmac_weight: int,
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
        self.rules_spec_ewmac = rules_spec_ewmac
        self.rules_spec_carry = rules_spec_carry
        self.carry_path = carry_path
        self.carry_weight = carry_weight
        self.ewmac_weight = ewmac_weight

    def calculate_positions(self):
        self.average_position_contracts_dict = calculate_position_series_given_variable_risk_for_dict(
            capital=self.capital,
            risk_target_tau=self.risk_target,
            idm=self.idm,
            weights=self.instrument_weights,
            std_dev_dict=self.std_dev_dict,
            fx_series_dict=self.fx_series_dict,
            multipliers=self.multipliers,)

        self.position_contracts_dict_ewmac = calculate_position_dict_with_forecast_applied(
            adjusted_prices_dict=self.adjusted_prices,
            carry_prices_dict=self.carry_prices,
            std_dev_dict=self.std_dev_dict,
            average_position_contracts_dict=self.average_position_contracts_dict,
            rule_spec=self.rules_spec_ewmac,)

        self.position_contracts_dict_carry = calculate_position_dict_with_forecast_applied(adjusted_prices_dict=self.adjusted_prices,
                                                                                           carry_prices_dict=self.carry_prices,
                                                                                           std_dev_dict=self.std_dev_dict,
                                                                                           average_position_contracts_dict=self.average_position_contracts_dict,
                                                                                           rule_spec=self.rules_spec_carry,)

        self.buffered_position_dict_ewmac = apply_buffering_to_position_dict(position_contracts_dict=self.position_contracts_dict_ewmac,
                                                                             average_position_contracts_dict=self.average_position_contracts_dict,)

        self.buffered_position_dict_carry = apply_buffering_to_position_dict(position_contracts_dict=self.position_contracts_dict_carry,
                                                                             average_position_contracts_dict=self.average_position_contracts_dict,)

        self.pre_cost_portfolio_returns_ewmac, self.post_cost_portfolio_returns_ewmac = calculate_returns(position_contracts=self.buffered_position_dict_ewmac,
                                                                                                          adjusted_prices=self.adjusted_prices,
                                                                                                          multipliers=self.multipliers,
                                                                                                          fx_series=self.fx_series_dict,
                                                                                                          capital=self.capital,
                                                                                                          cost_per_contract=self.cost_per_contract_dict,
                                                                                                          std_dev=self.std_dev_dict,
                                                                                                          aggregate=True)
        self.pre_cost_portfolio_returns_carry, self.post_cost_portfolio_returns_carry = calculate_returns(position_contracts=self.buffered_position_dict_carry,
                                                                                                          adjusted_prices=self.adjusted_prices,
                                                                                                          multipliers=self.multipliers,
                                                                                                          fx_series=self.fx_series_dict,
                                                                                                          capital=self.capital,
                                                                                                          cost_per_contract=self.cost_per_contract_dict,
                                                                                                          std_dev=self.std_dev_dict,
                                                                                                          aggregate=True)

    def run_strategy(self):
        self.adjusted_prices, self.current_prices, self.carry_prices = self.get_data()
        self.fx_series_dict = self.create_fx_series(self.adjusted_prices)
        self.std_dev_dict = self.calculate_std_dev(
            self.adjusted_prices, self.current_prices)
        self.calculate_positions()

        self.starting_portfolio_pre_cost = (
            self.pre_cost_portfolio_returns_ewmac * self.ewmac_weight +
            self.pre_cost_portfolio_returns_carry * self.carry_weight
        )
        self.starting_portfolio_post_cost = (
            self.post_cost_portfolio_returns_ewmac * self.ewmac_weight +
            self.post_cost_portfolio_returns_carry * self.carry_weight
        )

        self.relative_performance_pre_cost = self.pre_cost_portfolio_returns_ewmac - \
            self.pre_cost_portfolio_returns_carry
        self.relative_performance_post_cost = self.post_cost_portfolio_returns_ewmac - \
            self.post_cost_portfolio_returns_carry

        self.rolling_12_month_pre_cost = (
            self.relative_performance_pre_cost.rolling(BUSINESS_DAYS_IN_YEAR).sum() / self.risk_target)
        self.rolling_12_month_post_cost = (
            self.relative_performance_post_cost.rolling(BUSINESS_DAYS_IN_YEAR).sum() / self.risk_target)

        self.raw_weighting_pre_cost = 0.5 + self.rolling_12_month_post_cost / 2
        self.raw_weighting_post_cost = 0.5 + self.rolling_12_month_post_cost / 2

        self.clipped_weight_pre_cost = self.raw_weighting_pre_cost.clip(
            lower=0, upper=1)
        self.clipped_weight_post_cost = self.raw_weighting_post_cost.clip(
            lower=0, upper=1)

        self.smoothed_weight_pre_cost = self.clipped_weight_pre_cost.ewm(
            30).mean()
        self.smoothed_weight_post_cost = self.clipped_weight_post_cost.ewm(
            30).mean()
        self.weighted_portfolio_pre_cost = (self.pre_cost_portfolio_returns_ewmac * self.ewmac_weight * self.smoothed_weight_pre_cost
                                            + self.pre_cost_portfolio_returns_carry * self.carry_weight * (1 - self.smoothed_weight_pre_cost))

        self.weighted_portfolio_post_cost = (self.post_cost_portfolio_returns_ewmac * self.ewmac_weight * self.smoothed_weight_post_cost
                                             + self.post_cost_portfolio_returns_carry * self.carry_weight * (1 - self.smoothed_weight_post_cost))

        qs.reports.full(precost_returns=self.weighted_portfolio_pre_cost,
                        postcost_returns=self.weighted_portfolio_post_cost, benchmark='^GSPC')

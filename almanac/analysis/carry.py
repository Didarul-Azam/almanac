import pandas as  pd
from almanac.utils.standardDeviation import standardDeviation
from almanac.utils.utils import _total_year_frac_from_contract_series



def calculate_smoothed_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame, span: int
):

    risk_adj_carry = calculate_vol_adjusted_carry(
        stdev_ann_perc=stdev_ann_perc, carry_price=carry_price
    )

    smooth_carry = risk_adj_carry.ewm(span).mean()

    return smooth_carry


def calculate_vol_adjusted_carry(
    stdev_ann_perc: standardDeviation, carry_price: pd.DataFrame
) -> pd.Series:

    ann_carry = calculate_annualised_carry(carry_price)
    ann_price_vol = stdev_ann_perc.annual_risk_price_terms()

    risk_adj_carry = ann_carry.ffill() / ann_price_vol.ffill()

    return risk_adj_carry


def calculate_annualised_carry(
    carry_price: pd.DataFrame,
):

    ## will be reversed if price_contract > carry_contract
    raw_carry = carry_price.PRICE - carry_price.CARRY
    contract_diff = _total_year_frac_from_contract_series(
        carry_price.CARRY_CONTRACT
    ) - _total_year_frac_from_contract_series(carry_price.PRICE_CONTRACT)

    ann_carry = raw_carry / contract_diff

    return ann_carry

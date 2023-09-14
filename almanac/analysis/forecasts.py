import pandas as pd


def ewmac(adjusted_price: pd.Series, fast_span=16, slow_span=64) -> pd.Series:

    slow_ewma = adjusted_price.ewm(span=slow_span, min_periods=2).mean()
    fast_ewma = adjusted_price.ewm(span=fast_span, min_periods=2).mean()

    return fast_ewma - slow_ewma

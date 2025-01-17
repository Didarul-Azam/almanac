from scipy.stats import norm
import pandas as pd
import numpy as np
from almanac.utils.utils import periods_per_year,demeaned_remove_zeros
from almanac.config.configs import *
class Stats():
    def __init__(self,perc_return, at_frequency = NATURAL) -> None:
        self.perc_return = perc_return
        self.at_frequency = at_frequency
    
    def _sum_at_frequency(self):
        if self.at_frequency == NATURAL:
            return self.perc_return

        at_frequency_str_dict = {YEAR: "Y", WEEK: "7D", MONTH: "1M"}
        at_frequency_str = at_frequency_str_dict[self.at_frequency]

        perc_return_at_freq = self.perc_return.resample(at_frequency_str).sum()
        return perc_return_at_freq
    
    def _perc_return_at_freq(self):
        perc_return_at_freq =  self._sum_at_frequency()
        self.perc_return_at_freq = perc_return_at_freq

    
    def _ann_mean_given_frequency(self):
        perc_return_at_freq = self.perc_return_at_freq
        mean_at_frequency = perc_return_at_freq.mean()
        periods_per_year_for_frequency = periods_per_year(self.at_frequency)
        annualised_mean = mean_at_frequency * periods_per_year_for_frequency

        return annualised_mean

    def _ann_mean(self):
        ann_mean = self._ann_mean_given_frequency()
        self.ann_mean = ann_mean

    def _ann_std_given_frequency(self):
        std_at_frequency = self.perc_return_at_freq.std()
        periods_per_year_for_frequency = periods_per_year(self.at_frequency)
        annualised_std = std_at_frequency * (periods_per_year_for_frequency**0.5)

        return annualised_std
    
    def _ann_std(self):
        ann_std = self._ann_std_given_frequency()
        self.ann_std = ann_std
    def _sharpe_ratio(self):
        sharpe = self.ann_mean/self.ann_std
        self.sharpe = sharpe
    def _skew_at_freq(self):
        skew_at_freq = self.perc_return_at_freq.skew()
        self.skew_at_freq = skew_at_freq
    def _calculate_drawdown(self):
        perc_return = self.perc_return_at_freq
        cum_perc_return = perc_return.cumsum()
        max_cum_perc_return = cum_perc_return.rolling(
            len(perc_return) + 1, min_periods=1
        ).max()
        return max_cum_perc_return - cum_perc_return

    def _drawdowns(self):
        drawdowns = self._calculate_drawdown()
        self.drawdowns = drawdowns
        self.avg_drawdown = drawdowns.mean()
        self.max_drawdown = drawdowns.max()
    def _calculate_quant_ratio_upper(self):
        x_dm = demeaned_remove_zeros(self.perc_return_at_freq)
        raw_ratio = x_dm.quantile(1 - QUANT_PERCENTILE_EXTREME) / x_dm.quantile(
            1 - QUANT_PERCENTILE_STD
        )
        return raw_ratio / NORMAL_DISTR_RATIO
    def _calculate_quant_ratio_lower(self):
        x_dm = demeaned_remove_zeros(self.perc_return_at_freq)
        raw_ratio = x_dm.quantile(QUANT_PERCENTILE_EXTREME) / x_dm.quantile(
            QUANT_PERCENTILE_STD
        )
        return raw_ratio / NORMAL_DISTR_RATIO
    def _quant_ratio_lower(self):
        quant_ratio_lower = self._calculate_quant_ratio_lower()
        self.quant_ratio_lower = quant_ratio_lower
    def _quant_ratio_upper(self):
        quant_ratio_upper = self._calculate_quant_ratio_upper()
        self.quant_ratio_upper = quant_ratio_upper

    def stats(self,show=False):
        self._perc_return_at_freq()
        self._ann_mean()
        self._ann_std()
        self._sharpe_ratio()
        self._skew_at_freq()
        self._drawdowns()
        self._quant_ratio_lower()
        self._quant_ratio_upper()
        if show:
            return dict(
            ann_mean=self.ann_mean,
            ann_std=self.ann_std,
            sharpe_ratio=self.sharpe,
            skew=self.skew_at_freq,
            avg_drawdown=self.avg_drawdown,
            max_drawdown=self.max_drawdown,
            quant_ratio_lower=self.quant_ratio_lower,
            quant_ratio_upper=self.quant_ratio_upper,
        )
            
    def show_stats(self):
       return self.stats(show=True)
    
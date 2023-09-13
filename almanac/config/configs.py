from enum import Enum
from scipy.stats import norm
import pandas as pd
import numpy as np

DEFAULT_DATE_FORMAT = "%Y-%m-%d"
Frequency = Enum("Frequency", "Natural Year Month Week BDay")

NATURAL = Frequency.Natural
YEAR = Frequency.Year
MONTH = Frequency.Month
WEEK = Frequency.Week

BUSINESS_DAYS_IN_YEAR = 256
WEEKS_PER_YEAR = 52.25
MONTHS_PER_YEAR = 12
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60

PERIODS_PER_YEAR = {MONTH: MONTHS_PER_YEAR, WEEK: WEEKS_PER_YEAR, NATURAL:256, YEAR: 1}

QUANT_PERCENTILE_EXTREME = 0.01
QUANT_PERCENTILE_STD = 0.3
NORMAL_DISTR_RATIO = norm.ppf(QUANT_PERCENTILE_EXTREME) / norm.ppf(QUANT_PERCENTILE_STD)

from enum import Enum

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

PERIODS_PER_YEAR = {MONTH: MONTHS_PER_YEAR, WEEK: WEEKS_PER_YEAR, YEAR: 1}

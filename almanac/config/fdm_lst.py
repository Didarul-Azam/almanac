from scipy.interpolate import interp1d

FDM_LIST = {
    1: 1.0,
    2: 1.02,
    3: 1.03,
    4: 1.23,
    5: 1.25,
    6: 1.27,
    7: 1.29,
    8: 1.32,
    9: 1.34,
    10: 1.35,
    11: 1.36,
    12: 1.38,
    13: 1.39,
    14: 1.41,
    15: 1.42,
    16: 1.44,
    17: 1.46,
    18: 1.48,
    19: 1.50,
    20: 1.53,
    21: 1.54,
    22: 1.55,
    25: 1.69,
    30: 1.81,
    35: 1.93,
    40: 2.00,
}

fdm_x = list(FDM_LIST.keys())
fdm_y = list(FDM_LIST.values())

f_interp = interp1d(fdm_x, fdm_y, bounds_error=False, fill_value=2)

def get_fdm(rule_count):
    fdm = float(f_interp(rule_count))
    return fdm

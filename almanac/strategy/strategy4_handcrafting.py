from almanac.analysis.handcrafting import handcrafting_algo


portfolio_returns = 'almanac/sample_data/jumbo_instrument_returns.csv'

portfolio_weights = handcrafting_algo(portfolio_returns)
print(portfolio_weights)

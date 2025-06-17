import yfinance as yf
import backtrader as bt
import datetime
import pandas as pd

class SmaCross(bt.Strategy):
    params = dict(period_short=10, period_long=30)

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.period_short)
        sma2 = bt.ind.SMA(period=self.p.period_long)
        self.crossover = bt.ind.CrossOver(sma1, sma2)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()

def fetch_data(symbol='AAPL', start='2020-01-01', end='2024-01-01'):
    data = yf.download(symbol, start=start, end=end, auto_adjust=True)
    
    # Drop multi-index if present (happens when single ticker but multi-index)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # Rename to lowercase to match backtrader expectations
    data.columns = [col.lower() for col in data.columns]

    # Just keep the required OHLCV columns
    return data[['open', 'high', 'low', 'close', 'volume']]


def run_backtest(data):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(10000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()

if __name__ == '__main__':
    df = fetch_data('AAPL', '2020-01-01', '2024-01-01')
    run_backtest(df)



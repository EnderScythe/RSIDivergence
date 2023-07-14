import matplotlib.pyplot as plt
import pandas as pd
import talib
import seaborn as sns
import yfinance as yf
import math

fig, ax = plt.subplots(2, 1)


def identify_divergences(stock, timeframe):
    df = yf.download(tickers=stock, start=str(2023 - timeframe) + '-6-15', end='2023-6-16')
    rsi = pd.DataFrame(talib.RSI(df['Close']))
    stock_peaks = []
    stock_valleys = []
    rsi_peaks = []
    rsi_valleys = []
    for i in range(1, len(df['Close']) - 1):
        stock_info = {
            'Date': df.index[i].strftime('%Y-%m-%d'),
            'Price': df['Close'][i]
        }
        if math.isnan(rsi[0][i - 1]) or math.isnan(rsi[0][i + 1]) or math.isnan(rsi[0][i]):
            i += 1
        elif df['Close'][i] > df['Close'][i - 1] and df['Close'][i] > df['Close'][i + 1]:
            stock_peaks.append(stock_info)
        elif df['Close'][i] < df['Close'][i - 1] and df['Close'][i] < df['Close'][i + 1]:
            stock_valleys.append(stock_info)
    for i in range(1, len(rsi[0]) - 1):
        rsi_info = {
            'Date': rsi.index[i].strftime('%Y-%m-%d'),
            'RSI': rsi[0][i]
        }
        if math.isnan(rsi[0][i - 1]) or math.isnan(rsi[0][i + 1]) or math.isnan(rsi[0][i]):
            i += 1
        elif rsi[0][i] > rsi[0][i - 1] and rsi[0][i] > rsi[0][i + 1]:
            rsi_peaks.append(rsi_info)
        elif rsi[0][i] < rsi[0][i - 1 ] and rsi[0][i] < rsi[0][i + 1]:
            rsi_valleys.append(rsi_info)
    divergences = []
    for i in range(1, len(stock_peaks)):
        if (stock_peaks[i].get('Price') > stock_peaks[i - 1].get('Price')) and (rsi_peaks[i].get('RSI') < rsi_peaks[i - 1].get('RSI')):
            divergence = {
                'Start' : stock_peaks[i - 1].get('Date'),
                'End' : stock_peaks[i].get('Date'),
                'Start Price': stock_peaks[i - 1].get('Price'),
                'End Price': stock_peaks[i].get('Price'),
                'Start RSI': rsi_peaks[i - 1].get('RSI'),
                'End RSI': rsi_peaks[i].get('RSI'),
                'Flag': -1
            }
            divergences.append(divergence)
    for i in range(1, len(stock_valleys)):
        if (stock_valleys[i].get('Price') < stock_valleys[i - 1].get('Price')) and (rsi_valleys[i].get('RSI') > rsi_valleys[i - 1].get('RSI')):
            divergence = {
                'Start': stock_valleys[i - 1].get('Date'),
                'End': stock_valleys[i].get('Date'),
                'Start Price': stock_valleys[i - 1].get('Price'),
                'End Price': stock_valleys[i].get('Price'),
                'Start RSI': rsi_valleys[i - 1].get('RSI'),
                'End RSI': rsi_valleys[i].get('RSI'),
                'Flag' : 1
            }
            divergences.append(divergence)
    return df, rsi, divergences


def plot_graph(stock, time):
    df, rsi, divergences = identify_divergences(stock, time)
    sns.set_style("ticks")
    sns.lineplot(data=df, x='Date', y='Close', color='firebrick', ax=ax[0])
    sns.lineplot(data=rsi, x='Date', y=0, color='blue', ax=ax[1])
    sns.despine()
    plt.show()

user_input = input("Enter Stock: ")
time = int(input("Enter number of years: "))
plot_graph(user_input, time)
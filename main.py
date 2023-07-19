#All imports necessary
import matplotlib.pyplot as plt
import pandas as pd
import talib
import seaborn as sns
import math


# Change subplot numbers to have however many graphs as needed 
# First number increases subplots in rows, second number increases subplots in columns
fig, ax = plt.subplots(2, 1)
sns.set_style("ticks")
data = pd.read_csv('price_godbole.csv')

# Gets all  stock prices and dates and makes a pandas dataframe
def get_stock_info(stock):
    info = data.values.tolist()
    dates = []
    stock_price = []
    num = 0
    for i in range(len(info)):
        if info[i][0] == stock:
            num = i
            dates = info[1][1:len(info[1])]
            stock_price = info[num][1:len(info[num])]
            for j in range(len(stock_price)):
                stock_price[j] = float(stock_price[j])
            dates = dates[::-1]
            stock_price = stock_price[::-1]
            df = pd.DataFrame({
                'Date': dates,
                'Close': stock_price
            })
            return df
     
# Finds Divergences by finding local maxima and minima of both the stock price and RSI, and then returns divergences that are bullish ('Flag': 1) and bearish ('Flag': -1)
def identify_divergences(stock):
    df = get_stock_info(stock)
    rsi = pd.DataFrame({
        'Date': df['Date'],
        'RSI': talib.RSI(df['Close'])
        })
    stock_peaks = []
    stock_valleys = []
    rsi_peaks = []
    rsi_valleys = []
    for i in range(1, len(df['Close']) - 1):
        stock_info = {
            'Date': df['Date'][i],
            'Price': df['Close'][i]
        }
        if math.isnan(rsi['RSI'][i - 1]) or math.isnan(rsi['RSI'][i + 1]) or math.isnan(rsi['RSI'][i]):
            continue
        elif df['Close'][i] > df['Close'][i - 1] and df['Close'][i] > df['Close'][i + 1]:
            stock_peaks.append(stock_info)
        elif df['Close'][i] < df['Close'][i - 1] and df['Close'][i] < df['Close'][i + 1]:
            stock_valleys.append(stock_info)
    for i in range(1, len(rsi['RSI']) - 1):
        rsi_info = {
            'Date': rsi['Date'][i],
            'RSI': rsi['RSI'][i]
        }
        if math.isnan(rsi['RSI'][i - 1]) or math.isnan(rsi['RSI'][i + 1]) or math.isnan(rsi['RSI'][i]):
            continue
        elif rsi['RSI'][i] > rsi['RSI'][i - 1] and rsi['RSI'][i] > rsi['RSI'][i + 1]:
            rsi_peaks.append(rsi_info)
        elif rsi['RSI'][i] < rsi['RSI'][i - 1 ] and rsi['RSI'][i] < rsi['RSI'][i + 1]:
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

# Given a divergence, calculates buy return (bullish) or sell return (bearish) in a 21 day span
def calc_return(df, divergence):
    i = 0
    while divergence.get('End') != df['Date'][i]:
        i += 1
    days = []
    returns = []
    for j in range(1, 22):
        if(i + j < len(df['Close'])):
            ret = (df['Close'][i + j] - divergence.get('End Price')) * divergence.get('Flag')
            returns.append(ret)
            days.append(j)
        else:
            break
    div_curve = {
        'Days after Divergence': days,
        'Return': returns
    }
    return div_curve

#Asks a user for a stock and sets up counting and list variables that will be useful later
user_input = input("Enter Stock: ")
buy_returns = [0] * 21
bcount = [0] * 21
sell_returns = [0] * 21
scount = [0] * 21
days = []

df, rsi, divergences = identify_divergences(user_input)

# Takes all divergences found from user given stock and calculates mean buy and sell return for 21 days
for divergence in divergences:
    returns = calc_return(df, divergence)['Return']
    for i in range(len(returns)):
        if divergence['Flag'] == 1:
                buy_returns[i] += returns[i] 
                bcount[i] += 1
        else:
                sell_returns[i] += returns[i]
                scount[i] += 1

for i in range(len(buy_returns)):
    buy_returns[i] = buy_returns[i] / bcount[i]
for i in range(len(sell_returns)):
    sell_returns[i] = sell_returns[i] / scount[i]
for i in range(1, 22):
    days.append(i)

buy_df = pd.DataFrame({
    "Days after Divergence": days,
    "Buy Return": buy_returns
})         

sell_df = pd.DataFrame({
    "Days after Divergence": days,
    "Sell Return": sell_returns
})

# Uncomment to Graph Date vs Stock Price
# sns.lineplot(data=df, x='Date', y='Close', color='firebrick', ax=ax[0])
# Uncomment to Graph Date vs RSI Value
# sns.lineplot(data=rsi, x='Date', y='RSI', color='blue', ax=ax[1])
# (Make sure to double check subplot and axis values otherwise code will give an error)

# Displays 2 graphs: Days after Divergence (21 total) vs Mean Buy Return graph and Days after Divergence (21 total) vs Mean Sell Return graph
sns.lineplot(data=buy_df, x='Days after Divergence', y='Buy Return', marker = 'o', color='firebrick', ax=ax[0])
sns.lineplot(data=sell_df, x='Days after Divergence', y='Sell Return', marker = 'o', color='firebrick', ax=ax[1])
sns.despine()
plt.show()

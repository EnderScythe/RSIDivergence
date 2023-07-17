import matplotlib.pyplot as plt
import pandas as pd
import talib
import seaborn as sns
import yfinance as yf
import math

#ADD DOCUMENTATION

# Change subplot numbers to have however many graphs as needed 
# First number increases subplots in rows, second number increases subplots in columns
fig, ax = plt.subplots(2, 1)
sns.set_style("ticks")
data = pd.read_csv('price_godbole.csv')

def stock_list():
    stocks = data['Unnamed: 0'][2:len(data['Unnamed: 0'])]
    return stocks

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
            df = pd.DataFrame({
                'Date': dates,
                'Close': stock_price
            })
            return df
     

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
            i += 1
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
            i += 1
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
        'Buy Return': returns,
        'Sell Return': returns
    }
    return div_curve, returns
    
#user_input = input("Enter Stock: ")
#End date is set to June 16th 2023 (can change if necessary)
#start = input("Enter Start Date: ")
stocks = stock_list()
buy_returns = [0] * 21
bcount = 0
sell_returns = [0] * 21
scount = 0
days = []

for stock in stocks[1:20]:
    df, rsi, divergences = identify_divergences(stock)
    for div in range(len(divergences)):
        div_curve, returns = calc_return(df, divergences[div])
        
        #df_curve = pd.DataFrame(div_curve)
        for i in range(len(returns)): 
            if divergences[div].get('Flag') == 1:
                buy_returns[i] = buy_returns[i] + returns[i] 
            else:
                sell_returns[i] = sell_returns[i] + returns[i]
        if divergences[div].get('Flag') == 1:
            bcount += 1
        else:
            scount += 1

for i in range(len(buy_returns)):
    buy_returns[i] = buy_returns[i] / bcount
for i in range(len(sell_returns)):
    sell_returns[i] = sell_returns[i] / scount
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

#print(type(stock_list()[2]))
# Uncomment to Graph Date vs Stock Price on Closing
#sns.lineplot(data=df, x='Date', y='Close', color='firebrick', ax=ax[0])
# Uncomment to Graph Date vs RSI Value
#sns.lineplot(data=rsi, x='Date', y=0, color='blue', ax=ax[1])

sns.lineplot(data=buy_df, x='Days after Divergence', y='Buy Return', color='firebrick', ax=ax[0])
sns.lineplot(data=sell_df, x='Days after Divergence', y='Sell Return', color='firebrick', ax=ax[1])
sns.despine()
plt.show()

# if divergences[0].get('Flag') == 1:
#     sns.lineplot(data=df_curve, x='Days after Divergence', y='Buy Return', color='firebrick', ax = ax[2])
# else:
#     sns.lineplot(data=df_curve, x='Days after Divergence', y='Sell Return', color='firebrick', ax = ax[2])
#All imports necessary
import matplotlib.pyplot as plt
import pandas as pd
import talib
import seaborn as sns
import math
import numpy as np
import sys


# Change subplot numbers to have however many graphs as needed 
# First number increases subplots in rows, second number increases subplots in columns
fig, ax = plt.subplots(2, 1)
sns.set_style("ticks")
data = pd.read_csv('price_godbole.csv')
info = data.values.tolist()

# Gets all  stock prices and dates and makes a pandas dataframe
def get_stock_info(stock):
    dates = []
    stock_price = []
    num = 0
    for i in range(len(info)):
        if info[i][0] == stock:
            num = i
            #Remove 21 when done testing
            dates = info[1][1:len(info[1])]
            stock_price = info[num][1:len(info[num])]
            for j in range(len(stock_price)):
                stock_price[j] = float(stock_price[j])
            dates = dates[::-1]
            stock_price = stock_price[::-1]
            df = pd.DataFrame({
                'Date': dates,
                'Close': stock_price,
                'RSI': list(talib.RSI(np.array(stock_price)))
            })
            return df

#returns a list of all the stock names
def get_stock_list():
    stock_list = []
    for i in range(2, len(info)):
        stock_list.append(info[i][0])
    return stock_list

#finds all nan values in a given list and returns the starting and ending points of actual values
def find_nan(temp):
    start = 0
    end = 0
    for i in range(len(temp)):
        if math.isnan(temp[i]) is False:
            start = i
            break
    temp = temp[::-1]
    for i in range(len(temp)):
        if math.isnan(temp[i]) is False:
            end = len(temp) - i
            break
    return start, end

#removes all nan values and restructures dataframe to have just the dates where the stock and rsi are not nan
def clean_info(df):
    m_start = 0
    m_end = 0
    s_start, s_end = find_nan(list(df['Close']))
    rsi_start, rsi_end = find_nan(list(df['RSI']))
    if s_start >= rsi_start:
        m_start = s_start
    else:
        m_start = rsi_start
    if s_end >= rsi_end:
        m_end = rsi_end
    else:
        m_end = s_end
    newdf = pd.DataFrame({
        'Date': list(df['Date'][m_start:m_end]),
        'Close': list(df['Close'][m_start:m_end]),
        'RSI': list(df['RSI'][m_start:m_end])
    })
    return newdf

# Finds Divergences by finding local maxima and minima of both the stock price and RSI, and then returns divergences that are bullish ('Flag': 1) and bearish ('Flag': -1)
def identify_divergences(stock, period):
    df_temp = clean_info(get_stock_info(stock))
    df = pd.DataFrame({
        'Date': df_temp['Date'],
        'Close': df_temp['Close']
    })
    rsi = pd.DataFrame({
        'Date': df_temp['Date'],
        'RSI': df_temp['RSI']
        })
    stock_peaks = []
    stock_valleys = []
    rsi_peaks = []
    rsi_valleys = []
    stock_date = ''
    rsi_date = ''
    maxima = sys.float_info.min
    minima = sys.float_info.max
    
    for i in range(0, len(df['Close']), period):
        for j in range(period):
          if i + j < len(df['Close']):
              if maxima < df['Close'][i + j]:
                  maxima = df['Close'][i + j]
              elif minima > df['Close'][i + j]:
                  minima = df['Close'][i + j]
              stock_date = df['Date'][i + j]
          else:
            break
        stock_peaks.append({
            'Date': stock_date,
            'Price': maxima 
        })
        stock_valleys.append({
            'Date': stock_date,
            'Price': minima 
        })
        maxima = sys.float_info.min
        minima = sys.float_info.max
      
    for i in range(0, len(rsi['RSI']), period):
        for j in range(period):
          if i + j < len(rsi['RSI']):
              if maxima < rsi['RSI'][i + j]:
                  maxima = rsi['RSI'][i + j]
              elif minima > rsi['RSI'][i + j]:
                  minima = rsi['RSI'][i + j]
              rsi_date = rsi['Date'][i + j]
          else:
            break
        rsi_peaks.append({
            'Date': rsi_date,
            'RSI': maxima 
        })
        rsi_valleys.append({
            'Date': rsi_date,
            'RSI': minima 
        })
        maxima = sys.float_info.min
        minima = sys.float_info.max

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


period = int(input('Enter Period (in days): '))
buy_returns = [0] * 21
bcount = [0] * 21
sell_returns = [0] * 21
scount = [0] * 21
days = list(range(1,  22))

#If loop is false, it asks the user for a stock and then calculates average returns for it
#If loop is true, than it loops through all stocks in the csv and returns average returns for it
def stock_iteration(loop):
    stocks = []
    if loop is False:
        user_input = input("Enter Stock: ")
        stocks.append(user_input)
    else:
        stocks = get_stock_list()
    for stock in stocks:
        df, rsi, divergences = identify_divergences(stock, period)
        for divergence in divergences:
            returns = calc_return(df, divergence)['Return']
            for i in range(len(returns)):
                if divergence['Flag'] == 1:
                    buy_returns[i] += round(returns[i], 2)
                    bcount[i] += 1
                else:
                    sell_returns[i] += round(returns[i], 2)
                    scount[i] += 1
    return df, rsi, divergences   

#Finds a divergence for a specific date given the divergences array and date of choice
def find_divergence(divergences, date):
    for divergence in divergences:
        if divergence.get('End') == date:
            return divergence
    

# Takes all divergences found from user given stock and calculates mean buy and sell return for 21 days
#For 1 stock through user input enter False, for looping through all stocks enter True
df, rsi, divergences = stock_iteration(False)

#Prints List of all divergences with start times, end times, and stock and rsi prices, and flag (only works if Loop is False)
#print(divergences)

#Prints divergence for a specific date by replacing mm/dd/yy with a actual date (If no divergence is found on that date, then it will output 'None')
#print(find_divergence(divergences, 'mm/dd/yy'))

#Prints divergence for the last day on the csv (Again if no divergence is found on that date, then it will output 'None')
#end_date = '6/16/23'
#print(find_divergence(divergences, '6/16/23'))

#Prints return price for a specific divergence and days after specific divergence (i is a number asscoiated with a divergence in the divergences list) (only works if Loop is False)
#returns = calc_return(df, divergences[i])

for i in range(len(buy_returns)):
    buy_returns[i] = buy_returns[i] / bcount[i]
for i in range(len(sell_returns)):
    sell_returns[i] = sell_returns[i] / scount[i]

buy_df = pd.DataFrame({
    "Days after Divergence": days,
    "Buy Return": buy_returns
})         

sell_df = pd.DataFrame({
    "Days after Divergence": days,
    "Sell Return": sell_returns
})
# Displays 2 graphs: Days after Divergence (21 total) vs Mean Buy Return graph and Days after Divergence (21 total) vs Mean Sell Return graph
sns.lineplot(data=buy_df, x='Days after Divergence', y='Buy Return', color='firebrick', ax=ax[0])
sns.lineplot(data=sell_df, x='Days after Divergence', y='Sell Return', color='firebrick', ax=ax[1])

# Uncomment to Graph Date vs Stock Price (Only works if Loop is False)
#sns.lineplot(data=df, x='Date', y='Close', color='firebrick', ax=ax[0])
# Uncomment to Graph Date vs RSI Value (Only works if Loop is False)
#sns.lineplot(data=rsi, x='Date', y='RSI', color='blue', ax=ax[1])
# (Make sure to double check subplot and axis values otherwise code will give an error)


sns.despine()
plt.show()



# RSIDivergence

THIS PROGRAM ONLY WORKS ON PYTHON 3.9.
Currently, the Talib whl files are only up to Python 3.9.
If you want to use a different version, you must download the appropriate Talib whl file for that version (python 3.9>=).

RSI or relative strength index allows someone to measure the speed and magnitude of a paticular stock.
An RSI Divergence is indicated when the stock price and the RSI value go in opposite directions. This is very helpful when trading stocks because it is a good indication to show if a stock will increase or decrease in value.
This program helps see when a divergence will occur and whether it will increase or decrease the stock price, thus giving the user to make a choice to buy or sell the stock.
The program will have different outputs based on the parameters given to the 'stock_iteration' function.
If the boolean is true, than the program will loop through the stock list given and will generate an average buy (bullish divergence) and sell (bearish divergence) return looking out 21 days and display the info on a graph. 
If the boolean is false, than the program will ask you for a specific stock and will calculate buy and sell return looking out 21 days for just that 1 stock and display the info on a graph.
(Note: It will calculate divergences based on the period given during user input and will calculate local maxima and minima in that period)
If the boolean is false, you can also uncomment the bottom 2 lines in the program to generate a graph of the date held against the stock price and the rsi value.







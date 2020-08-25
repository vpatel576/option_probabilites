##Importing Libraries

from math import sqrt
from scipy.stats import norm
from numpy import diff as df
import pandas as pd
import pandas_datareader as web
from datetime import datetime, date
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.interpolate import interp1d

from bs4 import BeautifulSoup
import requests

from black_scholes_functions import d,call_price,put_price
from td_data import get_hist

#Inputs for company ticker and Puts or Calls
ticker = input('Ticker: ')
C_or_P = input('Calls or Put: ')

#Getting data from yahoo finance
#exp_dates gets all the expiration dates available
comp = yf.Ticker(ticker)
exp_dates = comp.options

##Gathering current price data and the ten-yr tresury yield
curr_price = web.DataReader(ticker,'yahoo',(date.today())-timedelta(days=1),date.today())['Adj Close'][-1]
r = requests.get('https://www.cnbc.com/quotes/?symbol=US10Y')
soup = BeautifulSoup(r.text, features="lxml")
ten_yr = float(soup.find('table',{'class':'quote-horizontal regular'}).find_all('tr')[-1].find('span').text)


#Here all the volatility and strike price data is gathered

vol_dist = []
strikes = []
all_strike = np.linspace(curr_price*(1-.8), curr_price*(1+.8), 30)

#Grabbing options data

data = get_hist(symbol = ticker,contractType=C_or_P.upper(),strikeCount=10)
dates = list(data['callExpDateMap'].keys())
strikes = list(data['callExpDateMap'][dates[0]].keys())

strikes = []
vol = []

for d in dates:
    s = list(data['callExpDateMap'][d].keys())
    v = []
    for str in s:
        v.append(data['callExpDateMap'][d][str][0]['volatility'])
    
    v = [float(i) for i in v]
    s = [float(i) for i in s]
    
    #Based on the highest and lowest strike price for each expiration date, it interpolates the existing data 
    #and creates a second degree function.Currently it only uses 30 data points but that number can increase it to get 
    #smoother distribution
    
    poly_deg = 2
    coefs = np.polyfit(s, v, poly_deg)
    vols = np.polyval(coefs, all_strike)
    vol_dist.append(list(vols))
    strikes.append(list(all_strike))
    
    #Once the volatility values are obtained (in variable 'vols'), a plot of it is created.
    #it looks at +- 80% of current strike price and makes sure strike price range is same for all the expiration dates
    
    plt.plot(all_strike,vols, label = d)
    plt.axvline(curr_price, color='red', linestyle='--')
    plt.xlabel('Strike Prices')
    plt.ylabel('Implied Volatility')
    plt.title(C_or_P.capitalize())    
    plt.legend(bbox_to_anchor=(1.0, 1.0))

plt.show()


#Here call price_data is calculated based on the volatility values collected earlier
call_price_data = []

for i in range(len(strikes)):
    call_price_data.append([])
    date_str = exp_dates[i]
    exp_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    diff = exp_date-date.today()
    no_days = diff.days

    for j in range(len(strikes[i])):
        d_vals = d(sigma=vol_dist[i][j], S=curr_price, K=strikes[i][j], r=ten_yr, t= (no_days/365))
        price = call_price(sigma=vol_dist[i][j], S=curr_price, K= strikes[i][j], r=ten_yr, t=no_days/365, d1=d_vals[0], d2=d_vals[1])
        call_price_data[-1].append(price)

#Taking double derivative of the call prices to get probability distribution of the each strike price. This is based on the principle developed by Breeden and Litzenberger 
distributions = []
for i in range(len(call_price_data)):
    dist = list(df(df(call_price_data[i])))
    
    #data is normalized to make sure the distributions add up to 1. 
    
    prop_dist = [i/sum(dist) for i in dist]
    distributions.append(prop_dist)


# For values that were far out, the disribution was not normal. It seemed like the bell-curve was not filled up all the way or it was only one sided distribution curve.

distributions = distributions[:10]
strikes = strikes[:10]

#Here, based on the probalilities for each strike price, the random.choice function chooses 10,000 different values

predicted_vals = []
for j in range(len(distributions)):
    ##Changes -ve probabilites to 0
    for k in range(len(distributions[j])):
        if distributions[j][k] < 0:
            distributions[j][k] = 0
            
    prob_d = [i/sum(distributions[j]) for i in distributions[j]]
    vals_pre = np.random.choice(strikes[j][:-2],10000,True,prob_d)
    new_pred = [round(i,2) for i in vals_pre]
    predicted_vals.append(new_pred)    


# Based on the predicted values a histrogram is created
# Y-axis is the frequency of each bin and x axis shows the strike prices
# Red line is the current price
# Black line is the average of all the predicted prices for a specific expiration date

for i in range(len(predicted_vals)):
    plt.hist(predicted_vals[i])
    plt.axvline(curr_price, color = 'red', label = str(curr_price,2) + ' Curr. Val')
    plt.axvline(np.mean(predicted_vals[i]), color = 'black', linestyle= '--',label= str(round(np.mean(predicted_vals[i]),2)) + ' Pred. Val') 
    plt.title(exp_dates[i])
    plt.legend()
    plt.show()

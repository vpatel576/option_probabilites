api_key_td = ###

def get_hist(**kwargs):
    url ='https://api.tdameritrade.com/v1/marketdata/chains'
    
    params = {}
    params.update({'apikey':api_key_td})
    
    for arg in kwargs:
        parameter = {arg: kwargs.get(arg)}
        params.update(parameter)
        
    return requests.get(url, params=params).json()

#Grabbing options data

data = get_hist(symbol = 'T',contractType='ALL',strikeCount=10)
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
    
    strikes.append(s)
    vol.append(v)

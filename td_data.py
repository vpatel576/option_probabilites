api_key_td = ###

def get_hist(**kwargs):
    url ='https://api.tdameritrade.com/v1/marketdata/chains'
    
    params = {}
    params.update({'apikey':api_key_td})
    
    for arg in kwargs:
        parameter = {arg: kwargs.get(arg)}
        params.update(parameter)
        
    return requests.get(url, params=params).json()

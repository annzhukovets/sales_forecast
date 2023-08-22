import requests

item = {
    'Date' : '2011-12-10',
    'StockCode' : 85123
}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=item)
print(response.json())

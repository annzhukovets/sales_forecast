import mlflow
import pandas as pd
from flask import Flask, request, jsonify


RUN_ID = 'ebf906765802473da4720b48209d1843'

logged_model = f's3://sales-forecast-bucket/3/{RUN_ID}/artifacts/models'
model = mlflow.pyfunc.load_model(logged_model)
historical_data = f's3://sales-forecast-bucket/data/historical_data.csv'

def create_features(df, features, lags = [28], wins = [7,28]):
    df = pd.read_csv(df)
    df = pd.concat([df, features], ignore_index=True)
    lag_cols = [f"lag_{lag}" for lag in lags ]

    for lag, lag_col in zip(lags, lag_cols):
        df = df[df['StockCode'] == features.iloc[0]['StockCode']].copy()
        df[lag_col] = df[['StockCode','Quantity']].groupby('StockCode')['Quantity'].shift(lag).fillna(-1)

    for win in wins :
        for lag,lag_col in zip(lags, lag_cols):
            df[f"rmean_{lag}_{win}"] = df[['StockCode', lag_col]].groupby('StockCode')[lag_col].transform(lambda x : x.rolling(win).mean()).fillna(-1)
            
    return df.iloc[len(df)-1]

def prepare_features(item):
    item_df = pd.DataFrame(item, index=[0])
    features = pd.DataFrame()
    features["Date"] = pd.to_datetime(item_df['Date'])
    features['Year'] = features['Date'].dt.year
    features['Quarter'] = features['Date'].dt.quarter
    features['Month'] = features['Date'].dt.month
    features['Week'] = features['Date'].dt.isocalendar().week
    features['Weekday'] = features['Date'].dt.weekday
    features['DayOfYear'] = features['Date'].dt.dayofyear
    features['Day'] = features['Date'].dt.day
    features['Date'] = features['Date'].dt.date
    features['StockCode'] = item_df['StockCode']

    lag_features = create_features(historical_data, features)
    features['lag_28'] = lag_features['lag_28']
    features['rmean_28_7'] = lag_features['rmean_28_7']
    features['rmean_28_28'] = lag_features['rmean_28_28']
    features.drop(['Date'], axis = 1, inplace = True)

    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('sales-forecast')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    item = request.get_json()

    features = prepare_features(item)
    pred = predict(features)

    result = {
        'Quantity': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)

import warnings
import numpy as np
import pandas as pd
import seaborn as sns
sns.set()
warnings.filterwarnings('ignore')

INPUT_PATH = '../data/data.csv'
OUTPUT_PATH = f's3://sales-forecast-bucket/data/historical_data.csv'

def count_numeric_chars(l):
    return sum(1 for c in l if c.isdigit())

def count_upper_chars(l):
    return sum(1 for c in l if c.isupper())

def create_features(df, lags = [28], wins = [7,28]):
    lag_cols = [f"lag_{lag}" for lag in lags ]
    for lag, lag_col in zip(lags, lag_cols):
        df[lag_col] = df[['StockCode','Quantity']].groupby('StockCode')['Quantity'].shift(lag).fillna(-1)

    for win in wins :
        for lag,lag_col in zip(lags, lag_cols):
            df[f"rmean_{lag}_{win}"] = df[['StockCode', lag_col]].groupby('StockCode')[lag_col].transform(lambda x : x.rolling(win).mean()).fillna(-1)
        
    return df

def prepare_historical_data(input_path):
    print('Processing data...')
    ecommerce_data = pd.read_csv(input_path, encoding='ISO-8859-1', dtype={'CustomerID': str})

    data = ecommerce_data.loc[(ecommerce_data['CustomerID'].isnull()==False) & (ecommerce_data['Description'].isnull()==False)].copy()

    data['IsCancelled']=np.where(data['InvoiceNo'].apply(lambda no: no[0]=="C"), True, False)
    data = data.loc[data['IsCancelled']==False].copy()
    data = data.drop('IsCancelled', axis=1)

    data = data[data['Quantity'] != 80995]

    data["InvoiceDate"] = pd.to_datetime(data['InvoiceDate'], cache=True)

    data['StockCodeLength'] = data['StockCode'].apply(len)
    data['nNumericStockCode'] = data['StockCode'].apply(count_numeric_chars)
    data = data.loc[(data['nNumericStockCode'] == 5)].copy()
    data['StockCode'] = data['StockCode'].apply(lambda x: x[:5])
    data['StockCode'] = data['StockCode'].astype(np.int64)

    data['UpCharsInDescription'] = data['Description'].apply(count_upper_chars)
    data = data.loc[data['UpCharsInDescription'] > 5].copy()
    data = data.drop(['nNumericStockCode', 'StockCodeLength', 'UpCharsInDescription'], axis=1)

    data = data.loc[(data['UnitPrice'] > 0.1) & (data['UnitPrice'] < 20)].copy()
    data = data.loc[data['Quantity'] < 55].copy()

    data['Revenue'] = data['Quantity'] * data['UnitPrice']

    data['Year'] = data['InvoiceDate'].dt.year
    data['Quarter'] = data['InvoiceDate'].dt.quarter
    data['Month'] = data['InvoiceDate'].dt.month
    data['Week'] = data['InvoiceDate'].dt.isocalendar().week
    data['Weekday'] = data['InvoiceDate'].dt.weekday
    data['Day'] = data['InvoiceDate'].dt.day
    data['DayOfYear'] = data['InvoiceDate'].dt.dayofyear
    data['Date'] = pd.to_datetime(data[['Year', 'Month', 'Day']])

    grouped_features = ['Date', 'Year', 'Quarter','Month', 'Week', 'Weekday', 'DayOfYear', 'Day', 'StockCode']
    daily_data = pd.DataFrame(data.groupby(grouped_features)['Quantity'].sum(),
                            columns=['Quantity'])
    daily_data['Revenue'] = data.groupby(grouped_features)['Revenue'].sum()
    daily_data = daily_data.reset_index()
    low_quantity = daily_data['Quantity'].quantile(0.01)
    high_quantity = daily_data['Quantity'].quantile(0.99)
    low_revenue = daily_data['Revenue'].quantile(0.01)
    high_revenue = daily_data['Revenue'].quantile(0.99)
    daily_data = daily_data.loc[(daily_data['Quantity'] >= low_quantity) & (daily_data['Quantity'] <= high_quantity)]
    daily_data = daily_data.loc[(daily_data['Revenue'] >= low_revenue) & (daily_data['Revenue'] <= high_revenue)]

    daily_data = create_features(daily_data)

    return daily_data

def split_data(daily_data):
    print('Splitting data...')
    cutoff = daily_data['Date'].max() - pd.to_timedelta(28, unit = 'D')
    X_train = daily_data.loc[daily_data['Date'] < cutoff].copy()
    X_val = daily_data.loc[daily_data['Date'] >= cutoff].copy()
    y_train = X_train['Quantity'].copy()
    y_val = X_val['Quantity'].copy()

    X_train.drop(['Quantity', 'Revenue', 'Date'], axis = 1, inplace = True)
    X_val.drop(['Quantity', 'Revenue', 'Date'], axis = 1, inplace = True)

    return (X_train, y_train, X_val, y_val)

def save_data(df, output_path):
    print('Saving data to the AWS S3 bucket...')
    df.to_csv(output_path, index=False)

def run(type: str = "historical", save: bool = True):
    if type == "historical":
        data = prepare_historical_data(INPUT_PATH)
        if save:
            save_data(data, OUTPUT_PATH)
    if type == "train":
        data = pd.read_csv(OUTPUT_PATH)
        X_train, y_train, X_val, y_val = split_data(data)
        return X_train, y_train, X_val, y_val


if __name__ == '__main__':
    run()






# E-Commerce Sales Forecast Project

This repository contains the code and resources for an E-Commerce Sales Forecasting project. The goal of this project is to predict the daily sales of items based on stock code and date. Accurate sales forecasts are crucial for optimizing inventory management, resource allocation, and overall business planning in the e-commerce industry.

## Introduction
Accurate sales forecasting is essential for e-commerce businesses to effectively plan their inventory, marketing strategies, and operational resources. This project aims to develop a predictive model that can forecast daily sales of items based on historical data, including stock code and date information.

## Dataset
The dataset used for this project consists of historical sales data containing the following attributes:

- **InvoiceNo**: Invoice number that consists 6 digits. If this code starts with letter 'C', it indicates a cancellation.
- **StockCode**: Product code that consists 5 digits.
- **Description**: Product name.
- **Quantity**: The quantities of each product per transaction
- **InvoiceDate**: Represents the day and time when each transaction was generated.
- **UnitPrice**: Product price per unit.
- **CustomerID**: Customer number that consists 5 digits. Each customer has a unique customer ID.
- **Country**: Name of the country where each customer resides.
The dataset is available in the data/ directory and is named data.csv.

## Project Structure
```
sales-forecast/
│
├── data/
│   ├── data.csv
│
├── notebooks/
│   ├── sales_forecast_EDA.ipynb
│
├── src/
│   ├── prepare_data.py
│   ├── predict.py
│   ├── test.py
│
├── README.md
│
├── Dockerfile
│
├── Pipfile
│
└── Pipfile.lock
```

- **data/**: Contains the dataset used for the project.
- **notebooks/**: Jupyter notebook for data exploration,model training, experiment tracking and model registry.
- **src/**: Source code for data preparation, prediction and testing.
- **README.md**: You are here!
- **Dockerfile**: instructions for building a Docker image.
- **Pipfile**: Required packages.
- **Pipfile.lock**: Dependencies for required packeges.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/annzhukovets/sales_forecast.git
```

2. Navigate to the project directory:

```bash
cd sales_forecast
```

3. Build Docker image:

```bash
docker build -t sales_forecast:v1 .
```

4. Run the image:

```bash
docker run -it --rm -p 9696:9696 -e AWS_ACCESS_KEY_ID="{YOUR_AWS_ACCESS_KEY_ID}" -e AWS_SECRET_ACCESS_KEY="{YOUR_AWS_SECRET_ACCESS_KEY}" -e AWS_DEFAULT_REGION="{YOUR_AWS_REGION}" sales_forecast:v1
```

5. Test the model deployment (in a new terminal tab):

```bash
cd src/
python test.py
```

## Usage
1. Explore the dataset, train and evaluate the sales forecasting model using the notebooks/sales_forecast_EDA.ipynb notebook.
2. Utilize the scripts in the src/ directory to preprocess data and predict sales for particular date.

## Model
The forecasting model employed in this project uses a time-series approach, incorporating historical sales data, stock code information, and date features to predict future sales.

## Evaluation
The performance of the model is evaluated using appropriate metric such as Root Mean Squared Error (RMSE).

## Results
The results of the sales forecasting model are documented in the notebooks/sales_forecast_EDA.ipynb notebook. Visualizations and performance metrics are provided to assess the accuracy of the predictions.

## Future Enhancements
Set workflow orchestration
Establish model monitoring
Write unit and integration tests
Implement more advanced time-series forecasting techniques.
Explore the impact of external factors (e.g., promotions, holidays) on sales.
Develop a web interface for users to input stock codes and obtain sales forecasts.

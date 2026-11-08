"""Space-weather forecasting for the NASA Beyond Earth app.

config   what is forecast (measurements, horizons, storm events) and how the data is split
data     reading the 5-minute OMNI file, features (past values only), storm events, data health
train    trains and tests the models, saves them in forecast/models/ and the scores in numbers/
service  everything the Predictions page and the API ask for
api      the same functions over HTTP (FastAPI):  uvicorn forecast.api:app --port 8600
"""

import pandas as pd
import streamlit as st  
import requests
import glob
from sqlalchemy import create_engine

# Establish connection to MySQL database using SQLAlchemy
def load_data_from_mysql(host, user, password, database, query):
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    data = pd.read_sql(query, engine)
    return data

# Example usage
host = 'localhost'
user = 'root'
password = ''
database = 'currency_data22'
query = 'SELECT * FROM currency_rates22'

# Load data into a Pandas DataFrame
#df = load_data_from_mysql(host, user, password, database, query)
#st.write(df)

# Function to preprocess currency data
def preprocess_currency_data(directory):
    query = "SELECT * FROM currency_rates22"
    data = load_data_from_mysql(host, user, password, database, query)
    for column in data.columns:
        data[column] = data[column].ffill()  # Forward fill for time series
        if column != 'Date':
            data[column] = data[column].fillna(data[column].mean())  # Mean imputation for numeric columns

# Function to get current exchange rate
def get_current_exchange_rate(base, target):
    url = f'https://api.exchangerate-api.com/v4/latest/{base}'
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json()['rates']
        return rates.get(target, None)
    return None

# Function to compute total value of a currency basket
def compute_basket_value(basket_weights, base_currency):
    total_value = 0
    for currency, weight in basket_weights.items():
        rate = get_current_exchange_rate(base_currency, currency)
        if rate is not None:
            total_value += rate * weight
        else:
            st.warning(f"Rate for {currency} could not be retrieved.")
    return total_value

# Function to plot currency data
def plot_currency_data(data, currency, time_frame):
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)

    if time_frame == "Weekly":
        resampled_data = data[currency].resample('W').mean()
    elif time_frame == "Monthly":
        resampled_data = data[currency].resample('ME').mean()
    elif time_frame == "Quarterly":
        resampled_data = data[currency].resample('QE').mean()
    elif time_frame == "Yearly":
        resampled_data = data[currency].resample('YE').mean()

    st.line_chart(resampled_data)

# Configure Streamlit interface
st.set_page_config(page_title="Currency Exchange Tracker", layout="wide")

# Preprocess currency data
data_directory = r"C:\Users\DELL\Documents\Code\mitwpu-team_4-currency_exchange\conversion_rates"
preprocess_currency_data(data_directory)

# Page title
st.markdown("<h1 style='text-align: center; color: #003366; background-color: #E6F2FF; padding: 20px; border-radius: 10px;'>Currency Exchange Tracker</h1>", unsafe_allow_html=True)

# Sidebar for user inputs
with st.sidebar:
    st.header("Currency Selection")
    currency_df = load_data_from_mysql(host, user, password, database, query)
    available_currencies = currency_df.columns[1:]

    currency_from = st.selectbox('From Currency:', available_currencies)
    currency_to = st.selectbox('To Currency:', available_currencies)
    selected_year = st.selectbox('Year of Data:', [str(year) for year in range(2012, 2023)])

# Load the selected year's data
selected_data = load_data_from_mysql(host, user, password, database, query)

if 'Date' in selected_data.columns and currency_from in selected_data.columns and currency_to in selected_data.columns:
    current_exchange = (selected_data[currency_to].iloc[-1] / selected_data[currency_from].iloc[-1]) if not selected_data[currency_from].isna().all() else None
else:
    current_exchange = None

# Display current exchange rate
st.markdown(f"**Current Exchange Rate:** 1 {currency_from} = {current_exchange:.4f} {currency_to}" if current_exchange else "Exchange rate information is not available.")

# Custom Currency Basket Feature
st.header("Create Your Custom Currency Basket")
basket_selection = st.multiselect("Choose Currencies for Your Basket", available_currencies, default=[available_currencies[0]])
basket_weights = {currency: st.number_input(f"Weight for {currency} (%)", min_value=0.0, max_value=100.0, value=20.0) for currency in basket_selection}

# Calculate basket value
if st.button("Calculate Basket Value"):
    basket_total_value = compute_basket_value({curr: weight / 100 for curr, weight in basket_weights.items()}, currency_from)
    st.success(f"Total Value of Your Basket in {currency_from}: {basket_total_value:.2f}" if basket_total_value > 0 else "Total value is 0. Check weights or rates.")

# Graph visualization section
st.header("Graph Visualization")
time_frame = st.radio("Select Time Frame for Chart Display", ["Weekly", "Monthly", "Quarterly", "Yearly"])
if time_frame:
    plot_currency_data(selected_data, currency_from, time_frame)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Developed by Team 4</p>", unsafe_allow_html=True)

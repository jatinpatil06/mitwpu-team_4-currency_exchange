import pandas as pd
import streamlit as st
import requests
import glob
import os

# Function to preprocess currency data
def preprocess_currency_data(directory):
    files = glob.glob(f"{directory}/*.csv")
    for file in files:
        data = pd.read_csv(file)
        for column in data.columns:
            data[column].fillna(method='ffill', inplace=True)  # Forward fill for time series
            if column != 'Date':
                data[column].fillna(data[column].mean(), inplace=True)  # Mean imputation
        data.to_csv(file, index=False)

# Function to get current exchange rates using API
def get_all_exchange_rates(base):
    url = f'https://v6.exchangerate-api.com/v6/09faa75a35afe0628483bae9/latest/{base}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'conversion_rates' in data:
            return data['conversion_rates']
        else:
            print("Error: 'conversion_rates' key not found in the response.")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {}

def get_current_exchange_rate(base, target):
    rates = get_all_exchange_rates(base)
    return rates.get(target, None)

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

# Function to load and merge currency data from multiple CSVs (for yearly data)
def load_and_merge_currency_data(directory):
    all_data = []
    files = glob.glob(f"{directory}/*.csv")
    
    for file in files:
        year = os.path.basename(file).split('_')[-1].split('.')[0]
        data = pd.read_csv(file)
        
        # Ensure proper date parsing
        try:
            data['Date'] = pd.to_datetime(data['Date'], format='%d-%b-%y')  # Assuming format like '3-Jan-12'
        except Exception as e:
            print(f"Error parsing date in file {file}: {e}")
            continue  # Skip files with date errors
        
        data['Year'] = year  # Add year column
        all_data.append(data)
    
    merged_data = pd.concat(all_data, ignore_index=True)
    return merged_data


# Function to plot currency data
def plot_currency_data(data, currency_from, currency_to, time_frame):
    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' column is datetime
    data.set_index('Date', inplace=True)

    if time_frame == "Daily":
        resampled_data = data[[currency_from, currency_to]]
    elif time_frame == "Weekly":
        resampled_data = data[[currency_from, currency_to]].resample('W').mean()
    elif time_frame == "Monthly":
        resampled_data = data[[currency_from, currency_to]].resample('M').mean()
    elif time_frame == "Quarterly":
        resampled_data = data[[currency_from, currency_to]].resample('Q').mean()
    elif time_frame == "Yearly":
        resampled_data = data[[currency_from, currency_to]].resample('Y').mean()

    st.line_chart(resampled_data)

# Function to calculate volatility with better error handling
def calculate_volatility(data, currency_from, currency_to, time_frame):
    # Check if 'Date' exists in the data
    if 'Date' not in data.columns:
        st.warning("The data does not contain a 'Date' column.")
        return None

    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' column is datetime
    data.set_index('Date', inplace=True)

    if time_frame == "Daily":
        returns = data[[currency_from, currency_to]].pct_change()
    elif time_frame == "Weekly":
        returns = data[[currency_from, currency_to]].resample('W').ffill().pct_change()
    elif time_frame == "Monthly":
        returns = data[[currency_from, currency_to]].resample('M').ffill().pct_change()

    if returns.empty:
        st.warning(f"No data available for the selected time frame: {time_frame}")
        return None

    # Calculate volatility (standard deviation of returns)
    volatility = returns.std() * 100  # Annualize if needed, here we keep it simple
    return volatility

# Configure Streamlit interface
st.set_page_config(page_title="Currency Exchange Tracker", layout="wide")

# Preprocess CSV data
data_directory = r"C:\Users\Asus\Desktop\mitwpu-team_4-currency_exchange\conversion_rates"
preprocess_currency_data(data_directory)

# Merge data across multiple years
merged_data = load_and_merge_currency_data(data_directory)

st.markdown("<h1 style='text-align: center; color: #003366; background-color: #E6F2FF; padding: 20px; border-radius: 10px;'>Currency Exchange Tracker</h1>", unsafe_allow_html=True)

# Sidebar for user inputs
with st.sidebar:
    st.header("Currency Selection")
    available_currencies = merged_data.columns[1:-1]  # Exclude 'Date' and 'Year'

    currency_from = st.selectbox('From Currency:', available_currencies)
    currency_to = st.selectbox('To Currency:', available_currencies)
    selected_year = st.selectbox('Year of Data:', ['All Years'] + [str(year) for year in merged_data['Year'].unique()])

# Filter data based on year selection
if selected_year != 'All Years':
    selected_data = merged_data[merged_data['Year'] == selected_year]
else:
    selected_data = merged_data

# Add month range selection only if a particular year is chosen
if selected_year != 'All Years':
    st.header("Select Date Range")

    # Extract available months in the selected data
    min_date = selected_data['Date'].min()
    max_date = selected_data['Date'].max()

    # Extract the month names for the slider
    available_months = pd.date_range(start=min_date, end=max_date, freq='M').strftime('%B').tolist()

    start_month, end_month = st.select_slider(
        'Select Month Range:',
        options=available_months,
        value=(available_months[0], available_months[-1])  # Default to first and last months
    )

    # Convert month names back to datetime for filtering
    start_date = pd.to_datetime(f"{selected_year} {start_month} 01")
    end_date = pd.to_datetime(f"{selected_year} {end_month} 01") + pd.offsets.MonthEnd()

    # Filter data within the selected range
    selected_data = selected_data[(selected_data['Date'] >= start_date) & (selected_data['Date'] <= end_date)]

# Exchange rate calculation display
if 'Date' in selected_data.columns and currency_from in selected_data.columns and currency_to in selected_data.columns:
    current_exchange = (selected_data[currency_to].iloc[-1] / selected_data[currency_from].iloc[-1]) if not selected_data[currency_from].isna().all() else None
else:
    current_exchange = None

if current_exchange is not None:
    st.markdown(f"**Current Exchange Rate:** 1 {currency_from} = {current_exchange:.4f} {currency_to}")
else:
    st.markdown("Exchange rate information is not available.")

# Custom Currency Basket Feature
st.header("Create Your Custom Currency Basket")
basket_selection = st.multiselect("Choose Currencies for Your Basket", available_currencies, default=[available_currencies[0]])
basket_weights = {currency: st.number_input(f"Weight for {currency} (%)", min_value=0.0, max_value=100.0, value=20.0) for currency in basket_selection}

if st.button("Calculate Basket Value"):
    basket_total_value = compute_basket_value({curr: weight / 100 for curr, weight in basket_weights.items()}, currency_from)
    st.success(f"Total Value of Your Basket in {currency_from}: {basket_total_value:.2f}" if basket_total_value > 0 else "Total value is 0. Check weights or rates.")

# Time frame options adjustment based on year selection
st.header("Graph Visualization")

if selected_year == 'All Years':
    time_frame_options = ["Yearly"]
else:
    time_frame_options = ["Daily", "Weekly", "Monthly", "Quarterly"]

time_frame = st.radio("Select Time Frame for Chart Display", time_frame_options)

if time_frame:
    plot_currency_data(selected_data, currency_from, currency_to, time_frame)

# Sidebar for volatility selection
st.sidebar.header("Volatility Analysis")
vol_currency_from = st.sidebar.selectbox('Select From Currency for Volatility:', available_currencies)
vol_currency_to = st.sidebar.selectbox('Select To Currency for Volatility:', available_currencies)
vol_time_frame = st.sidebar.selectbox('Select Time Frame for Volatility:', ["Daily", "Weekly", "Monthly"])

if st.sidebar.button("Calculate Volatility"):
    volatility = calculate_volatility(selected_data, vol_currency_from, vol_currency_to, vol_time_frame)
    if volatility is not None and vol_currency_to in volatility:
        st.success(f"Volatility of {vol_currency_from} to {vol_currency_to} over the selected period: {volatility[vol_currency_to]:.2f}%")
    else:
        st.warning(f"Volatility data for {vol_currency_to} is not available.")

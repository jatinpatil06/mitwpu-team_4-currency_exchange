import pandas as pd
import streamlit as st

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

# Function to calculate volatility
def calculate_volatility(data, currency_from, currency_to):
    if 'Date' not in data.columns:
        st.warning("The data does not contain a 'Date' column.")
        return None

    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' column is datetime
    data.set_index('Date', inplace=True)

    # Calculate returns
    returns = data[[currency_from, currency_to]].pct_change()

    # Calculate volatility as the standard deviation of returns for the currency_to
    volatility = returns[currency_to].std() * 100  # Multiply by 100 for percentage

    return volatility


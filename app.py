import os
import glob
import pandas as pd
import streamlit as st
from data_preprocessing import preprocess_currency_data, load_and_merge_currency_data
from exchange_rates import get_current_exchange_rate, compute_basket_value
from visualization import plot_currency_data, calculate_volatility

# Configure Streamlit interface
st.set_page_config(page_title="Currency Exchange Tracker", layout="wide")

# Preprocess and load data
data_directory = r"C:\Users\Asus\Desktop\mitwpu-team_4-currency_exchange\conversion_rates"
preprocess_currency_data(data_directory)
merged_data = load_and_merge_currency_data(data_directory)

st.markdown("<h1 style='text-align: center; color: #003366; background-color: #E6F2FF; padding: 20px; border-radius: 10px;'>Currency Exchange Tracker</h1>", unsafe_allow_html=True)

# Define available currencies once after loading data
available_currencies = merged_data.columns[1:-1]

# Create tabs for different analyses
tabs = st.tabs(["Analysis and Graph Visualization", "Volatility Analysis", "Basket Analysis"])

# Analysis and Graph Visualization Tab
with tabs[0]:
    st.header("Currency Selection")
    currency_from = st.selectbox('From Currency:', available_currencies)
    currency_to = st.selectbox('To Currency:', available_currencies)
    selected_year = st.selectbox('Year of Data:', ['All Years'] + [str(year) for year in merged_data['Year'].unique()])

    # Filter data based on year selection
    if selected_year != 'All Years':
        selected_data = merged_data[merged_data['Year'] == selected_year]
    else:
        selected_data = merged_data

    # Date range selection for Currency Converter
    st.subheader("Currency Converter")
    
    # Get the min and max date from the selected data
    min_date = selected_data['Date'].min()
    max_date = selected_data['Date'].max()
    
    # Allow user to select date range
    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End Date", min_value=start_date, max_value=max_date, value=max_date)

    # Current Exchange Calculation within the selected date range
    current_exchange = (
        selected_data.loc[(selected_data['Date'] >= pd.to_datetime(start_date)) & (selected_data['Date'] <= pd.to_datetime(end_date)), currency_to].iloc[-1] /
        selected_data.loc[(selected_data['Date'] >= pd.to_datetime(start_date)) & (selected_data['Date'] <= pd.to_datetime(end_date)), currency_from].iloc[-1]
        if not selected_data[currency_from].isna().all() else None
    )

    if current_exchange is not None:
        st.markdown(f"**Current Exchange Rate from {start_date} to {end_date}:** 1 {currency_from} = {current_exchange:.4f} {currency_to}")
    else:
        st.markdown("Exchange rate information is not available.")

    # Graph Visualization Section
    st.subheader("Graph Visualization")
    time_frame_options = ["Daily", "Weekly", "Monthly", "Quarterly"] if selected_year != 'All Years' else ["Yearly"]
    time_frame = st.radio("Select Time Frame for Chart Display", time_frame_options)

    if time_frame:
        plot_currency_data(selected_data[(selected_data['Date'] >= pd.to_datetime(start_date)) & (selected_data['Date'] <= pd.to_datetime(end_date))], currency_from, currency_to, time_frame)


   # Volatility Analysis Tab
# Volatility Analysis Tab

with tabs[1]:
    st.header("Volatility Analysis")
    
    # Currency selection for volatility analysis
    vol_currency_from = st.selectbox('Select From Currency for Volatility:', available_currencies)
    vol_currency_to = st.selectbox('Select To Currency for Volatility:', available_currencies)

    # Start and End Date for Volatility Calculation
    start_date_vol = st.date_input("Start Date", min_value=merged_data['Date'].min(), max_value=merged_data['Date'].max(), value=merged_data['Date'].min(), key="start_date_vol")
    end_date_vol = st.date_input("End Date", min_value=start_date_vol, max_value=merged_data['Date'].max(), value=merged_data['Date'].max(), key="end_date_vol")

    if st.button("Calculate Volatility"):
        # Filter data based on the selected date range
        filtered_data = merged_data[(merged_data['Date'] >= pd.to_datetime(start_date_vol)) & (merged_data['Date'] <= pd.to_datetime(end_date_vol))]

        # Ensure we have enough data to calculate volatility
        if filtered_data.empty:
            st.warning("No data available for the selected date range. Please adjust your dates.")
        else:
            # Calculate volatility
            volatility = calculate_volatility(filtered_data, vol_currency_from, vol_currency_to)

            if volatility is not None:
                st.success(f"Volatility of {vol_currency_from} to {vol_currency_to} from {start_date_vol} to {end_date_vol}: {volatility:f}%")
            else:
                st.warning(f"Volatility data for {vol_currency_to} is not available.")





# Basket Analysis Tab
with tabs[2]:
    st.header("Create Your Custom Currency Basket")
    basket_selection = st.multiselect("Choose Currencies for Your Basket", available_currencies, default=[available_currencies[0]])
    basket_weights = {currency: st.number_input(f"Weight for {currency} (%)", min_value=0.0, max_value=100.0, value=20.0) for currency in basket_selection}

    if sum(basket_weights.values()) != 100:
        st.warning("The total weight of all currencies should equal 100%. Please adjust the weights.")
    else:
        if st.button("Calculate Basket Value"):
            basket_total_value = compute_basket_value({curr: weight / 100 for curr, weight in basket_weights.items()}, currency_from)
            st.success(f"Total Value of Your Basket in {currency_from}: {basket_total_value:.2f}" if basket_total_value > 0 else "Total value is 0. Check weights or rates.")

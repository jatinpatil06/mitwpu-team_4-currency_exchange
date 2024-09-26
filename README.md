# mitwpu-team_4-currency_exchange

# Currency Exchange Tracker

## Overview

Currency Exchange Tracker is a Streamlit-based web application that allows users to analyze and visualize currency exchange rates, calculate volatility, and create custom currency baskets. This tool provides insights into currency trends and helps users make informed decisions about foreign exchange.

## Features

- **Currency Exchange Rate Analysis**: View and compare exchange rates between different currencies.
- **Interactive Visualizations**: Analyze currency trends with customizable time frames (daily, weekly, monthly, quarterly, yearly).
- **Volatility Analysis**: Calculate and display the volatility between selected currency pairs.
- **Custom Currency Basket**: Create and analyze a personalized basket of currencies with user-defined weights.
- **Date Range Selection**: Filter data and perform analyses within specific date ranges.

## Setup and Installation

### Prerequisites

- Python 3.7+
- pip

### Installation Steps

1. Clone the repository:

   ```
   git clone https://github.com/your-username/currency-exchange-tracker.git
   cd currency-exchange-tracker
   ```

2. Install required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up your Exchange Rate API key:

   - Sign up for a free API key at [ExchangeRate-API](https://www.exchangerate-api.com/)
   - Set the API key as an environment variable:
     ```
     export EXCHANGE_RATE_API_KEY='your_api_key_here'
     ```

4. Prepare your data:

   - Place your currency exchange rate CSV files in the `conversion_rates` directory.
   - Ensure your CSV files are named appropriately (e.g., `conversion_rates_2022.csv`).

5. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Usage

1. Select currencies for comparison in the "Analysis and Graph Visualization" tab.
2. Choose a date range and time frame for analysis.
3. Use the "Volatility Analysis" tab to calculate currency pair volatility.
4. Create a custom currency basket in the "Basket Analysis" tab.

## File Structure

- `app.py`: Main Streamlit application file
- `data_preprocessing.py`: Functions for data preprocessing and loading
- `exchange_rates.py`: Functions for fetching current exchange rates and basket calculations
- `visualization.py`: Functions for data visualization and volatility calculations
- `conversion_rates/`: Directory containing historical exchange rate data (CSV files)

## Contributing

Contributions to the Currency Exchange Tracker project are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Exchange rate data provided by [ExchangeRate-API](https://www.exchangerate-api.com/)
- Built with [Streamlit](https://streamlit.io/)

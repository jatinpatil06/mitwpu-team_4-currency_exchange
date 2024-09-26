import os
import requests

# Function to get current exchange rates using API
def get_all_exchange_rates(base):
    api_key = os.environ.get('EXCHANGE_RATE_API_KEY', '09faa75a35afe0628483bae9')
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'conversion_rates' in data:
            return data['conversion_rates']
        else:
            print(f"Error: 'conversion_rates' key not found in the response. Full response: {data}")
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
            print(f"Rate for {currency} could not be retrieved.")  # Consider using st.warning here for Streamlit
    return total_value

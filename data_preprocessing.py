import pandas as pd
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

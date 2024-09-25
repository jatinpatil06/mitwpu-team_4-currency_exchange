#importing the required libraries
import pandas as pd
import numpy as np
import mysql.connector
import re

df_old = pd.read_csv(r'conversion_rates\Exchange_Rate_Report_2022.csv')
new_cols = []
for x in list(df_old.columns):
    new_cols.append(x.strip())

# List to hold extracted currency codes
currency_codes = ['Date']

# Regex pattern to extract the currency code
pattern = r'\((\w{3})\)'

# Loop through each country name and extract the code
for country in new_cols:
    match = re.search(pattern, country)
    if match:
        currency_code = match.group(1)
        currency_codes.append(currency_code)

#reading the dataframe again, to modify it now
df = pd.read_csv(r'conversion_rates\Exchange_Rate_Report_2022.csv', names=currency_codes, header=0)
df = df.replace({np.nan: None})
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y').dt.strftime('%Y-%m-%d')

# Connect to MySQL Database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)

cursor = connection.cursor()
database_name = 'currency_data22'
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
cursor.execute(f"USE {database_name}")
cursor.close()
# Create the table with the appropriate schema
table_creation = "CREATE TABLE IF NOT EXISTS currency_rates22 ( Date DATE"
for x in currency_codes[1:]:
    table_creation += f", {x} DECIMAL(10,4)"
table_creation += ");"
cursor = connection.cursor()
cursor.execute(table_creation)
cursor.close()

insertion_format = "INSERT INTO currency_rates22 (Date "
for x in currency_codes[1:]:
    insertion_format += f", {x}"
insertion_format += ") VALUES"

for idx, row in df.iterrows():
    #print(row.values)
    toInsert = "" + insertion_format + "(" + f"\"{str(row.values[0])}\""
    for field in row.values[1:]:
        if field is None:
            toInsert += f", NULL"
        else:
            toInsert += f", {field}"
    toInsert += ");"
    cursor = connection.cursor()
    cursor.execute(toInsert)
    connection.commit()
    cursor.close()
connection.close()
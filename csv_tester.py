
import pandas as pd

df = pd.read_csv('pest_monitoring.csv', parse_dates=['timestamp'])

print(df.shape)           # (rows, columns)
print(df.dtypes)          # column types
print(df.site_id.unique()) # site names
print(df.head())          # first few rows

# Check the status distribution
print(df.status.value_counts())

# Check for missing data
print(df.isnull().sum())

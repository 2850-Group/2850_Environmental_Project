import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("pest_monitoring.csv", parse_dates=["timestamp"])
df["month"] = df.timestamp.dt.month
df["wet_season"] = df.month.isin([11, 12, 1, 2, 3])

print(df.shape)  # (rows, columns)
print(df.dtypes)  # column types
print(df.site_id.unique())  # site names
print(df.head())  # first few rows

# Check the status distribution
print(df.status.value_counts())

# Check for missing data
print(df.isnull().sum())


# Pest counts by season
seasonal = df.groupby(["site_id", "wet_season"]),["pest_trap_count"].mean().unstack()
seasonal.columns = ["Dry season", "Wet season"]
seasonal.plot(kind="bar", title="Mean trap count by season")
plt.show()

# Leaf wetness vs humidity
maize = df[df.site_id == "site_maize"]
maize.plot.scatter(
    x="relative_humidity_pct",
    y="leaf_wetness_0_1",
    alpha=0.1,
    title="Leaf wetness vs humidity",
)
plt.show()

# Disease high events
dh = df[df.alert_disease_high == 1]
print(f"Disease high alerts: {len(dh)} rows ({100*len(dh)/len(df):.1f}%)")
print(f"Mean leaf wetness during disease_high: {dh.leaf_wetness_0_1.mean():.3f}")
print(
    f"Mean leaf wetness otherwise:           {df[df.alert_disease_high==0].leaf_wetness_0_1.mean():.3f}"
)

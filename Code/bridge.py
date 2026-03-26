"""
Plan:
- Run the timer function to increment time every 15 minutes
- When timer function updates time:
    - fetch row from the database and send new stats to dashboard
    - seperate row into statistical data and alerts
    - create new average to include the new data - average over last 2 weeks for now but potential to be set by user in app
    - flags to indicate whether the data is greater than or less than average so dashboard arrows can be changed
    - alert types just as variables
    - flag for critical, warning and normal
    - then automated test it all!!!!
"""

from get_row_based_on_date import *
from calculate_average_for_x_days import *
from initialsie_database import *

new_data = timer(conn, cursor)
maize = new_data[0]
brassica = new_data[1]
orchard = new_data[2]

maize_stats = []
brassica_stats = []
orchard_stats = []
for i in range(3, 8):
    maize_stats.append(maize[i])
    brassica_stats.append(brassica[i])
    orchard_stats.append(orchard[i])
maize_stats.append(maize[15])
brassica_stats.append(brassica[15])
orchard_stats.append(orchard[15])

maize_alerts = []
brassica_alerts = []
orchard_alerts = []
for i in range(9, 14):
    maize_alerts.append(maize[i])
    brassica_alerts.append(brassica[i])
    orchard_alerts.append(orchard[i])



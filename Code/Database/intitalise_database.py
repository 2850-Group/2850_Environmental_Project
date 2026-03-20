import csv
import sqlite3

connection = sqlite3.connect('pest_control.db')

cursor = connection.cursor()

# This is used to check if the table already exists
listOfTables = cursor.execute(
    ''' SELECT name from sqlite_master WHERE type = 'table' AND name = 'pest_monitoring'; ''').fetchall()

# All the fields ready to be executed to create the table
create_table_pest = '''CREATE TABLE pest_monitoring(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time datetime NOT NULL,
                site_id varchar NOT NULL,
                air_temperature_c float NOT NULL,
                relative_humidity_pct float NOT NULL,
                leaf_wetness_0_1 float NOT NULL,
                light_lux float NOT NULL,
                vibration_level float NOT NULL,
                pest_trap_count integer NOT NULL,
                status varchar NOT NULL,
                alert_triggered integer NOT NULL,
                alert_pest_action integer NOT NULL,
                alert_pest_outbreak integer NOT NULL,
                alert_disease_moderate integer NOT NULL,
                alert_disease_high integer NOT NULL,
                wx_rain_mm_hr float NOT NULL);
                '''

create_table_user = '''CREATE TABLE user(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username varchar NOT NULL,
                password_hash varchar NOT NULL,
                role varchar NOT NULL);
                '''


# If there is no tables then create the new table
if listOfTables == []:
    cursor.execute(create_table_pest)
    cursor.execute(create_table_user)

# If the pest_monitoring table already exists then delete it and create a new one
else:
    connection.execute("DROP TABLE pest_monitoring")
    connection.execute("DROP TABLE user")
    cursor.execute(create_table_pest)
    cursor.execute(create_table_user)


file = open('pest_monitoring.csv')

contents = csv.reader(file)

insert_records = "INSERT INTO pest_monitoring (time, site_id, air_temperature_c, relative_humidity_pct, leaf_wetness_0_1, light_lux, vibration_level, pest_trap_count, status, alert_triggered, alert_pest_action, alert_pest_outbreak, alert_disease_moderate, alert_disease_high, wx_rain_mm_hr) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

# Inserts all of the records into the table
cursor.executemany(insert_records, contents)

connection.commit()
connection.close()

# I have left the blank spaces in the table at the minute
# By running the 'csv_tester' you can see the number of blank cells
# A blank cell just contains nothing and using the 'database_test.py' you can find these cells
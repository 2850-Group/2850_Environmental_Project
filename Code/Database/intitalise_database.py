import csv
import sqlite3

connection = sqlite3.connect('pest_control.db')

cursor = connection.cursor()

listOfTables = cursor.execute(
    ''' SELECT name from sqlite_master WHERE type = 'table' AND name = 'pest_monitoring'; ''').fetchall()

create_table = '''CREATE TABLE pest_monitoring(
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

print(listOfTables)
if listOfTables == []:
    cursor.execute(create_table)
else:
    connection.execute("DROP TABLE pest_monitoring")
    cursor.execute(create_table)


file = open('pest_monitoring.csv')

contents = csv.reader(file)

insert_records = "INSERT INTO pest_monitoring (time, site_id, air_temperature_c, relative_humidity_pct, leaf_wetness_0_1, light_lux, vibration_level, pest_trap_count, status, alert_triggered, alert_pest_action, alert_pest_outbreak, alert_disease_moderate, alert_disease_high, wx_rain_mm_hr) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

cursor.executemany(insert_records, contents)


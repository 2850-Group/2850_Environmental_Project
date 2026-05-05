import sqlite3

connection = sqlite3.connect("pest_control.db")

cursor = connection.cursor()

# cursor.execute("SELECT id FROM pest_monitoring
# WHERE air_temperature_c = '' ")

# cursor.execute("SELECT * FROM pest_monitoring")

cursor.execute("INSERT INTO user VALUES ('1', 'ash', 'hello', 'admin' ) ")
cursor.execute("SELECT * FROM user")

output = cursor.fetchone()
print(output)

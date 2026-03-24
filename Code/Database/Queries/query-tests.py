from calculate_average_for_x_days import *
from get_row_based_on_date import *
import datetime

#Connecting to the database to operate queries on
connection = sqlite3.connect('pest_control.db')
cursor = connection.cursor()

#TEST: row_by_timestamp(conn, cursor, timestamp)

#Test 1: Correct row returned correlating to specified date.
#Input: conn=connection, cursor=cursor, timestamp=2022-01-01 00:00:00
#Expected Output: All rows with timestamp 2022-01-01 00:00:00. Length of list should be 3.
date = datetime.datetime(2022, 1, 1, 0, 0, 0)
rows = row_by_timestamp(connection, cursor, date)
print(rows)
print(len(rows))
#Output 1: None no such table: pest_monitory
    #Fixed: table name was wrong in function. changed to pest_monitoring
#Ouput 2: None no such column: timestamp
    #Fixed: column name was not timestamp. changed to time.
#Output 3: [] None
    #Fixed: try and except statement did not work. So removed.
#Output 4: [(2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9, 'warning', 1, 1, 0, 0, 0, 0.5), (70079, '2022-01-01 00:00:00', 'site_brassica', 14.08, 97.0, 0.951, 5.0, 0.287, 1, 'normal', 0, 0, 0, 0, 0, 0.5), (140156, '2022-01-01 00:00:00', 'site_orchard', 15.15, 98.3, 0.943, 2.0, 0.066, 5, 'warning', 1, 1, 0, 1, 0, 0.5)]
#          3
#Test Passed

#Test 2: No row returned as there are no correlating to specified date.
#Input: conn=connection, cursor=cursor, timestamp=2022-01-01 00:00:06
#Expected Output: Empty array returned. Length 0.
date = datetime.datetime(2022, 1, 1, 0, 0, 6)
rows = row_by_timestamp(connection, cursor, date)
print(rows, len(rows))
#Output: [], 0
#Test Passed

#TEST: data_between_times()

#Test 1: All rows between two timestamps returned. Upper and Lower Boundary test.
#Input: conn=connection, cursor=cursor, start_timestamp=2022-01-01 00:00:00, end_timestamp=2022-01-01-01 00:15:00
#Expected Output: All records between the two timestamps returned. List length should be 6.
start_date = datetime.datetime(2022, 1, 1, 0, 0, 0)
end_date = datetime.datetime(2022, 1, 1, 0, 15, 0)
rows = data_between_times(connection, cursor, start_date, end_date)
print(rows, len(rows))
#Output 1: Error binding parameter 1: type 'tuple' is not supported
    #Fixed: Changed brackets as there was one set making start and end timestamp into a tuple.
#Output 2: ([], None) 2
    #Fixed: Removed try, except statement.
#Output 3: [] 0
    #Fixed: Had to change <, > into <= and >=.
#Output 4: [(2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9, 'warning', 1, 1, 0, 0, 0, 0.5), (3, '2022-01-01 00:15:00', 'site_maize', 14.59, 99.3, 0.915, 4.0, 0.062, 0, 'normal', 0, 0, 0, 0, 0, 0.485), (70079, '2022-01-01 00:00:00', 'site_brassica', 14.08, 97.0, 0.951, 5.0, 0.287, 1, 'normal', 0, 0, 0, 0, 0, 0.5), (70080, '2022-01-01 00:15:00', 'site_brassica', 15.46, 100.0, 0.862, 2.0, 0.491, 0, 'warning', 1, 0, 0, 1, 0, 0.485), (140156, '2022-01-01 00:00:00', 'site_orchard', 15.15, 98.3, 0.943, 2.0, 0.066, 5, 'warning', 1, 1, 0, 1, 0, 0.5), (140157, '2022-01-01 00:15:00', 'site_orchard', 13.48, 99.8, 0.839, 1.0, 0.156, 3, 'normal', 0, 0, 0, 0, 0, 0.485)]
#           6
#Test passed.

#Test 2: All rows between two timestamps returned. Boundary test.
#Input: conn=connection, cursor=cursor, start_timestamp=2022-01-01 00:00:01, end_timestamp=2022-01-01 00:16:00
#Expected Output: All records between the two timestamps returned. List length should be 3.
start_date = datetime.datetime(2022, 1, 1, 0, 0, 1)
end_date = datetime.datetime(2022, 1, 1, 0, 16, 0)
rows = data_between_times(connection, cursor, start_date, end_date)
print(rows, len(rows))
#Output: [(3, '2022-01-01 00:15:00', 'site_maize', 14.59, 99.3, 0.915, 4.0, 0.062, 0, 'normal', 0, 0, 0, 0, 0, 0.485), (70080, '2022-01-01 00:15:00', 'site_brassica', 15.46, 100.0, 0.862, 2.0, 0.491, 0, 'warning', 1, 0, 0, 1, 0, 0.485), (140157, '2022-01-01 00:15:00', 'site_orchard', 13.48, 99.8, 0.839, 1.0, 0.156, 3, 'normal', 0, 0, 0, 0, 0, 0.485)]
#        3
#Test passed.

#Test 3: No rows returned when timnestamps do not reference any entities.
#Input: conn=connection, cursor=cursor, start_timestamp=2022-01-01 00:00:01, end_timestamp=2022-01-01 00:14:00
#Expected Output: Empty list returned. List length should be 0.
start_date = datetime.datetime(2022, 1, 1, 0, 0, 1)
end_date = datetime.datetime(2022, 1, 1, 0, 14, 0)
rows = data_between_times(connection, cursor, start_date, end_date)
print(rows, len(rows))
#Output: [] 0
#Test passed.


#TEST: data_over_x_days()

#Test 1: All rows x days before the start date should be returned. Upper and Lower Boundary test.
#Input: conn=connection, cursor=cursor, start_timestamp=2022-01-01 00:00:00, days=1.
#Expected Output: All records x days before the start timestamp. List length should be 96.
start_date = datetime.datetime(2022, 1, 1, 0, 0, 1)
days = 1
rows = data_over_x_days(connection, cursor, start_date, days)
print(rows, len(rows))
#Output 1: list, error = rows_by_x_days(conn, cursor, start, end). ValueError: not enough values to unpack (expected 2, got 0)
    #Fixed: return statement changed in rows_by_x_days due to earlier tests so needed to be updated in data_over_x_days
#Output 2: [] 0


#TEST: remove_record_null()

#TEST: average_data_all_rows()
from calculate_average_for_x_days import *
from get_row_based_on_date import *
import datetime
import sqlite3
import unittest

#Connecting to the database to operate queries on
connection = sqlite3.connect('pest_control.db')
cursor = connection.cursor()

class testGetRowBasedOnDate(unittest.TestCase):
    def test_year_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timestamp = datetime.datetime(2021,10,12,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # out of upper bound
            timestamp = datetime.datetime(2024,10,12,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)

    def test_month_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timestamp = datetime.datetime(2022,13,12,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # out of upper bound
            timestamp = datetime.datetime(2022,-1,12,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)
    
    def test_day_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timestamp = datetime.datetime(2022,10,32,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # out of upper bound
            timestamp = datetime.datetime(2022,10,-1,12,15,0)
            row_by_timestamp(connection,cursor,timestamp)

    def test_hour_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timestamp = datetime.datetime(2022,10,12,25,15,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # out of upper bound
            timestamp = datetime.datetime(2022,10,12,-1,15,0)
            row_by_timestamp(connection,cursor,timestamp)

    def test_minute_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timestamp = datetime.datetime(2022,10,12,12,61,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # out of upper bound
            timestamp = datetime.datetime(2022,10,12,12,-1,0)
            row_by_timestamp(connection,cursor,timestamp)
        with self.assertRaises(ValueError):
            # not divisible by 15
            timestamp = datetime.datetime(2022,10,12,12,16,0)
            row_by_timestamp(connection,cursor,timestamp)
    
    def test_returns_correct_data(self):
        # returns the correct rows from the database
        timestamp = datetime.datetime(2022,1,1,0,0,0)
        result = row_by_timestamp(connection,cursor,timestamp)

        self.assertEqual(result,[(2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9, 'warning', 1, 1, 0, 0, 0, 0.5),
                                (70079, '2022-01-01 00:00:00', 'site_brassica', 14.08, 97.0, 0.951, 5.0, 0.287, 1, 'normal', 0, 0, 0, 0, 0, 0.5),
                                (140156, '2022-01-01 00:00:00', 'site_orchard', 15.15, 98.3, 0.943, 2.0, 0.066, 5, 'warning', 1, 1, 0, 1, 0, 0.5)])




class testDataBetweenTimes(unittest.TestCase):

    def test_two_valid_timestamps(self):

        start_date = datetime.datetime(2022, 1, 1, 0, 0, 0)
        end_date = datetime.datetime(2022, 1, 1, 0, 15, 0)
        rows = data_between_times(connection, cursor, start_date, end_date)
        
        self.assertEqual(rows, [(2, '2022-01-01 00:00:00', 'site_maize', 14.83, 97.1, 0.872, 1.0, 0.397, 9,'warning', 1, 1, 0, 0, 0, 0.5), 
                                (3, '2022-01-01 00:15:00', 'site_maize', 14.59, 99.3, 0.915, 4.0, 0.062, 0, 'normal', 0, 0, 0, 0, 0, 0.485), 
                                (70079, '2022-01-01 00:00:00', 'site_brassica', 14.08, 97.0, 0.951, 5.0, 0.287, 1, 'normal', 0, 0, 0, 0, 0, 0.5), 
                                (70080, '2022-01-01 00:15:00', 'site_brassica', 15.46, 100.0, 0.862, 2.0, 0.491, 0, 'warning', 1, 0, 0, 1, 0, 0.485), 
                                (140156, '2022-01-01 00:00:00', 'site_orchard', 15.15, 98.3, 0.943, 2.0, 0.066, 5, 'warning', 1, 1, 0, 1, 0, 0.5), 
                                (140157, '2022-01-01 00:15:00', 'site_orchard', 13.48, 99.8, 0.839, 1.0, 0.156, 3, 'normal', 0, 0, 0, 0, 0, 0.485)])
        self.assertEqual(len(rows),6)
    
    def test_one_valid_timestamp(self):
        







class testTimerFunction(unittest.TestCase):
    def test_year_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timer(connection,cursor,2021,10,20,13,15)
        with self.assertRaises(ValueError):
            # out of upper bound
            timer(connection,cursor,2024,10,20,13,15)

    def test_month_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timer(connection,cursor,2022,13,20,13,15)
        with self.assertRaises(ValueError):
            # out of upper bound
            timer(connection,cursor,2022,-1,20,13,15)

    def test_day_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timer(connection,cursor,2022,10,32,13,15)
        with self.assertRaises(ValueError):
            # out of upper bound
            timer(connection,cursor,2022,10,-1,13,15)

    def test_hour_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timer(connection,cursor,2022,10,20,25,15)
        with self.assertRaises(ValueError):
            # out of upper bound
            timer(connection,cursor,2022,10,20,-1,15)

    def test_minute_range(self):
        with self.assertRaises(ValueError):
            # out of lower bound
            timer(connection,cursor,2022,10,20,13,62)
        with self.assertRaises(ValueError):
            # out of upper bound
            timer(connection,cursor,2022,10,20,13,-1)
        with self.assertRaises(ValueError):
            # not divisible by 15
            timer(connection,cursor,2022,10,20,13,16)

    '''
     get_row_based_on_date() has already been tested so I do not need to test
     it again. 
    '''



if __name__ == '__main__':
    unittest.main()
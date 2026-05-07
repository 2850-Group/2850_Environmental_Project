"""
Testing: Dashboard

We have chosen to use a mix of integrated and scripted testing for the dashbaord because of the UI demonstration.

"""
from Dashboard import *
import unittest
from unittest.mock import MagicMock
"""
SignUp Testing
"""
class SignUpTest() :

    def make_screen(self, name="Jane Doe", username="janeD", password="12345678"):
        screen = MagicMock()
        screen.fullname.text = name
        screen.username.text = username
        screen.password.text = password
        screen._error = MagicMock()
        return screen
    
    #TEST 1: User leaves both username and password fields empty.
    def test_1(self):
        screen = self.make_screen(username="", password="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 2: User leaves password field empty.
    def test_2(self):
        screen = self.make_screen(password="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 3: User leaves username field empty.
    def test_3(self):
        screen = self.make_screen(name="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")
    
    #TEST 4: User leaves name field empty.
    def test_4(self):
        screen = self.make_screen(name="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 5: User uses a username already in the database.
    def test_5(self):
        screen = self.make_screen(username="holly")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("Username is taken. Please choose another.")

    #TEST 6: User uses password less than 8 characters.
    def test_6(self):
        screen = self.make_screen(password="1234")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("Password must be at least 8 characters")

    #TEST 7: User uses a unique username and a valid password.
    def test_7(self):
        screen = self.make_screen(username="BobM", name="Bob Muncan", password="12345678")
        screen._on_sign_up()
        #???


"""
LogIn Testing
"""
#TEST 1: User leaves both username and password fields empty.

#TEST 2: User leaves password field empty.

#TEST 3: User leaves username field empty.

#TEST 4: User uses a username with an incorrect passowrd.

#TEST 5: User uses a unique username and a valid password.

#TEST 6: User attempts to log in 10 times.

"""
Dashboard Testing
"""
#TEST 1: Arrows - green, red, neutral

#TEST 2: Alert pop ups

#TEST 3: Graphs - date range, etc

#TEST 4: 

"""
Scanning Page Testing
"""
#TEST 1: Image capture is given a blank photo.

#TEST 2: Image capture is given a healthy tomato leaf

#TEST 3: Image capture is gven an unhealthy tomato leaf

"""
Profile page Testing
"""
#TEST 1: Users full name related to the username is displayed.

#TEST 2: Users role realted to their identity is displayed.

if __name__ == "__main__":
    unittest.main()
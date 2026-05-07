"""
Testing: Dashboard

We have chosen to use a mix of integrated and scripted testing for the dashboard because of the UI demonstration.

"""
import unittest
from unittest.mock import patch, MagicMock

mock_model = MagicMock()
patch('tensorflow.keras.models.load_model', return_value=mock_model).start()



"""
SignUp Testing
"""
from Dashboard import SignUpPanel

class SignUpTest(unittest.TestCase) :

    def make_screen(self, name="Jane Doe", username="janeD", password="12345678"):
        screen = MagicMock()
        screen.fullname.text = name
        screen.username.text = username
        screen.password.text = password
        screen._error = MagicMock()
        screen.success_cb = MagicMock()

        screen._on_sign_up = SignUpPanel._on_sign_up.__get__(screen)
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
        screen = self.make_screen(username="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")
    
    #TEST 4: User leaves name field empty.
    def test_4(self):
        screen = self.make_screen(name="")
        screen._on_sign_up()
        screen._error.show.assert_called_once_with("All fields are required")

    #TEST 5: User uses a username already in the database. Prequisite there must be a user profile with the username already stored in the database.
    def test_5(self):
        screen = self.make_screen(username="i.martin")
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
        with patch('Dashboard.sign_up_query', return_value=True):
            screen._on_sign_up()
        screen.success_cb.assert_called_once()
        screen._error.show.assert_not_called()


"""
LogIn Testing
"""
from Dashboard import SignInPanel 
class SignInTest(unittest.TestCase) :

    def make_screen(self, name="Jane Doe", username="janeD", password="12345678"):
        screen = MagicMock()
        screen.fullname.text = name
        screen.username.text = username
        screen.password.text = password
        screen._error = MagicMock()
        screen.success_cb = MagicMock()

        screen._on_sign_in = SignInPanel._on_sign_in.__get__(screen)
        return screen
    
    #TEST 1: User leaves both username and password fields empty.
    def test_1(self):
        screen = self.make_screen(username="", password="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")

    #TEST 2: User leaves password field empty.
    def test_2(self):
        screen = self.make_screen(password="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")

    #TEST 3: User leaves username field empty.
    def test_3(self):
        screen = self.make_screen(username="")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Please enter your username and password")
    
    #TEST 4: User uses a username with an incorrect passowrd.
    def test_4(self):
        screen = self.make_screen(username="izzy.martin")
        screen = self.make_screen(password="1")
        screen._on_sign_in()
        screen._error.show.assert_called_once_with("Incorrect username or password.")

    #TEST 5: User uses a username and a valid password. Prerequsite, an account must be made with the details username="i.martin" and password="12345678"
    def test_5(self):
        screen = self.make_screen(username="i.martin")
        screen = self.make_screen(password="12345678")
        with patch('Dashboard.sign_in_query', return_value={"username": "i.martin"}):
            screen._on_sign_in()
        screen.success_cb.assert_called_once()
        screen._error.show.assert_not_called()
        


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
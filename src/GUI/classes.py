import sys, time, re
import src.GUI.predict
import src.GUI.app.app
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import psycopg2
import multiprocessing
import yaml

# connect to PostgreSQL database
conn = psycopg2.connect(user="odpcjwissjwjiu",
                                  password="dfd65b18f109b8a176372a90d744432bbdc83ace7702955eef46345cdaa3e4e9",
                                  host="",
                                  port="5432",
                                  database="df7qi7tmkpi4ba") # taken out host server IP
# make a cursor to run commands
cursor = conn.cursor()

def make_table():
    # function to initially create the database
    query = '''CREATE TABLE members
              (id SERIAL PRIMARY KEY,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              email TEXT NOT NULL
              ); '''

    cursor.execute(query)
    conn.commit()

def flaskThread():
    # function to start the backend flask server
    src.GUI.app.app.app.run()

# run the server in a separate thread, otherwise GUI will freeze
thread = multiprocessing.Process(target=flaskThread)
thread.start()

def insert_table(values):
    # registers a new member
    query = '''INSERT INTO members(username, password, email) VALUES(%s, %s, %s); '''

    cursor.execute(query, values)
    conn.commit()


class Main(QWidget):
    # Main GUI window
    def __init__(self, x, y, width=500, height=500, parent=None):
        super().__init__()
        self.x, self.y, self.width, self.height = x, y, width, height
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(self.x, self.y, self.width, self.height)
        self.addWidgets()

    def addWidgets(self):
        self.welcome_label = QLabel("Who Is At My Door?")
        self.welcome_label.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; font-size: 30px; font-weight: 600;}")

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0.273, stop: 0 rgba(85,172,238,1), stop: 1 rgba(79, 165, 240, 1)); border-radius: 20px; color: white; font: bold 18px; min-width: 5em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.register_button.clicked.connect(self.on_register)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 20px; color: white; font: bold 18px; min-width: 5em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.login_button.clicked.connect(self.on_login)


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.welcome_label)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)

    def on_register(self):
        self.register_screen = RegisterScreen(self.x, self.y, self.width, self.height)
        self.close()
        self.register_screen.show()

    def on_login(self):
        with open("settings.yaml") as file:
            doc = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
            if not doc:
                self.login_screen = LoginScreen(self.x, self.y, self.width, self.height)
                self.close()
                self.login_screen.show()
            else:
                self.auto_login = doc["auto_login"][0]
                if self.auto_login:
                    self.username = doc["auto_login"][1]
                    self.password = doc["auto_login"][2]
                    self.email = doc["auto_login"][3]
                    self.valid = LoginScreen.valid_user(self.email, self.username, self.password)
                    if self.valid:
                        self.dashboard = Dashboard(self.password, self.email, self.username, self.x, self.y, self.width, self.height)
                        self.close()
                        self.dashboard.show()
                    else:
                        self.login_screen = LoginScreen(self.x, self.y, self.width, self.height)
                        self.close()
                        self.login_screen.show()
                else:
                    self.login_screen = LoginScreen(self.x, self.y, self.width, self.height)
                    self.close()
                    self.login_screen.show()

class RegisterScreen(QWidget):
    # GUI screen for registering new members
    def __init__(self, x, y, width=500, height=500, parent=None):
        super().__init__()
        self.x, self.y, self.width, self.height = x, y, width, height
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(x, y, width, height)
        self.addWidgets()
        self.email_check = re.compile('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        self.username_check = re.compile('^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$')
        self.strong_password_check = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})')
        self.medium_password_check = re.compile('^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})')

    def addWidgets(self):
        self.error_message = QLabel()
        self.error_message.setStyleSheet("QLabel {color: red; qproperty-alignment: AlignCenter;}")

        self.password_color = QLabel()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-Mail Address")
        self.email.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")
        self.password.setEchoMode(QLineEdit.Password)

        self.submit = QPushButton("Register")
        self.submit.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.submit.clicked.connect(self.register)

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.back_button.clicked.connect(self.back)

        self.layout = QFormLayout()
        self.layout.addWidget(self.error_message)
        self.layout.addWidget(self.password_color)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.email)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.submit)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def is_alpha(self, word):
      try:
        w = word.encode('ascii')
        return True
      except:
        return False

    def register(self):
        self.username_get = self.username.text()
        self.password_get = self.password.text()
        self.email_get = self.email.text()
        self.check = []

        if self.strong_password_check.match(self.password_get):
            self.password_color.setText("Strong password!")
            self.password_color.setStyleSheet("QLabel {color: green; qproperty-alignment: AlignCenter;}")
            self.check.append(True)
        elif self.medium_password_check.match(self.password_get):
            self.password_color.setText("Medium password!")
            self.password_color.setStyleSheet("QLabel {color: orange; qproperty-alignment: AlignCenter;}")
            self.check.append(True)
        else:
            self.password_color.setText("Too weak! Enter a new password.")
            self.password_color.setStyleSheet("QLabel {color: red; qproperty-alignment: AlignCenter;}")
            self.check.append(False)

        if not self.is_alpha(self.password_get) or not self.is_alpha(self.username_get) or not self.is_alpha(self.email_get):
            self.error_message.setText("Please input valid characters!")
            self.check.append(False)
        else:
            self.check.append(True)

        if not self.email_check.match(self.email_get):
            self.error_message.setText("Your E-Mail Address is not valid.")
            self.check.append(False)
        else:
            self.error_message.clear()
            self.check.append(True)

        if not self.username_check.match(self.username_get):
            self.error_message.setText("Your username is not valid!")
            self.check.append(False)
        else:
            self.error_message.clear()
            self.check.append(True)

        if False not in self.check:
            check = []
            command = "SELECT * FROM members WHERE username=%s"
            data = (self.username_get,)
            cursor.execute(command, data)
            rows = cursor.fetchall()
            if len(rows) != 0:
                check.append(rows[0][1])
            command = "SELECT * FROM members WHERE email=%s"
            data = (self.email_get,)
            cursor.execute(command, data)
            rows = cursor.fetchall()
            if len(rows) != 0:
                check.append(rows[0][3])

            if len(check) > 0:
                self.error_message.setText("Your username/e-mail combination is already taken.")
            else:
                data = (self.username_get, self.password_get, self.email_get.lower())
                insert_table(data)
                self.validating = LoginScreen.valid_user(self.email_get, self.username_get, self.password_get)
                if self.validating:
                    self.dashboard = Dashboard(self.password_get, self.email_get, self.username_get, self.x, self.y, self.width, self.height)
                    self.close()
                    self.dashboard.show()
                else:
                    self.error_message.setText("An error has occurred while logging in! Please manually login.")

    def back(self):
        self.main_window = Main(self.x, self.y, self.width, self.height)
        self.close()
        self.main_window.show()

class LoginScreen(QWidget):
    # GUI screen for returning members
    def __init__(self, x, y, width=500, height=500, parent=None):
        super().__init__()
        self.x, self.y, self.width, self.height = x, y, width, height
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(x, y, width, height)
        self.addWidgets()

    def addWidgets(self):
        self.error_message = QLabel()
        self.error_message.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; color: red;}")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")

        self.email = QLineEdit()
        self.email.setPlaceholderText("E-Mail Address")
        self.email.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet("QLineEdit {border: 2px; border-style: solid; border-color: rgba(85,172,238,1); border-radius: 10px; padding: 1px;}")
        self.password.setEchoMode(QLineEdit.Password)

        self.submit = QPushButton("Login")
        self.submit.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.submit.clicked.connect(self.login)

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.back_button.clicked.connect(self.back)

        self.layout = QFormLayout()
        self.layout.addWidget(self.error_message)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.email)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.submit)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def login(self):
        self.username_get = self.username.text()
        self.password_get = self.password.text()
        self.email_get = self.email.text()
        if self.valid_user(self.email_get, self.username_get, self.password_get):
            self.dashboard = Dashboard(self.password_get, self.email_get, row_username, self.x, self.y, self.width, self.height)
            self.close()
            self.dashboard.show()
        else:
            self.error_message.setText("Invalid username/password/e-mail address! Try again.")

    @staticmethod
    def valid_user(email, username, password):
        email = email.lower()
        command = "SELECT * FROM members WHERE email=%s"
        data = (email,)
        cursor.execute(command, data)
        rows = cursor.fetchall()
        if len(rows) != 0:
            row_id = rows[0][0]
            global row_username
            row_username = rows[0][1]
            row_password = rows[0][2]
            row_email = rows[0][3]
            if email == row_email.lower() and username.lower() == row_username.lower() and password == row_password:
                return True
            else:
                return False
        else:
            return False

    def back(self):
        self.main_window = Main(self.x, self.y, self.width, self.height)
        self.close()
        self.main_window.show()

class Detected(QWidget):
    # GUI screen to display possible intruders
    def __init__(self, type, password, email, user, x, y, width=500, height=500, parent=None):
        super().__init__()
        self.type, self.password, self.email, self.x, self.y, self.width, self.height, self.user = type, password, email, x, y, width, height, user
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(x, y, width, height)
        self.addWidgets()
        self.detect(0.9)

    def addWidgets(self):
        self.thief = QLabel("")
        self.thief.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; font-size: 30px; font-weight: 600;}")

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.back_button.clicked.connect(self.back)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.thief)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def detect(self, confidence):
        self.detection = src.GUI.predict.MaskPredict(self.type, confidence)
        self.detected = self.detection.detect()
        if self.detected[0]:
            self.thief.setText("A " + self.detected[1] + " has been detected at your door!")
            self.thief.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; font-size: 30px; font-weight: 600; color:red;}")

    def back(self):
        self.dashboard = Dashboard(self.password, self.email, self.user, self.x, self.y, self.width, self.height)
        self.close()
        self.dashboard.show()

class SettingsWindow(QWidget):
    # GUI screen to set certain settings
    def __init__(self, password, email, user, x, y, width=500, height=500, parent=None):
        super().__init__()
        self.x, self.y, self.width, self.height, self.user, self.password, self.email = x, y, width, height, user, password, email
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(x, y, width, height)
        self.addWidgets()

    def addWidgets(self):
        self.auto_login = False
        self.welcome_label = QLabel("Settings")
        self.welcome_label.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; font-size:30px; font-weight:600;}")

        self.detector_type = QComboBox(self)
        self.detector_type.setStyleSheet("QComboBox {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: black; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QComboBox:hover {background-color: rgba(69, 131, 186, 1);}")
        self.detector_type.addItem("Anyone who comes to my door")
        self.detector_type.addItem("Suspicious masked people")

        self.check = QCheckBox("Auto-login", self)
        self.check.stateChanged.connect(self.checkBoxChange)
        self.check.toggle()

        self.save = QPushButton("Save")
        self.save.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.save.clicked.connect(self.submit)

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.back_button.clicked.connect(self.back)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.welcome_label)
        self.layout.addWidget(self.detector_type)
        self.layout.addWidget(self.check)
        self.layout.addWidget(self.save)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def checkBoxChange(self, state):
        if state == Qt.Checked:
            self.auto_login = True
        else:
            self.auto_login = False

    def submit(self):
        self.current_text = str(self.detector_type.currentText())
        data = {"type": self.current_text, "auto_login": [self.auto_login, self.user, self.password, self.email]}
        with open("settings.yaml", "w") as f:
            dump = yaml.dump(data, f)
            f.close()
        self.back()

    def back(self):
        self.dashboard = Dashboard(self.password, self.email, self.user, self.x, self.y, self.width, self.height)
        self.close()
        self.dashboard.show()

class Dashboard(QWidget):
    # GUI screen for the dashboard
    def __init__(self, password, email, user, x, y, width=500, height=500, parent=None):
        super().__init__()
        with open("settings.yaml") as file:
            self.doc = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
        if not self.doc:
            self.type = None
            self.auto_login = None
        else:
            self.type = self.doc["type"]
            self.auto_login = self.doc["auto_login"]

        self.x, self.y, self.width, self.height, self.user, self.password, self.email = x, y, width, height, user, password, email
        self.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.setWindowTitle("Who Is At My Door?")
        self.setGeometry(x, y, width, height)
        self.addWidgets()

    def addWidgets(self):
        self.welcome_label = QLabel("Welcome,  " + self.user)
        self.welcome_label.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; font-size:30px; font-weight:600;}")

        self.start = QPushButton("Start")
        self.start.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.start.clicked.connect(self.detect)

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.back_button.clicked.connect(self.back)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet("QPushButton {background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0.273, stop:0 rgba(85,172,238,1), stop:1 rgba(79, 165, 240, 1)); border-radius: 15px; color: white; font: bold 15px; min-width: 4em; min-height: 1.8em; padding: 1px;} QPushButton:hover {background-color: rgba(69, 131, 186, 1);}")
        self.settings_button.clicked.connect(self.settings)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.welcome_label)
        self.layout.addWidget(self.start)
        self.layout.addWidget(self.settings_button)
        self.layout.addWidget(self.back_button)
        self.setLayout(self.layout)

    def back(self):
        self.main_window = Main(self.x, self.y, self.width, self.height)
        self.close()
        self.main_window.show()

    def settings(self):
        self.settings_window = SettingsWindow(self.password, self.email, self.user, self.x, self.y, self.width, self.height)
        self.close()
        self.settings_window.show()

    def detect(self):
        self.detected_window = Detected(self.type, self.password, self.email, self.user, self.x, self.y, self.width, self.height)
        self.close()
        self.detected_window.show()


class SplashScreen(QSplashScreen):
    # Loading screen with the throbber
    def __init__(self, animation, flags):
        QSplashScreen.__init__(self, QPixmap(), flags)
        self.movie = QMovie(animation)
        self.connect(self.movie, SIGNAL('frameChanged(int)'), SLOT('onNextFrame()'))
        self.movie.start()

    def onNextFrame(self):
        pixmap = self.movie.currentPixmap()
        self.setPixmap(pixmap)
        self.setMask(pixmap.mask())

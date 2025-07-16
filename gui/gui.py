from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QStackedLayout, QFormLayout,
    QLabel, QLineEdit, QCheckBox, QHBoxLayout, QListWidget, QVBoxLayout, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QRunnable, pyqtSlot, QThreadPool
from app.api import *
import sys, os
from db.database import *
from app.JsonToCSV import GetCSV
import time, requests

class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 250)

        self.conn, self.cursor = open_connection()
        self.current_user_email = None
        self.json_path = None
        self.access_token = None
        self.refresh_token = None
        self.current_user_id = None

        self.setWindowTitle('Spotify PlayList Transfer')
        self.stacked_layout = QStackedLayout()
        self.main_layout = QVBoxLayout()

        self.login_page = QWidget()
        self.signup_page = QWidget()
        self.list_page = QWidget()
        self.filter_page = QWidget()
        self.new_request_page = QWidget()
        self.token_page = QWidget()

        self.login_page_layout = QFormLayout()
        self.signup_page_layout = QFormLayout()
        self.list_page_layout = QFormLayout()
        self.filter_page_layout = QFormLayout()
        self.new_request_page_layout = QFormLayout()
        self.token_page_layout = QFormLayout()

        self.login_page.setLayout(self.login_page_layout)
        self.signup_page.setLayout(self.signup_page_layout)
        self.list_page.setLayout(self.list_page_layout)
        self.filter_page.setLayout(self.filter_page_layout)
        self.new_request_page.setLayout(self.new_request_page_layout)
        self.token_page.setLayout(self.token_page_layout)

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(2)
        

        # login page set up
            # row 1
        self.signup_button = QPushButton('Sign Up')
        self.signup_button.clicked.connect(self.__go_to_signup)
        self.row11 = QHBoxLayout()
        self.row11.addWidget(self.signup_button)
        self.row11.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.login_page_layout.addRow(self.row11)

            # row 2
        self.email_fl = QLineEdit()
        self.email_fl.setPlaceholderText('Enter your email')
        self.error_l = QLabel()
        self.row12 = QVBoxLayout()
        self.row12.addWidget(self.error_l)
        self.row12.addWidget(self.email_fl)
        self.login_page_layout.addRow(self.row12)

            # row 3
        self.password_fl = QLineEdit()
        self.password_fl.setPlaceholderText('Enter your password')
        self.row13 = QVBoxLayout()
        self.row13.addWidget(self.password_fl)
        self.login_page_layout.addRow(self.row13)

            # row 4
        self.login = QPushButton('Log In')
        self.login.clicked.connect(self.__check_user)
        self.login_page_layout.addRow(self.login)

        # signup page set up
            # row 1
        self.login_button = QPushButton('Log In')
        self.login_button.clicked.connect(self.__go_to_login)
        self.row21 = QHBoxLayout()
        self.row21.addWidget(self.login_button)
        self.row21.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.signup_page_layout.addRow(self.row21)

            # row 2
        self.email_fs = QLineEdit()
        self.error_s = QLabel()
        self.row22 = QVBoxLayout()
        self.row22.addWidget(self.error_s)
        self.row22.addWidget(self.email_fs)
        self.email_fs.setPlaceholderText('Set your email')
        self.signup_page_layout.addRow(self.row22)

            # row 3
        self.password_fs = QLineEdit()
        self.password_fs.setPlaceholderText('Set your password')
        self.signup_page_layout.addRow(self.password_fs)

            # row 4
        self.signup = QPushButton('Sign Up')
        self.signup.clicked.connect(self.__signup_new_user)
        self.signup_page_layout.addRow(self.signup)

        # token page
            # row 1
        self.tokens_error = QLabel('getting access token...')
        self.token_page_layout.addRow(self.tokens_error)

        # list page set up
            # row 1
        self.col31 = QHBoxLayout()
        self.list_title = QLabel('Your Playlists:')
        self.reload = QPushButton('Refresh List')
        self.col31.addWidget(self.reload)
        self.reload.clicked.connect(self.__show_playlists)
        self.col31.addStretch()
        self.creat = QPushButton('Create new playlist')
        self.creat.clicked.connect(self.__go_to_filter)
        self.col31.addWidget(self.creat)
        self.row31 = QVBoxLayout()
        self.row31.addLayout(self.col31)
        self.ans = QListWidget()
        self.row31.addWidget(self.list_title)
        self.row31.addWidget(self.ans)
        self.list_page_layout.addRow(self.row31)

        # filter page
            # row 1
        self.ispub = QCheckBox('Public PlayList')
        self.iscoll = QCheckBox('Collabrative Playlist')
        self.filter_page_layout.addRow(self.ispub, self.iscoll)

            # row 2
        self.plname = QLineEdit()
        self.plname.setPlaceholderText('Enter your playlist name')
        self.filter_page_layout.addRow(self.plname)

            # row 3
        self.row43 = QVBoxLayout()
        self.upload = FileUploader()
        self.lunch = QPushButton('Open json file')
        self.lunch.clicked.connect(self.__get_file_path)
        self.show_file_path = QLabel()
        self.row43.addStretch()
        self.row43.addWidget(self.lunch)
        self.row43.addWidget(self.show_file_path)
        self.filter_page_layout.addRow(self.row43)

            # row 4
        self.creat = QPushButton('Create')
        self.creat.clicked.connect(self.__go_to_new_request)
        self.filter_page_layout.addRow(self.creat)

        # new request page set up
            # row 1
        self.load_song_tilte = QLabel()
        self.load_song = LoadingBar()
        self.row52 = QVBoxLayout()
        self.row52.addWidget(self.load_song_tilte)
        self.row52.addWidget(self.load_song)
        self.new_request_page_layout.addRow(self.row52)

            # row 2
        self.load_query_tilte = QLabel('Waiting...')
        self.load_query = LoadingBar()
        self.row53 = QVBoxLayout()
        self.row53.addWidget(self.load_query_tilte)
        self.row53.addWidget(self.load_query)
        self.new_request_page_layout.addRow(self.row53)

        self.stacked_layout.addWidget(self.login_page)
        self.stacked_layout.addWidget(self.signup_page)
        self.stacked_layout.addWidget(self.list_page)
        self.stacked_layout.addWidget(self.filter_page)
        self.stacked_layout.addWidget(self.new_request_page)
        self.stacked_layout.addWidget(self.token_page)
        self.stacked_layout.setCurrentIndex(1)

        self.main_layout.addLayout(self.stacked_layout)

        self.quit = QPushButton('Quit the app')
        self.quit.clicked.connect(self.__quit)
        self.new_request_page_layout.addRow(self.quit)

        self.main_layout.addWidget(self.quit)
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def __signup_new_user(self):
        if is_user_there(self.cursor, self.email_fs.text()):
            self.error_s.setText("You have account, no need to sign up.")
        else:
            add_new_user(self.conn, self.cursor, 
                        self.email_fs.text(), self.password_fs.text())
            self.stacked_layout.setCurrentIndex(0)
        
    def __check_user(self):
        if is_user_there(self.cursor, self.email_fl.text()) and is_pass_correct(self.cursor, self.email_fl.text(), self.password_fl.text()):
            self.current_user_email = self.email_fl.text()
            self.__go_to_token()

        else:
            self.error_l.setText("Your username or password is wrong.")

    def __show_playlists(self):
        if not self.current_user_id:
            if show_user_id:
                self.current_user_id = show_user_id(cursor=self.cursor, email=self.current_user_email)
            else:
                self.current_user_id = get_user_id(email=self.current_user_email, access_token=self.access_token)
        the_playlists = list_user_playlists(user_id=self.current_user_id, access_token=self.access_token)
        update_playlist(self.conn, self.cursor, self.current_user_id, *the_playlists)
        for result in playlists(self.cursor, self.current_user_email):
            self.ans.addItem(result[0])
        return self.ans

    def __starting_progress(self):
        self.stacked_layout.setCurrentIndex(4)
        MyPlayList = PlayList(plname=self.plname.text(), access_token=self.access_token, 
                        ispublic=self.ispub.isChecked(), iscollabrative=self.iscoll.isChecked(), user_id=self.current_user_id)
        
        MyGetCSV = GetCSV(self.json_path)
        mySongs = MyGetCSV.song_json_csv()

        self.load_song.add_length(len(mySongs))

        all_uris = {}
        numsLists = int(len(mySongs) / 100) + ((len(mySongs) % 100) != 0)
        wasted_songs = {
            'Track name': [],
            'Artist name': []
        }
        for i in range(numsLists):
            all_uris[f'uris{i+1}'] = []
        
        counter = 1
        self.load_song_tilte.setText('Loading songs...')
        for row in range(len(mySongs)):
            try:
                songURI = MyPlayList.find_uri(song_name=mySongs['Track name'][row],
                                            artist_name=mySongs['Artist name'][row])
                
                if songURI:
                    all_uris[f'uris{counter}'].append(songURI)
                else:
                    wasted_songs['Artist name'].append(row.get('performer', ''))
                    wasted_songs['Track name'].append(row.get('title', ''))

                if len(all_uris[f'uris{counter}']) == 100:
                    counter += 1
            except requests.exceptions.SSLError:
                wasted_songs.append(f'{mySongs['Track name'][row]} - {mySongs['Artist name'][row]}')
                continue
            
            time.sleep(0.2)
            self.load_song.update_progress()
        self.load_song_tilte.setText('Done.')
        MyGetCSV.export_csv(wasted_songs)

        self.load_query.add_length(len(all_uris))

        self.load_query_tilte.setText('Adding songs to the playlist...')
        for key in all_uris:
            MyPlayList.add_songs(uris=all_uris[key])
            self.load_query.update_progress()
        self.load_query_tilte.setText("Done.")
        self.stacked_layout.setCurrentIndex(2)

                
    def __get_tokens(self):
        worker_conn, worker_cursor = open_connection()
        MyAccessToken = UserAccessToken()
        self.access_token, self.refresh_token = get_tokens(worker_cursor, self.current_user_email)
        if not self.access_token:
            self.tokens_error.setText("The access token not found. redirecting to the authorization.")
            MyAccessToken.get_access_token(self.current_user_email)
            self.access_token, self.refresh_token = get_tokens(worker_cursor, self.current_user_email)
            
        else:
            response = requests.get("https://api.spotify.com/v1/me", headers={
                "Authorization": f"Bearer {self.access_token}"
            })
            if response.status_code == 401:
                self.tokens_error.setText('The access token has expired. getting new access token from refresh token.')
                MyAccessToken.refresh_access_token(self.current_user_email)
                self.access_token, self.refresh_token = get_tokens(worker_cursor, self.current_user_email)
            
            else:
                self.tokens_error.setText('Getting the access token successfully.')
            
        close_connection(worker_conn)
        self.stacked_layout.setCurrentIndex(2)
            

    def __go_to_login(self):
        self.stacked_layout.setCurrentIndex(0)

    def __go_to_signup(self):
        self.stacked_layout.setCurrentIndex(1)
    
    def __go_to_filter(self):
        self.stacked_layout.setCurrentIndex(3)
    
    def __get_file_path(self):
        self.json_path = self.upload.upload_file()
        self.show_file_path.setText(self.json_path)

    def __go_to_new_request(self):
        worker = Worker(
            self.__starting_progress
        )
        self.threadpool.start(worker)

    def __go_to_token(self):
        worker = Worker(
            self.__get_tokens
        )
        self.stacked_layout.setCurrentIndex(5)
        self.threadpool.start(worker)

    def __quit(self):
        close_connection(self.conn)
        QApplication.quit()

class FileUploader(QWidget):
    def __init__(self):
        super().__init__()

    def upload_file(self):
        filefilter = 'Data File (*.json)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select file',
            filter=filefilter,
            directory=os.getcwd()
        )

        if response:
            return response[0]
        
class LoadingBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.length = None
        self.setMaximum(100)
        self.start = 0

    def add_length(self, length):
        self.length = length

    def update_progress(self):
        self.start += 1
        self.setValue(int((self.start / self.length) * 100))




def load_stylesheet(file_path):
    with open(file_path, "r") as f:
        return f.read()

app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet("theme.qss"))
MyMainWindow = MainWindow()

MyMainWindow.show()
sys.exit(app.exec())
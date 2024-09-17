from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from Components.btmapp_sheets import BTMAppSheets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic
class PlayersUI(QWidget):
    
    def __init__(self, parent): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        
    def InitUi(self):     
        # Get Config
        self.config = GetConfig.read_config()
        self.import_url = self.config['TOURNAMENT_DETAILS']['URL']
        # Setup API
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            self.c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])
            if self.import_url != "":
                self.tournament = self.c_api.get_tournament(self.import_url)
        # Directly find the child widgets within self
        self.player_table = self.parent_widget.findChild(QTableWidget, 'player_table')
        self.import_button = self.parent_widget.findChild(QPushButton, 'import_btn')
        self.load_button = self.parent_widget.findChild(QPushButton, 'load_btn')
        self.add_player = self.parent_widget.findChild(QPushButton, 'padd_btn')
        self.create_button = self.parent_widget.findChild(QPushButton, 'create_btn')
        self.current_url = self.parent_widget.findChild(QLabel, 'current_url')
        self.status_label = self.parent_widget.findChild(QLabel, 'status_label')
        self.player_count = self.parent_widget.findChild(QLabel, 'pcount_label')
        self.start_button = self.parent_widget.findChild(QPushButton, 'start_btn')
        
        if self.player_table is None or self.import_button is None or self.load_button is None:
            print("Checkin table or button not found")
            return
        
        if self.tournament is not None:
            # Populate the table
            self.populate_table()
            
        # Finally connect the button events
        self.import_button.clicked.connect(self.execute_importDiag)
        self.load_button.clicked.connect(self.show_load_previous)
        self.create_button.clicked.connect(self.show_create_tournament)
        self.add_player.clicked.connect(self.add_new_player)
        self.start_button.clicked.connect(self.start_tournamnet)
    
    def update_ui(self):
        if self.tournament is not None:
            self.status_label.setText("Tournament Status: " + self.tournament.get_state())
            self.player_count.setText("Player Count: " + str(self.tournament.get_participants_count()))
            
            if self.tournament.get_state() == "pending":
                self.start_button.setEnabled(True)
            else:
                self.start_button.setEnabled(False)
        
        if self.import_url != "":
            self.current_url.setText("Current URL: https://challonge.com/" + self.import_url)
       
    def populate_table(self):
        # Get Config
        self.config = GetConfig.read_config()
        
        self.import_url = self.config['TOURNAMENT_DETAILS']['URL']
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            self.c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])

        try:
            # Get the tournament
            # Check to see if the URL has changed
            if self.tournament.get_url() != self.import_url:  
                self.tournament = self.c_api.get_tournament(self.import_url)
                
            participants = self.c_api.get_participants(self.tournament.get_id())
            
            self.player_table.setRowCount(len(participants))
            self.player_table.setColumnCount(4)
            # Set the headers
            self.player_table.setHorizontalHeaderLabels(["Player", "Region", "Checked in At", "Checked In"])
            
            for i in range(0, len(participants)):
                for j in range(0, 2):
                    match j:
                        case 0:
                            item = QTableWidgetItem(participants[i].get_name())
                            self.player_table.setItem(i, j, item)
                        case 1:
                            checkbox_widget = QWidget()
                            layout = QHBoxLayout(checkbox_widget)
                            layout.addWidget(QCheckBox())
                            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            layout.setContentsMargins(0, 0, 0, 0)
                            checkbox_widget.setLayout(layout)
                            self.player_table.setCellWidget(i, 3, checkbox_widget)
                        case 2:                        
                            if participants[i].get_checked_in():
                                item = QTableWidgetItem(participants[i].get_checked_in_at())
                                self.player_table.setItem(i, j, item)
            self.update_ui()
        except:
            print("Error getting tournament")
    
    def update_table(self):
        # Get Config
        self.config = GetConfig.read_config()
        
        self.import_url = self.config['TOURNAMENT_DETAILS']['URL']
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            try:
                participants = self.c_api.get_participants(self.tournament.get_id())
                
                # Check for new participants
                if len(participants) > self.player_table.rowCount():
                    self.player_table.setRowCount(len(participants))
                    for i in range(0, len(participants)):
                        for j in range(0, 2):
                            match j:
                                case 0:
                                    item = QTableWidgetItem(participants[i].get_name())
                                    self.player_table.setItem(i, j, item)
                                case 1:
                                    checkbox_widget = QWidget()
                                    layout = QHBoxLayout(checkbox_widget)
                                    layout.addWidget(QCheckBox())
                                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                    layout.setContentsMargins(0, 0, 0, 0)
                                    checkbox_widget.setLayout(layout)
                                    self.player_table.setCellWidget(i, 3, checkbox_widget)
                                case 2:                        
                                    if participants[i].get_checked_in():
                                        item = QTableWidgetItem(participants[i].get_checked_in_at())
                                        self.player_table.setItem(i, j, item)
                self.update_ui()
            except:
                print("Error getting tournament")
            
    def execute_importDiag(self):
        # Create the dialog
        import_diag = QInputDialog()
        import_diag.setLabelText("Enter the Challonge URL")
        import_diag.setInputMode(QInputDialog.InputMode.TextInput)
        import_diag.setOkButtonText("Import")
        import_diag.setCancelButtonText("Cancel")
                
        # Get the URL
        if import_diag.exec() == QDialog.DialogCode.Accepted:
            self.import_url = self.format_url(import_diag.textValue())
            GetConfig.set_url(self.import_url)
            self.clear_table()
            self.populate_table()
    
    def start_tournamnet(self):
        try:            
            id = self.tournament.get_id()
            self.c_api.start_tournament(id)
            
            # Update the tournament once it's opened to get the new state
            self.tournament = self.c_api.get_tournament(self.import_url)
            
            self.update_ui()
        except (Exception) as e:
            print("Error starting tournament: " + str(e))
    
    def show_create_tournament(self):
        try:            
            create_tournament = CreateTournament()
            create_tournament.exec()
            
            # Check if the tournament was created
            if create_tournament.t is not None:
                self.import_url = self.format_url(create_tournament.t.get_url())
                GetConfig.set_url(self.import_url)
                self.clear_table()
                self.populate_table
            
        except(Exception) as e:
            print("Error creating tournament" + str(e))

    def show_load_previous(self):
        try:
            load_previous = LoadPrevious()
            load_previous.exec()
            
            if load_previous.url is not None:
                self.import_url = load_previous.url
                GetConfig.set_url(self.import_url)
                self.clear_table()
                self.populate_table()
        except(Exception) as e:
            print("Error loading previous tournament" + str(e))        
    
    def create_tournament(self):
        t = ChallongeAPI.create_tournament(self.name, self.desc, self.t_type)

        
        self.import_url = self.format_url(t.get_url())
        GetConfig.set_url(self.import_url)
        self.clear_table()
        self.populate_table()
    
    def add_new_player(self):
        try:
            # Open new player dialog
            add_player = AddNewPlayer(self.tournament.get_id())
            add_player.exec()
            self.update_table()
        except (Exception) as e:
            print("Error adding new player: " + str(e))
    
    def format_url(self, url):
        # Regex to get code from URL. Example: https://challonge.com/12345678
        # Returns 12345678
        print(url.split('/')[-1])
        return url.split('/')[-1]
    
    def clear_table(self):
        self.player_table.clear()
        self.player_table.setRowCount(0)
        self.player_table.setColumnCount(0)
        
class CreateTournament(QDialog):
    def __init__(self):
        super().__init__() 
        #self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        uic.loadUi('./src/GUI/new_tournament.ui', self)
        self.config = GetConfig.read_config()
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            self.c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])
        
        self.tournament_name = self.findChild(QTextEdit, "name_text")
        self.description = self.findChild(QTextEdit, "desc_text")
        self.t_type = self.findChild(QComboBox, "type_cb")
        self.dialog_button = self.findChild(QDialogButtonBox, "buttonBox")
        
        # Get the OK button
        self.ok_button = self.dialog_button.button(QDialogButtonBox.StandardButton.Ok)
        
        # Connect the OK button to the create function
        self.ok_button.clicked.connect(self.create)
        
        
    def create(self):    
        try:
            print(self.t_type.currentText())
            self.t = ChallongeAPI.create_tournament(
                self.tournament_name.toPlainText(),
                self.description.toPlainText(),
                self.t_type.currentText()
            )          
            GetConfig.set_url(self.t.get_url())
            
            self.t = self.c_api.get_tournament(self.t.get_url())
            date = None

            if self.t.get_started_at() is not None:
                date = self.t.get_started_at().strftime("%d/%m/%Y")
            else:
                date = self.t.get_created_at().strftime("%d/%m/%Y")

            sheet_name = self.t.get_name() + " - " + date
        
            sheets = BTMAppSheets(self.config['GOOGLE_SHEETS']['URL'])
            sheets.create_sheet(sheet_name)
        except (Exception) as e:
            print("Error creating tournament: " + str(e))
    
class LoadPrevious(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('./src/GUI/previous_tournament.ui', self)
        
        self.previous = self.findChild(QComboBox, "previous_cb")
        
        # Populate the previous combobox
        for url in GetConfig.get_previous():
            self.previous.addItem(url)
        
        self.dialog_button = self.findChild(QDialogButtonBox, "buttonBox")
        
        # Get the OK button
        self.ok_button = self.dialog_button.button(QDialogButtonBox.StandardButton.Ok)
        
        # Connect the OK button to the create function
        self.ok_button.clicked.connect(self.load)
        
    def load(self):
        self.url = self.previous.currentText()        
        GetConfig.set_url(self.url)

class AddNewPlayer(QDialog):
    def __init__(self, tournament_id):
        super().__init__()
        uic.loadUi('./src/GUI/new_player.ui', self)
        self.tournament_id = tournament_id
        self.player_name = self.findChild(QTextEdit, "nameTxt")
        self.dialog_button = self.findChild(QDialogButtonBox, "buttonBox")
        
        # Get the OK button
        self.ok_button = self.dialog_button.button(QDialogButtonBox.StandardButton.Ok)
        
        # Connect the OK button to the create function
        self.ok_button.clicked.connect(self.add)
        
    def add(self):
        try:
            p = ChallongeAPI.add_participant(self.tournament_id, self.player_name.toPlainText())
        except (Exception) as e:
            print("Error adding participant: " + str(e))


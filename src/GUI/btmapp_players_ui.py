from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic
class PlayersUI(QWidget):
    
    def __init__(self, parent): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        
    def InitUi(self):     
        # Directly find the child widgets within self
        self.player_table = self.parent_widget.findChild(QTableWidget, 'player_table')
        self.import_button = self.parent_widget.findChild(QPushButton, 'import_btn')
        self.load_button = self.parent_widget.findChild(QPushButton, 'load_btn')
        self.create_button = self.parent_widget.findChild(QPushButton, 'create_btn')
        self.current_url = self.parent_widget.findChild(QLabel, 'current_url')
        
        if self.player_table is None or self.import_button is None or self.load_button is None:
            print("Checkin table or button not found")
            return
        
        # Populate the table
        self.populate_table()
        
        
        # Finally connect the button events
        self.import_button.clicked.connect(self.execute_importDiag)
        self.load_button.clicked.connect(self.show_load_previous)
        self.create_button.clicked.connect(self.show_create_tournament)
        
                    

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
        
    def populate_table(self):
        # Get Config
        self.config = GetConfig.read_config()
        
        self.import_url = self.config['TOURNAMENT_DETAILS']['URL']
        self.current_url.setText("Current URL: https://challonge.com/" + self.import_url)
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])
            print(self.config['CHALLONGE']['USERNAME'])

        try:
            # Get the tournament
            tournament = c_api.get_tournament(self.import_url)
            participants = c_api.get_participants(tournament.get_id())
            
            self.player_table.setRowCount(len(participants))
            self.player_table.setColumnCount(4)
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
        

        import_diag
        # Create the dialog
        load_diag = QInputDialog()
        load_diag.setLabelText("Select a previous tournament")
        
        # Generate a list of previous tournaments
        previous = GetConfig.get_previous()
        
        # Set the items
        load_diag.setComboBoxItems(previous)
        
        load_diag.setOkButtonText("Load")
        load_diag.setCancelButtonText("Cancel")
    
       # Get the URL
        if load_diag.exec() == QDialog.DialogCode.Accepted:
            self.import_url = load_diag.textValue()
            GetConfig.set_url(self.import_url)
            self.clear_table()
            self.populate_table()
    
      
        
    
    def test(self):
        print("Test")
    
    def create_tournament(self):
        t = ChallongeAPI.create_tournament(self.name, self.desc, self.t_type)
        self.import_url = self.format_url(t.get_url())
        GetConfig.set_url(self.import_url)
        self.clear_table()
        self.populate_table()
    
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


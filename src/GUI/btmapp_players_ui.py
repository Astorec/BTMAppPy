from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from Components.btmapp_sheets import BTMAppSheets
from Classes.player import Player
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic
from Components.btmapp_gauth import GAuth

class PlayersUI(QWidget):
    
    def __init__(self, parent, service): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        self.service = service
        
    def InitUi(self):     
        # Get Config
        self.config = GetConfig.read_config()
        self.import_url = self.config['TOURNAMENT_DETAILS']['URL']
        self.tournament = None
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
        self.remove_player_button = self.parent_widget.findChild(QPushButton, 'premove_btn')
        self.create_button = self.parent_widget.findChild(QPushButton, 'create_btn')
        self.current_url = self.parent_widget.findChild(QLabel, 'current_url')
        self.status_label = self.parent_widget.findChild(QLabel, 'status_label')
        self.player_count = self.parent_widget.findChild(QLabel, 'pcount_label')
        self.start_button = self.parent_widget.findChild(QPushButton, 'start_btn')
        self.type_label = self.parent_widget.findChild(QLabel, 'type_label')
        self.players_group_a = []
        self.players_group_b = []
        self.players_group_finals = []
        self.players_group_none = []
        self.players = []

        if self.tournament is not None:
            self.type_label.setText("Tournament Type: " + self.tournament.get_tournament_type())
        
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
        self.remove_player_button.clicked.connect(self.remove_player)
        self.start_button.clicked.connect(self.start_tournamnet)
        
        self.player_table.itemSelectionChanged.connect(self.update_ui)
        
    
    def update_ui(self):
        if self.tournament is not None:
            self.tournament = self.c_api.get_tournament(self.import_url)
            self.status_label.setText("Tournament Status: " + self.tournament.get_state())
            self.player_count.setText("Player Count: " + str(self.tournament.get_participants_count()))
            self.type_label.setText("Tournament Type: " + self.tournament.get_tournament_type())

            
            if self.tournament.get_state() == "pending":
                self.start_button.setEnabled(True)
                self.add_player.setEnabled(True)                
            else:
                self.start_button.setEnabled(False)
                self.add_player.setEnabled(False)
                
        # If player is selected enable the remove button
        if self.player_table.currentRow() != -1:
            self.remove_player_button.setEnabled(True)
        else:
            self.remove_player_button.setEnabled(False)
        
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

                            # Add player to list if not already in the global list
                            if participants[i].get_name() not in self.players:
                                self.players.append(self.format_player(participants[i]))
                        case 2:                        
                            if participants[i].get_checked_in():
                                item = QTableWidgetItem(participants[i].get_checked_in_at())
                                self.player_table.setItem(i, j, item)

            self.update_ui()
            
            if self.config['GOOGLE_SHEETS']['URL'] != "":
                self.sheets = BTMAppSheets(self.config['GOOGLE_SHEETS']['URL'], self.service)
        except (Exception) as e:
            print("Error getting tournament - " + str(e))
    
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
                                        
                # Check to see if a player has been removed
                if len(participants) < self.player_table.rowCount():
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

    def assign_to_group(self, player, group = None):
        match(group):
            case "A":
                # Check to see if the list already contains the player id
                exists = any(p.get_id() == player.get_id() for p in self.players_group_a)

                if exists:
                    # Get the player from the list based on the ID
                    p = next((p for p in self.players_group_a if p.get_id() == player.get_id()), None)
                    # Remove the player from the list
                    self.players_group_a.remove(p)
                    # Add the player to the list
                    self.players_group_a.append(player)
                else:

                    self.players_group_a.append(player)
            case "B":
                exists = any(p.get_id() == player.get_id() for p in self.players_group_b)
                
                if exists:
                    p = next((p for p in self.players_group_b if p.get_id() == player.get_id()), None)
                    self.players_group_b.remove(p)
                    self.players_group_b.append(player)
                else:
                    self.players_group_b.append(player)
            case "Finals":

                exists = any(p.get_id() == player.get_id() for p in self.players_group_finals)
                if  exists:
                    p = next((p for p in self.players_group_finals if p.get_id() == player.get_id()), None)
                    self.players_group_finals.remove(p)
                    self.players_group_finals.append(player)
                else:
                    self.players_group_finals.append(player)
            case None:

                exists = any(p.get_id() == player.get_id() for p in self.players_group_none)
                if  exists:
                    p = next((p for p in self.players_group_none if p.get_id() == player.get_id()), None)
                    self.players_group_none.remove(p)
                    self.players_group_none.append(player)
                else:
                    self.players_group_none.append(player)

    def clear_group(self, group = None):
        match(group):
            case "A": 
                self.players_group_a.clear()
            case "B":
                self.players_group_b.clear()
            case "Finals":
                self.players_group_finals.clear()
            case None:
                self.players_group_none.clear()

    def sort_players_to_groups(self):
        # Get the participants from challonge
    
        matches = self.c_api.get_matches(self.tournament.get_id())
        highest_id = 0 # I think this is group A
        lowest_id = 0 # And this is group B
        # If there is group ID this usually means it's in the finals 
        for match in matches:
            if match.get_group_id() is not None:
                if match.get_group_id() > highest_id:
                    highest_id = match.get_group_id()
                if match.get_group_id() < highest_id:
                    lowest_id = match.get_group_id()

    
        for p in self.players:
            is_finals = False
            player_final = None
            for m in matches:
               if m.get_player1_id() == p.get_id() or m.get_player1_id() == p.get_group_id()[0] or m.get_player2_id() == p.get_id() or m.get_player2_id() == p.get_group_id()[0]:
                    
                    if m.get_group_id() is not None:
                        if m.get_winner_id() == p.get_id() or m.get_winner_id() == p.get_group_id()[0]:
                            p.updateScore(1, 0)
                        elif m.get_loser_id() == p.get_id() or m.get_loser_id() == p.get_group_id()[0]:
                            p.updateScore(0, 1)
                    else:
                        if not is_finals:                            
                            is_finals = True
                            # Create a new player object for the finals
                            player_final = Player(p.get_name(), p.get_id(), p.get_group_id())
                            player_final.updateScore(0, 0)
                        
                        if m.get_winner_id() == p.get_id() or m.get_winner_id() == p.get_group_id()[0]:
                            player_final.updateScore(1, 0)
                        elif m.get_loser_id() == p.get_id() or m.get_loser_id() == p.get_group_id()[0]:
                            player_final.updateScore(0, 1)
                            


                    if len(self.players) <= 7:
                        self.assign_to_group(p)
                    elif m.get_group_id()== highest_id:
                        self.assign_to_group(p, "A")
                    elif m.get_group_id() == lowest_id:
                        self.assign_to_group(p, "B")
                    else:
                        self.assign_to_group(player_final, "Finals")

        print("Group A: " + str(len(self.players_group_a)))                 

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
            self.check_for_sheet()
            
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
                participants = self.c_api.get_participants(self.tournament.get_id())
                if self.players_group_a is None or self.players_group_b is None or self.players_group_finals is None or self.players_group_none is None:
                    self.sort_players_to_groups()
                if len(participants) <= 7:
                    self.sheets.create_sheet(self.tournament.get_related_sheet(), self.players_group_none)
                else:
                    self.sheets.create_sheet(self.tournament.get_related_sheet(), [self.players_group_a, self.players_group_b], ["A", "B"])
            
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
            # get the player from the dialog
            p = add_player.get_participant()
            
            if p == "Participant already in the tournament":
                # Display Dialog saying the player is already in the tournament
                dialog = QDialog()
                dialog.setWindowTitle("Error")
                dialog.setFixedSize(300, 100)
                dialog.setModal(True)
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(QLabel("Participant already in the tournament"))
                dialog_button = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
                # Add button below the label
                dialog.layout().addWidget(dialog_button)
                dialog_button.accepted.connect(dialog.accept)                
                dialog.exec()
                
                return
            fromated_player = self.format_player(p)
            self.sheets.add_player(self.tournament.get_related_sheet(), fromated_player)
            self.update_table()    
               
            # Check to see if we need to update the Tournament Type
            self.c_api.update_format(self.tournament.get_id(), self.tournament.get_participants_count())
            
          
            
        except (Exception) as e:
            print("Error adding new player: " + str(e))
    
    def remove_player(self):
        # Get the selected row
        row = self.player_table.currentRow()
        # Get the player name
        player_name = self.player_table.item(row, 0).text()
        
        # Get the participants
        self.participants = self.c_api.get_participants(self.tournament.get_id())
        
        # Find the player
        for p in self.participants:
            if p.get_name() == player_name:
                self.c_api.remove_participant(self.tournament.get_id(), p.get_id())
                self.sheets.remove_player(self.tournament.get_related_sheet(), player_name)
                
                # look in the group lists and remove the player
                for player in self.players_group_a:
                    if player.get_name() == player_name:
                        self.players_group_a.remove(player)
                for player in self.players_group_b:
                    if player.get_name() == player_name:
                        self.players_group_b.remove(player)
                for player in self.players_group_finals:
                    if player.get_name() == player_name:
                        self.players_group_finals.remove(player)
                for player in self.players_group_none:
                    if player.get_name() == player_name:
                        self.players_group_none.remove(player)

                self.tournament = self.c_api.get_tournament(self.import_url)
                
                self.update_table()
                self.c_api.update_format(self.tournament.get_id(), self.tournament.get_participants_count())
                self.update_ui()
                return
    
    def format_url(self, url):
        # Regex to get code from URL. Example: https://challonge.com/12345678
        # Returns 12345678
        print(url.split('/')[-1])
        return url.split('/')[-1]
    
    def clear_table(self):
        self.player_table.clear()
        self.player_table.setRowCount(0)
        self.player_table.setColumnCount(0)
    
    def format_players(self):
        # get the participants
        participants = self.c_api.get_participants(self.tournament.get_id())
        
        # Get matches
        matches = self.c_api.get_matches(self.tournament.get_id())
        players = []
        for p in participants:
            player = Player(p.get_name(), p.get_id(), p.get_group_player_ids())
            player.updateScore(0, 0)
            print("Player ID: " + str(player.get_id()) + " Player Group ID: " + str(player.get_group_id()[0]))
            for m in matches:
                if m.get_player1_id() == player.get_id() or m.get_player1_id() == player.get_group_id()[0] or m.get_player2_id() == player.get_id() or m.get_player2_id() == player.get_group_id()[0]:
                    if m.get_state() == "complete":
                        print("Winner ID: " + str(m.get_winner_id()))
                        if m.get_winner_id() == player.get_id() or m.get_winner_id() == player.get_group_id()[0]:
                            player.updateScore(1, 0)
                        else:
                            player.updateScore(0, 1)
         
            players.append(player)
        
        # Determine who came first second and third
        if len(players) > 3:
            players.sort(key=lambda x: x.get_wins(), reverse=True)
            players[0].addFirst()
            players[1].addSecond()
            players[2].addThird()
        
        return players
    
    def format_player(self, participant):
        player = Player(participant.get_name(), participant.get_id(), participant.get_group_player_ids())
        player.updateScore(0, 0)
        return player
        
    def check_for_sheet(self):
        
        if self.sheets is not None:
            # Check to see if the tournament has a sheet associated with it
            date = None
            if self.tournament.get_started_at() is not None:
                date = self.tournament.get_started_at().strftime("%d/%m/%Y")
            else:
                date = self.tournament.get_created_at().strftime("%d/%m/%Y")
                
            sheet_name = self.tournament.get_name() + " - " + date

            participants = self.c_api.get_participants(self.tournament.get_id())
            
            if not self.sheets.check_sheet_exists(sheet_name): 
                if len(participants) > 0:
                    self.sort_players_to_groups()
                    if len(participants) > 7:
                        if len(self.players_group_finals) == 0:
                            self.sheets.create_sheet(sheet_name, [self.players_group_a, self.players_group_b], ["A", "B"])
                        else:
                            self.sheets.create_sheet(sheet_name, [self.players_group_a, self.players_group_b, self.players_group_finals], ["A", "B", "Finals"])
                    else:
                        self.sheets.create_sheet(sheet_name, self.players_group_none)
                else:
                    self.sheets.create_sheet_empty(sheet_name)
    
                
class CreateTournament(QDialog):
    def __init__(self, sheets):
        super().__init__() 
        self.sheets = sheets
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
            self.sheets.create_sheet(sheet_name)
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
            self.p = ChallongeAPI.add_participant(self.tournament_id, self.player_name.toPlainText())
        except (Exception) as e:
            print("Error adding participant: " + str(e))
    def get_participant(self):
        return self.p


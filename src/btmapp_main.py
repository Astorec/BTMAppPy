from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Classes.player import Player
from Components.btmapp_sheets import BTMAppSheets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QTabWidget

# Username and API Key for Challonge
c_api = ChallongeAPI("", "")
s_api = BTMAppSheets("") # URL from google sheets
participants = []
matches = []

def get_tournament(url):
    return c_api.get_tournament(url)


def get_matches(tournament):
    return c_api.get_matches(tournament.get_id())

def print_matches(self, participants, matches):
    for match in matches:
        p1 = "TBD"
        p2 = "TBD"
        for participant in participants:
            
            if participant.get_id() == match.get_player1_id() or match.get_player1_id() in participant.get_group_player_ids():
                p1 = participant.get_name()
            if participant.get_id() == match.get_player2_id() or match.get_player2_id() in participant.get_group_player_ids():
                p2 = participant.get_name()
            
        print("Match: {} vs {}".format(p1, p2))

def get_participants(tournament_id):
    return c_api.get_participants(tournament_id)
    
def get_players(self):
    players = []
    
    for participant in participants:
        p = Player(participant.get_name(), participant.get_id())
        players.append(p)
        
    return players
        

class BTMAppMain(QMainWindow):

    def __init__(self):        
        tournament = get_tournament("z8w9672g")
        super().__init__()
        uic.loadUi('./src/GUI/main.ui', self)
        
        # Find the QTabWidget
        self.tab_widget = self.findChild(QTabWidget, 'tabWidget')
        if self.tab_widget is None:
            print("Tab Widget not found")
            return
        
        # Get the participants from the API via the Tournament ID
        participants = get_participants(tournament.get_id())
        #players = get_players()
        table_widget = self.findChild(QTableWidget, 'tableWidget')
        if table_widget is None:
            print("Table Widget not found")
            return
        
        table_widget.setColumnCount(3)
        table_widget.setRowCount(len(participants))
        for i in range(0, len(participants)):
            for j in range(0, 3):
                match j:
                    case 0:
                        item = QTableWidgetItem(participants[i].get_name())
                        table_widget.setItem(i, j, item)
                    case 1:
                        checkbox_widget = QWidget()
                        layout = QHBoxLayout(checkbox_widget)
                        layout.addWidget(QCheckBox())
                        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        layout.setContentsMargins(0, 0, 0, 0)
                        checkbox_widget.setLayout(layout)
                        table_widget.setCellWidget(i, 3, checkbox_widget)
                    case 2:                        
                        if participants[i].get_checked_in():
                            item = QTableWidgetItem(participants[i].get_checked_in_at())
                            table_widget.setItem(i, j, item)
                print(f"Row {i} inserted. Player Name {participants[i].get_name()}")
                        
                        
        
        # Print the first object to make sure that we have the correct info    
        #matches = get_matches(tournament.get_id()) 
        #print_matches(participants, matches)  
        #sheet_data = s_api.get_sheet(tournament.get_related_sheet())
    
    
    
if __name__ == '__main__':
    app = QApplication([])
    window = BTMAppMain()
    window.show()
    app.exec()
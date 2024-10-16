from qasync import asyncSlot
from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from Components.btmapp_sheets import BTMAppSheets
from Classes.match import Match
from Classes.participant import Participant
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QScrollArea, QFrame, QGroupBox, QSizePolicy, QSpinBox, QGridLayout, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QInputDialog, QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic, sip
import asyncio

class BracketUI(QWidget):
    
    def __init__(self, parent, service): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        self.tournament = None
        self.bracket_list = self.parent_widget.findChild(QComboBox, 'bracket_list')
        if self.bracket_list is None:
            print("Bracket list not found")
            return
        
        self.bracket_list.addItem("Group A")
        self.bracket_list.addItem("Group B")
        self.bracket_list.addItem("Finals")
        
        self.bracket_list.currentIndexChanged.connect(self.swap_grid)

        self.bracket_label = self.parent_widget.findChild(QLabel, 'bracket_label')

        self.bracket_scroll_area = self.parent_widget.findChild(QScrollArea, 'bracket_scroll_area')
        if self.bracket_scroll_area is None:
            print("Bracket scroll area not found")
            return
        
        self.bracket_contents = self.bracket_scroll_area.findChild(QWidget, 'bracket_contents')
        self.bracket_grid = self.bracket_contents.findChild(QGridLayout, 'bracket_grid')
        self.complete_button = self.parent_widget.findChild(QPushButton, 'finish_btn')
        self.complete_button.clicked.connect(self.execute_complete)

        self.service = service
        
    async def InitUi(self):
        self.config = GetConfig.read_config()
        
        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            self.c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])
          
            current_torunament = self.config['TOURNAMENT_DETAILS']['URL']
            tournament_task = asyncio.create_task(self.c_api.get_tournament(current_torunament))
            self.tournament = await tournament_task
            participants = await self.c_api.get_participants(self.tournament.get_id())
            self.matches = await self.c_api.get_matches(self.tournament.get_id())
            for i in range(self.bracket_grid.count()):
                self.bracket_grid.itemAt(i).widget().deleteLater()

            # Initialize lists to keep references to the widgets
            self.match_widgets_a = []
            self.match_widgets_b = []
            self.match_widgets_finals = []
            self.widgets = []

            # Get the highest and lowest id for the group id from matches
            highest_id = 0
            lowest_id = 0
            for match in self.matches:
                if match.get_group_id() is not None:
                    if match.get_group_id() > highest_id:
                        highest_id = match.get_group_id()
                    if match.get_group_id() < highest_id:
                        lowest_id = match.get_group_id()

            count = 0
            for match in self.matches:
                # init p1 and p2
                self.p1 = None
                self.p2 = None

                try:
                    for participant in participants:
                        if participant.get_id() == match.get_player1_id() or len(participant.get_group_player_ids()) > 0 and participant.get_group_player_ids()[0] == match.get_player1_id():
                            self.p1 = participant
                        if participant.get_id() == match.get_player2_id() or len(participant.get_group_player_ids()) > 0 and participant.get_group_player_ids()[0] == match.get_player2_id():
                            self.p2 = participant
                        if self.p1 is not None and self.p2 is not None:
                            break
                except Exception as e:
                    print("Error getting participants: " + str(e))
                    return

                new_bracket = CreateBracket(match, self.p1, self.p2, BTMAppSheets(self.config['GOOGLE_SHEETS']['URL'], self.service))
                new_bracket.setObjectName("bracket_" + str(count))

                new_bracket.bracket_updated.connect(self.refresh_ui)
                
                if match.get_group_id() == lowest_id:
                    # Add the bracket to the correct group tab
                    self.match_widgets_a.append(new_bracket)               
                    
                elif match.get_group_id() == highest_id:
                    self.match_widgets_b.append(new_bracket)
                else:
                    self.match_widgets_finals.append(new_bracket)

            # order each match widget by round
            self.match_widgets_a.sort(key=lambda x: x.match.get_round())
            self.match_widgets_b.sort(key=lambda x: x.match.get_round())
            self.match_widgets_finals.sort(key=lambda x: x.match.get_round())
            
            
            if self.match_widgets_a and self.match_widgets_b:
                # Make bracket list visible
                self.bracket_list.setVisible(True)
                self.bracket_label.setVisible(True)
                self.create_grid("Group A")
            else:
                self.bracket_list.setVisible(False)
                self.bracket_label.setVisible(False)
                self.create_grid("Finals")
                
            if self.tournament.get_state() == "complete" or self.tournament.get_state() == "pending":
                self.complete_button.setEnabled(False)

    def create_grid(self, group):
        match group:
            case "Group A":
                self.widgets = self.match_widgets_a
            case "Group B":
                self.widgets = self.match_widgets_b
            case "Finals":
                self.widgets = self.match_widgets_finals

        column = 0
        row = 0
        round = 0
        nextRound = False

        for i in range(len(self.widgets)):
            # get the match from the widget
            match = self.widgets[i].match
            
            if match.get_round() != round:
                nextRound = True
                round = match.get_round()
                if column == 2 or column == 1:
                    column = 0
                    row += 2
                self.round_label = QLabel("Round " + str(round))
                self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.bracket_grid.addWidget(self.round_label, row, column, 1, 2)                
                
            if nextRound:
                column = 0
                row += 1
                nextRound = False

            self.bracket_grid.addWidget(self.widgets[i], row, column)
            
            # set cell to same size as widget
            self.bracket_grid.setRowStretch(row, 1)
            self.bracket_grid.setColumnStretch(column, 1)
            column += 1
            if column == 2:
                column = 0
                row += 1

 
        self.bracket_grid.setSpacing(10)
        # Add bracket_grid to contents
        grid_widget = QWidget()
        grid_widget.setLayout(self.bracket_grid)
        
        # Set the grid widget as the content of the scroll area
        self.bracket_scroll_area.setWidget(grid_widget)


        # Make sure scroll area is scrollable
        self.bracket_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.bracket_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        
                        
    def refresh_ui(self):
        self.reset_bracket_ui()
    
    def edit_bracket(self):
        pass

    def swap_grid(self):                
        # Get the selected group
        group = self.bracket_list.currentText()
        self.create_grid(group)
        
        # Hide all other widgets
        if group == "Group A":
            for widget in self.match_widgets_b:
                widget.setVisible(False)
            for widget in self.match_widgets_finals:
                widget.setVisible(False)
            for widget in self.match_widgets_a:
                widget.setVisible(True)
        elif group == "Group B":
            for widget in self.match_widgets_a:
                widget.setVisible(False)
            for widget in self.match_widgets_finals:
                widget.setVisible(False)
            for widget in self.match_widgets_b:
                widget.setVisible(True)
        else:
            for widget in self.match_widgets_a:
                widget.setVisible(False)
            for widget in self.match_widgets_b:
                widget.setVisible(False)
            for widget in self.match_widgets_finals:
                widget.setVisible(True)

    async def reset_bracket_ui(self):
        reset = False
        # Get the information and see if we need to update the UI again
        if self.tournament is not None:
            # Get the matches and see if any of the match states have changed
            matches = await self.c_api.get_matches(self.tournament.get_id())
            for m in matches:
                for widget in self.match_widgets_a:
                    if m.get_id() == widget.match.get_id() and m.get_state() != widget.match.get_state():
                        reset = True
                        break;                        
                for widget in self.match_widgets_b:
                    if m.get_id() == widget.match.get_id() and m.get_state() != widget.match.get_state():
                        reset = True
                        break;
                for widget in self.match_widgets_finals:
                    if m.get_id() == widget.match.get_id() and m.get_state() != widget.match.get_state():
                       reset = True
                       break;

                if reset:
                    break;
            if reset:   
                await self.InitUi()
        else:
            await self.InitUi()

    def delete_widgets(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:  
                    self.delete_widgets(item.layout())
    
    def execute_complete(self):
        self.c_api.finalize_tournament(self.tournament.get_id())
        
        # Hide the edit and complete buttons in the bracket widgets
        for widget in self.match_widgets_a:
            widget.complete_button.setVisible(False)
            widget.edit_button.setVisible(False)
        
        for widget in self.match_widgets_b:
            widget.complete_button.setVisible(False)
            widget.edit_button.setVisible(False)
        
        for widget in self.match_widgets_finals:
            widget.complete_button.setVisible(False)
            widget.edit_button.setVisible(False)
            
        self.complete_button.setEnabled(False)
        
class CreateBracket(QWidget):
    bracket_updated = pyqtSignal()
    def __init__(self, match, p1, p2, sheets):
        super().__init__()
        self.sheets = sheets
        uic.loadUi('./src/GUI/bracket_widget.ui', self)
        self.config = GetConfig.read_config()        
            
        self.bracket_layout = QHBoxLayout()
        self.bracket_layout.setContentsMargins(10, 10, 10, 10)
        self.setMinimumSize(321, 111)
        self.setMaximumSize(321, 111)
        self.bracket_layout.addSpacing(10)  
        
        # Create padding between each bracket
        self.p1_label = self.findChild(QLabel, 'p1_label')
        self.p2_label = self.findChild(QLabel, 'p2_label')
        self.p1_score = self.findChild(QSpinBox, 'p1_score')
        self.p2_score = self.findChild(QSpinBox, 'p2_score')
        
        self.complete_button = self.findChild(QPushButton, 'complete_btn')
        self.complete_button.setVisible(False)
        self.edit_button = self.findChild(QPushButton, 'edit_btn')
        self.edit_button.setVisible(False)
        self.match = match
        self.p1 = p1
        self.p2 = p2
        self.p1_score.setEnabled(False)
        self.p2_score.setEnabled(False)

        self.complete_button.clicked.connect(self.complete_bracket)
        self.edit_button.clicked.connect(self.edit_bracket)
        if self.p1 is not None and self.p2 is not None:
            p1_length = len(self.p1.get_name())
            p2_length = len(self.p2.get_name())

            # Set the length of the label to the longest name
            if p1_length > p2_length:
                self.p1_label.setMinimumWidth(p1_length * 10)
                self.p2_label.setMinimumWidth(p1_length * 10)
            else:
                self.p1_label.setMinimumWidth(p2_length * 10)
                self.p2_label.setMinimumWidth(p2_length * 10)
                
            # Set Padding between labels, scores and buttons
            self.p1_label.setContentsMargins(100, 0, 100, 0)
            self.p2_label.setContentsMargins(100, 0, 100, 0)


        self.create_bracket()

    @asyncSlot()
    async def create_bracket(self):
        try:
            if self.p1 is None:
                self.p1_label.setText("TBD")
            else:
                self.p1_label.setText(self.p1.get_name())

            if self.p2 is None:
                self.p2_label.setText("TBD")        
            else:
                self.p2_label.setText(self.p2.get_name())

            scores = self.match.get_scores()
            if scores is not None:
                scores = scores.split("-")
                # Set the scores
                self.p1_score.setValue(int(scores[0]))
                self.p2_score.setValue(int(scores[1]))
                
            c_api = ChallongeAPI(GetConfig.read_config()['CHALLONGE']['USERNAME'], GetConfig.read_config()['CHALLONGE']['API_KEY'])    
            
            tournament = await c_api.get_tournament(self.match.get_tournament_id())
            if self.match.get_state() == "complete":
                self.complete_button.setVisible(False)
                self.edit_button.setVisible(True)
                self.p1_score.setEnabled(False)
                self.p2_score.setEnabled(False)
            else:
                self.complete_button.setVisible(True)
                self.edit_button.setVisible(False)
                self.p1_score.setEnabled(True)
                self.p2_score.setEnabled(True)
            if tournament.get_state() == "complete":
                self.complete_button.setVisible(False)
                self.edit_button.setVisible(False)
                
        except Exception as e:
            print("Error creating bracket: " + str(e))
            
    @asyncSlot()
    async def complete_bracket(self):
        match = self.match
        
        p1_score = self.p1_score.value()
        p2_score = self.p2_score.value()
        
        if p1_score > p2_score:
            winner = match.get_player1_id()
            loser = match.get_player2_id()
        else:
            winner = match.get_player2_id()
            loser = match.get_player1_id()
            
        tournament_id = match.get_tournament_id()
        completed_match = match.complete_match(winner, loser, p1_score, p2_score)
        
        c_api = ChallongeAPI(GetConfig.read_config()['CHALLONGE']['USERNAME'], GetConfig.read_config()['CHALLONGE']['API_KEY'])
        await asyncio.to_thread(c_api.set_match_scores, tournament_id, completed_match.get_id(), completed_match.get_scores(), winner, loser)
        
        tournament_sheet = await asyncio.to_thread(c_api.get_tournament, GetConfig.read_config()['TOURNAMENT_DETAILS']['URL']).get_related_sheet()
        
        self.bracket_updated.emit()
        self.p1_score.setEnabled(False)
        self.p2_score.setEnabled(False)
        
        winner_name = ""
        loser_name = ""
        participants = await asyncio.to_thread(c_api.get_participants, tournament_id)
        
        for participant in participants:
            if participant.get_id() == winner:
                winner_name = participant.get_name()
            if participant.get_id() == loser:
                loser_name = participant.get_name()
        
        await asyncio.to_thread(self.sheets.update_player, tournament_sheet, winner_name, loser_name)
        
    def edit_bracket(self):
        match = self.match
        c_api = ChallongeAPI(GetConfig.read_config()['CHALLONGE']['USERNAME'], GetConfig.read_config()['CHALLONGE']['API_KEY'])
        
        # get the tournament id
        tournament_id = match.get_tournament_id()
        tournamnet_sheet = c_api.get_tournament(tournament_id).get_related_sheet()
        participants = c_api.get_participants(tournament_id)
        
        winner = ""
        loser = ""
        for participant in participants:
            if participant.get_id() == winner:
                winner_name = participant.get_name()
            if participant.get_id() == loser:
                loser_name = participant.get_name()
        
        
        c_api.undo_match(match.get_tournament_id(), match.get_id())
        self.sheets.undo_update_player(tournamnet_sheet, winner_name, loser_name)
        self.bracket_updated.emit()
        
        self.complete_button.setVisible(True)
        self.edit_button.setVisible(False)
        self.p1_score.setEnabled(True)
        self.p2_score.setEnabled(True)
        self.p1_score.setValue(0)
        self.p2_score.setValue(0)
    
    def update_sheet(self, winner, loser, group = None):
        self.sheets.update_player(winner, loser, group)
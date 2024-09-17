from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from Classes.match import Match
from Classes.participant import Participant
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabWidget, QScrollArea, QFrame, QGroupBox, QSizePolicy, QSpinBox, QGridLayout, QVBoxLayout, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic, sip

class BracketUI(QWidget):
    
    def __init__(self, parent): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        
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


    def InitUi(self):
        print("Bracket UI")

        self.config = GetConfig.read_config()

        if self.config['CHALLONGE']['USERNAME'] != "" or self.config['CHALLONGE']['API_KEY'] != "":
            c_api = ChallongeAPI(self.config['CHALLONGE']['USERNAME'], self.config['CHALLONGE']['API_KEY'])
            current_torunament = self.config['TOURNAMENT_DETAILS']['URL']
            tournament = c_api.get_tournament(current_torunament)
            participants = c_api.get_participants(tournament.get_id())
            self.matches = c_api.get_matches(tournament.get_id())

        
            self.match_widgets_a = []
            self.match_widgets_b = []
            self.match_widgets_finals = []

            # Get the highest and lowest id for the group id from matches
            highest_id = 0
            lowest_id = 0
            for match in self.matches:
                if match.get_group_id() != None:
                
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
                except (Exception) as e:
                    print("Error getting participants: " + str(e))
                    return

                new_bracket = CreateBracket(match, self.p1, self.p2)
                
                new_bracket.setObjectName("bracket_" + str(count))

                if match.get_group_id() == lowest_id:
                    # Add the bracket to the correct group tab
                    self.match_widgets_a.append(new_bracket)
                elif match.get_group_id() == highest_id:
                    self.match_widgets_b.append(new_bracket)
                else:
                    self.match_widgets_finals.append(new_bracket)

            if self.match_widgets_a != None and self.match_widgets_b:
                # Make bracket list visible
                self.bracket_list.setVisible(True)
                self.bracket_label.setVisible(True)
                self.create_grid("Group A")
            else:
                self.bracket_list.setVisible(False)
                self.bracket_label.setVisible(False)
                self.create_grid("Finals")


    def create_grid(self, group):
        for i in reversed(range(self.bracket_grid.count())):
            widgetToRemove = self.bracket_grid.itemAt(i).widget()
            widgetToRemove.setParent(None)
            widgetToRemove.deleteLater()

        match (group):
            case "Group A":
                self.widgets = self.match_widgets_a
            case "Group B":
                self.widgets = self.match_widgets_b
            case "Finals":
                self.widgets = self.match_widgets_finals

        column = 0
        row = 0
        for i in range(0, len(self.widgets)):
            self.bracket_grid.addWidget(self.widgets[i], row, column)
            column += 1
            if column == 2:
                column = 0
            if column == 0:
                row += 1

        self.bracket_scroll_area.setLayout(self.bracket_grid)  # Set layout directly on scroll area
        self.bracket_scroll_area.setWidgetResizable(True)
        self.bracket_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def create_brackets(self, group):
        match(group):
            case "Group A":
                self.match_widgets = self.match_widgets_a
            case "Group B":
                self. match_widgets = self.match_widgets_b
            case "Finals":
                self.match_widgets = self.match_widgets_finals

        # Create or update CreateBracket objects based on matches
        for match in self.matches:
            if len(self.match_widgets) < len(self.matches):
                new_bracket = CreateBracket(match, None, None)
                self.match_widgets.append(new_bracket)

    def swap_grid(self):
        self.create_grid(self.bracket_list.currentText())

    def reset_bracket_ui(self):
        self.InitUi()

    def deleteWidgets(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:  
                    self.deleteWidgets(item.layout())   
   

class CreateBracket(QWidget):
    def __init__(self, Match, p1, p2):
        super().__init__()
        uic.loadUi('./src/GUI/bracket_widget.ui', self)
        self.bracket_layout = QHBoxLayout()
        self.bracket_layout.setContentsMargins(10, 10, 10, 10)
        self.setMinimumSize(213, 76)
        self.setMaximumSize(213, 76)
        self.bracket_layout.addSpacing(10)


        # Create padding between each bracket
        self.p1_label = self.findChild(QLabel, 'p1_label')
        self.p2_label = self.findChild(QLabel, 'p2_label')
        self.p1_score = self.findChild(QSpinBox, 'p1_score')
        self.p2_score = self.findChild(QSpinBox, 'p2_score')
        self.vs_label = self.findChild(QLabel, 'vs_label')
        
        self.complete_button = self.findChild(QPushButton, 'complete_btn')
        self.edit_button = self.findChild(QPushButton, 'edit_btn')
        self.match = Match
        self.p1 = p1
        self.p2 = p2

   
        if self.p1 is not None and self.p2 is not None:

            p1_length = len(self.p1.get_name())
            p2_length = len(self.p2.get_name())
            if p1_length > p2_length:
                self.p2_label.setFixedWidth(p1_length * 10)
            else:
                self.p1_label.setFixedWidth(p2_length * 10)


        self.create_bracket()

    def create_bracket(self):
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
        except (Exception) as e:
            print("Error creating bracket: " + str(e))


        
from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Components.btmapp_get_config import GetConfig
from Classes.match import Match
from Classes.participant import Participant
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabWidget, QScrollArea, QFrame, QGroupBox, QSizePolicy, QSpinBox, QGridLayout, QVBoxLayout, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic

class BracketUI(QWidget):
    
    def __init__(self, parent): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        self.groups_tab = self.parent_widget.findChild(QTabWidget, 'groups_tab')
        if self.groups_tab is None:
            print("Groups tab not found")
            return
        
        self.group_a_tab = self.groups_tab.findChild(QWidget, 'group_a')
        self.group_b_tab = self.groups_tab.findChild(QWidget, 'group_b')
        self.group_finals_tab = self.groups_tab.findChild(QWidget, 'group_finals')

        if self.group_a_tab is None or self.group_b_tab is None or self.group_finals_tab is None:
            print("Group tabs not found")
            return
        

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
                #new_bracket.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

                # DEBUG - make sure the bracket is created
                if new_bracket is None:
                    print("Bracket not created")
                    return

                if match.get_group_id() == lowest_id:
                    # Add the bracket to the correct group tab
                    self.match_widgets_a.append(new_bracket)
                elif match.get_group_id() == highest_id:
                    self.match_widgets_b.append(new_bracket)
                else:
                    self.match_widgets_finals.append(new_bracket)

            if self.match_widgets_a != None and self.match_widgets_b:
                # remove current tab if there is only one
                if self.groups_tab.count() == 1:
                    self.groups_tab.removeTab(0)
                # check if group a and b tabs exist and add them, then set the order of tabs
                if self.group_a_tab is None:
                    self.group_a_tab = QWidget()
                    self.group_a_tab.setObjectName("group_a")
                    self.groups_tab.addTab(self.group_a_tab, "Group A")
                if self.group_b_tab is None:
                    self.group_b_tab = QWidget()
                    self.group_b_tab.setObjectName("group_b")
                    self.groups_tab.addTab(self.group_b_tab, "Group B")
                if self.group_finals_tab is None:
                    self.group_finals_tab = QWidget()
                    self.group_finals_tab.setObjectName("group_finals")
                    self.groups_tab.addTab(self.group_finals_tab, "Finals")

                self.create_grid_a()
                self.create_grid_b()
            else:
                # Remove Group a and B tabs
                self.groups_tab.removeTab(0)
                self.groups_tab.removeTab(0)
                
                # rename finals tab
                self.groups_tab.setTabText(0, "Matches")
            self.create_grid_finals()

    def create_grid_a(self):
        self.scrollAreaWidgetContents_a = QWidget()
        
        self.bracket_grid_a = QGridLayout(self.scrollAreaWidgetContents_a)
        self.bracket_grid_a.setObjectName("bracket_grid")

        # if scroll area is not empty, clear it
        for i in reversed(range(self.bracket_grid_a.count())): 
            self.bracket_grid_a.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.scrollAreaWidgetContents_a.layout().count())):
            self.scrollAreaWidgetContents_a.layout().itemAt(i).widget().setParent(None)

        self.scrollAreaWidgetContents_a.setLayout(self.bracket_grid_a)


        # Ensure the scroll area is resizable
        self.scrollAreaWidgetContents_a.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        column = 0
        row = 0
        for i in range(0, len(self.match_widgets_a)):
            self.bracket_grid_a.addWidget(self.match_widgets_a[i], row, column)
            column += 1
            if column == 2:
                column = 0

            if column == 0:
                row += 1

        self.tmp_layout_a = QHBoxLayout()
        self.tmp_layout_a.addWidget(self.scrollAreaWidgetContents_a)
        self.group_a_tab.findChild(QScrollArea, "group_a_scroll_area").setWidgetResizable(True)
        self.group_a_tab.findChild(QScrollArea, "group_a_scroll_area").setWidget(self.scrollAreaWidgetContents_a)
        self.group_a_tab.findChild(QScrollArea, "group_a_scroll_area").setLayout(self.tmp_layout_a)
        self.group_a_tab.findChild(QScrollArea, "group_a_scroll_area").setAlignment(Qt.AlignmentFlag.AlignCenter)

    def create_grid_b(self):
        self.scrollAreaWidgetContents_b = QWidget()
        
        self.bracket_grid_b = QGridLayout(self.scrollAreaWidgetContents_b)
        self.bracket_grid_b.setObjectName("bracket_grid")

        # reset layouts if they are not empty
        for i in reversed(range(self.bracket_grid_b.count())): 
            self.bracket_grid_b.itemAt(i).widget().setParent(None)
        
        for i in reversed(range(self.scrollAreaWidgetContents_b.layout().count())): 
            self.scrollAreaWidgetContents_b.layout().itemAt(i).widget().setParent(None)

        self.scrollAreaWidgetContents_b.setLayout(self.bracket_grid_b)


        # Ensure the scroll area is resizable
        self.scrollAreaWidgetContents_b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        column = 0
        row = 0
        for i in range(0, len(self.match_widgets_b)):
            self.bracket_grid_b.addWidget(self.match_widgets_b[i], row, column)
            column += 1
            if column == 2:
                column = 0

            if column == 0:
                row += 1

        self.tmp_layout_b = QHBoxLayout()
        self.tmp_layout_b.addWidget(self.scrollAreaWidgetContents_b)
        self.group_b_tab.findChild(QScrollArea, "group_b_scroll_area").setWidgetResizable(True)
        self.group_b_tab.findChild(QScrollArea, "group_b_scroll_area").setWidget(self.scrollAreaWidgetContents_b)
        self.group_b_tab.findChild(QScrollArea, "group_b_scroll_area").setLayout(self.tmp_layout_b)
        self.group_b_tab.findChild(QScrollArea, "group_b_scroll_area").setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def create_grid_finals(self):
        scrollAreaWidgetContents_finals = QWidget()
        
        bracket_grid_finals = QGridLayout(scrollAreaWidgetContents_finals)
        bracket_grid_finals.setObjectName("bracket_grid")

        scrollAreaWidgetContents_finals.setLayout(bracket_grid_finals)


        # Ensure the scroll area is resizable
        scrollAreaWidgetContents_finals.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        column = 0
        row = 0
        for i in range(0, len(self.match_widgets_finals)):
            bracket_grid_finals.addWidget(self.match_widgets_finals[i], row, column)
            column += 1
            if column == 2:
                column = 0

            if column == 0:
                row += 1

        tmp_layout_finals = QHBoxLayout()
        tmp_layout_finals.addWidget(scrollAreaWidgetContents_finals)
        self.group_finals_tab.findChild(QScrollArea, "group_finals_scroll_area").setWidgetResizable(True)
        self.group_finals_tab.findChild(QScrollArea, "group_finals_scroll_area").setWidget(scrollAreaWidgetContents_finals)
        self.group_finals_tab.findChild(QScrollArea, "group_finals_scroll_area").setLayout(tmp_layout_finals)
        self.group_finals_tab.findChild(QScrollArea, "group_finals_scroll_area").setAlignment(Qt.AlignmentFlag.AlignCenter)

    def reset_bracket_ui(self):

        self.InitUi()
   
        


   



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


        
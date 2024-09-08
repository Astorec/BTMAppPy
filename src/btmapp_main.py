from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Classes.player import Player
from GUI.btmapp_players_ui import PlayersUI
from GUI.btmapp_settings_ui import SettingsUI
from Components.btmapp_sheets import BTMAppSheets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow,QVBoxLayout, QTableWidget, QPushButton, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QTabWidget
import os

class BTMAppMain(QMainWindow):

    def __init__(self):        
        super().__init__()
        uic.loadUi('./src/GUI/main.ui', self) 
        
        # Find the QTabWidgetz
        self.tab_widget = self.findChild(QTabWidget, 'tabWidget')
        if self.tab_widget is None:
            print("Tab Widget not found")
            return
        
        # Find the checkin tab
        self.checkin_tab = self.tab_widget.findChild(QWidget, 'checkin_tab')
        if self.checkin_tab is None:
            print("Checkin tab not found")
            return
        
        # Create the Players UI passing in the type qwidget checkin_tab
        self.checkin_ui = PlayersUI(self.checkin_tab)
        self.checkin_ui.InitUi()
        self.settings_tab = self.tab_widget.findChild(QWidget, 'settings_tab')
        if self.settings_tab is None:
            print("Settings tab not found")
            return
        
        self.settings_ui = SettingsUI(self.settings_tab)
        
        # Connect the tab change event
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        
    def on_tab_change(self, index):
        match index:
            case 0:                          
                self.checkin_ui.InitUi()
                print("Checkin Tab")
            case 1:
                print("Bracket Tab")
            case 2:
                print("Leaderboard Tab")
            case 3:
                self.setting_ui.InitUi()
                print("Settings Tab")
    
    
if __name__ == '__main__':
    app = QApplication([])
    window = BTMAppMain()
    window.show()
    app.exec()
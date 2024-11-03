from ChallongeAPI.ChallongeAPI import ChallongeAPI
from Classes.player import Player
from GUI.btmapp_players_ui import PlayersUI
from GUI.btmapp_settings_ui import SettingsUI
from GUI.btmapp_bracket_ui import BracketUI
from GUI.btmapp_leaderboard_ui import LeaderboardUI
from Components.btmapp_sheets import BTMAppSheets
from Components.btmapp_gauth import GAuth
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidget, QPushButton, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QTabWidget
from qasync import QEventLoop, asyncSlot
import os
import asyncio

class BTMAppMain(QMainWindow):

    def __init__(self):        
        super().__init__()

        self.service = GAuth('./src/key.json', ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']).get_service()

        uic.loadUi('./src/GUI/main.ui', self) 
        
        # Find the QTabWidget
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
        self.checkin_ui = PlayersUI(self.checkin_tab, self.service)
        
        self.bracket_tab = self.tab_widget.findChild(QWidget, 'bracket_tab')
        if self.bracket_tab is None:
            print("Bracket tab not found")
            return
        
        self.bracket_ui = BracketUI(self.bracket_tab, self.service)

        self.leaderboard_tab = self.tab_widget.findChild(QWidget, 'leaderboard_tab')
        if self.leaderboard_tab is None:
            print("Leaderboard tab not found")
            return
        
        self.leaderboard_ui = LeaderboardUI(self.leaderboard_tab, self.service)

        self.settings_tab = self.tab_widget.findChild(QWidget, 'settings_tab')
        if self.settings_tab is None:
            print("Settings tab not found")
            return
        
        self.settings_ui = SettingsUI(self.settings_tab)
        
        # Connect the tab change event
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        
    @asyncSlot(int)
    async def on_tab_change(self, index):
        try:
            match index:
                case 0:                       
                    await self.checkin_ui.InitUi()
                case 1:
                    await self.bracket_ui.reset_bracket_ui()
                case 2:
                    await self.leaderboard_ui.InitUi()
                case 3:
                    await self.settings_ui.InitUi()
        except Exception as e:
            print(f"Error in on_tab_change: {e}")
    
    async def initialize_ui(self):
        await self.checkin_ui.InitUi()

async def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = BTMAppMain()
    window.show()
    
    await window.initialize_ui()
    
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    asyncio.run(main())
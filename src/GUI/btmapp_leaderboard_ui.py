from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic
from Components.btmapp_sheets import BTMAppSheets
from Components.btmapp_get_config import GetConfig

class LeaderboardUI(QWidget):
    def __init__(self, parent): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent

    def InitUi(self):
                # Get the config
        self.config = GetConfig.read_config()
        self.sheet_id = self.config['GOOGLE_SHEETS']['URL']

        if self.sheet_id == "Enter your Google Sheets URL here" or self.sheet_id == "":
            self.sheet_id = self.get_sheet_id()
        
        self.sheets = BTMAppSheets(self.sheet_id)

        self.sheet_list = self.parent_widget.findChild(QComboBox, "sheet_cb")
        self.sheet_list.addItems(self.sheets.get_sheet_names())

        self.sheet_list.setCurrentIndex(0)

        self.headers = self.sheets.get_headers(self.sheet_list.currentText())
        # split the headers into columns
        self.table = self.parent_widget.findChild(QTableWidget, "leaderboard_table")
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setRowCount(0)

        self.load_data()

        # Connect the sheet list change event
        self.sheet_list.currentIndexChanged.connect(self.load_data)


    
    def load_data(self):
        # Get Sheet data after the headers
        data = self.sheets.get_sheet(self.sheet_list.currentText())
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        
        # Check to see if the Headers where included in the data and remove them
        if data[0] == self.headers:
            data.pop(0)

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(cell))
    
        

        

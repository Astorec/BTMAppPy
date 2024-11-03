from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QLabel, QComboBox,QDialogButtonBox, QInputDialog,QTableWidgetItem, QCheckBox, QTextEdit, QWidget, QHBoxLayout, QPushButton, QDialog
from PyQt6 import uic
from qasync import asyncSlot
from Components.btmapp_sheets import BTMAppSheets
from Components.btmapp_get_config import GetConfig
from GUI.loading import Loading

class LeaderboardUI(QWidget):
    def __init__(self, parent, service): # Accept parent_widget reference
        super().__init__(parent)
        self.parent_widget = parent
        self.service = service

    @asyncSlot()
    async def InitUi(self):
        # Get the config
        self.config = GetConfig.read_config()
        self.sheet_id = self.config['GOOGLE_SHEETS']['URL']

        if self.sheet_id == "Enter your Google Sheets URL here" or self.sheet_id == "":
            # Display a dialog box to get the Google Sheets URL
            text, ok = QInputDialog.getText(self, 'Google Sheets URL', 'Enter the Google Sheets URL:')
            if ok:
                self.config['GOOGLE_SHEETS']['URL'] = text
                GetConfig.write_config(self.config)
                self.sheet_id = text
        
        loading_dialog = Loading(self)
        loading_dialog.show()
        loading_dialog.update_label("Loading Sheets")
        
        try:
            self.sheets = BTMAppSheets(self.sheet_id, self.service)

            self.sheet_list = self.parent_widget.findChild(QComboBox, "sheet_cb")
            sheet_names = await self.sheets.get_sheet_names()
            self.sheet_list.addItems(sheet_names)

            self.sheet_list.setCurrentIndex(0)

            self.headers = await self.sheets.get_headers(self.sheet_list.currentText())
            # split the headers into columns
            self.table = self.parent_widget.findChild(QTableWidget, "leaderboard_table")
            self.table.setColumnCount(len(self.headers))
            self.table.setHorizontalHeaderLabels(self.headers)
            self.table.setRowCount(0)

            await self.load_data()

            # Connect the sheet list change event
            self.sheet_list.currentIndexChanged.connect(self.load_data)
        except Exception as e:
            print("Error whilst loading sheets: " + str(e))
        finally:
            loading_dialog.close()
        
    
    @asyncSlot()
    async def load_data(self, loading_dialog=None):
        if loading_dialog is not None:
            loading_dialog.update_label("Loading Data")
        # Get Sheet data after the headers
        data = await self.sheets.get_sheet(self.sheet_list.currentText())
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))
        
        # Check to see if the Headers where included in the data and remove them
        if data[0] == self.headers:
            data.pop(0)

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(cell))
    
        

        

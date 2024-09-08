from Components.btmapp_get_config import GetConfig
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLineEdit, QTextEdit, QVBoxLayout, QLabel

class SettingsUI(QWidget):
    def __init__(self, parent_widget):  # Accept parent_widget reference
        super().__init__(parent_widget)  # Call parent constructor
        self.parent_widget = parent_widget  # Store the reference
        self.InitUi()
        
    # Initialize the UI
    def InitUi(self):
        # Get Config
        self.config = GetConfig.read_config()
        for child in self.children():
            print(child.objectName())
              

        self.username_text = self.parent_widget.findChild(QTextEdit, "username_text")
        self.api_text = self.parent_widget.findChild(QTextEdit, "api_text")
        self.sheetid_text = self.parent_widget.findChild(QTextEdit, "sheetid_text")
        self.save_button = self.parent_widget.findChild(QPushButton, "save_button")
        self.save_button.clicked.connect(self.save_config)
        self.saved = self.parent_widget.findChild(QLabel, "saved")
        self.saved.setVisible(False)
        
        
        # Set Username text
        self.username_text.setProperty("placeholderText", self.config['CHALLONGE']['USERNAME'])
        self.api_text.setProperty("placeholderText", self.config['CHALLONGE']['API_KEY'])
        self.sheetid_text.setProperty("placeholderText", self.config['GOOGLE_SHEETS']['URL'])

    def save_config(self):
        if self.username_text.toPlainText() != None:
            self.config['CHALLONGE']['USERNAME'] = self.username_text.toPlainText()
        else:
            self.config['CHALLONGE']['USERNAME'] = "Enter your Challonge username here"

        if self.api_text.toPlainText() != None:
            self.config['CHALLONGE']['API_KEY'] = self.api_text.toPlainText()
        else:
            self.config['CHALLONGE']['API_KEY'] = "Enter your Challonge API key here"

        if self.sheetid_text.toPlainText() != None:
            self.config['GOOGLE_SHEETS']['URL'] = self.sheetid_text.toPlainText()
        else:
            self.config['GOOGLE_SHEETS']['URL'] = "Enter your Google Sheets URL here"

        GetConfig.write_config(self.config)
        self.saved.setVisible(True)
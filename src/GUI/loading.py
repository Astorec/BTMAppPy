from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt

class Loading(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setModal(True)
        
        # Disable the close button
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint)
        
        layout = QVBoxLayout()
        
        # Create a horizontal layout to hold the GIF and the label
        h_layout = QHBoxLayout()
        
        # Create a QLabel to display the GIF
        self.gif_label = QLabel()
        self.movie = QMovie("./src/media/loading.gif") 
        self.gif_label.setMovie(self.movie)
        # Resize the Gif to fit the label
        self.gif_label.setScaledContents(True)
        
        self.movie.start()
        
        # Create a QLabel for the loading message
        self.label = QLabel("Loading, please wait...")
        
        # Add the GIF and the label to the horizontal layout
        h_layout.addWidget(self.gif_label)
        h_layout.addWidget(self.label)
        
        # Add the horizontal layout to the main layout
        layout.addLayout(h_layout)
        
        # Create and add a QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def update_label(self, text):
        self.label.setText(text)
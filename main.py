from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.SETTINGS import *
from src.data.layouts.gui import Ui_MainWindow as GUI
from src.scraper import WebCrawler

import time
import sys

class MainWindow(QMainWindow, GUI):
    # Initialize all views
    initialRun = True

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        super(GUI, self).__init__(*args, **kwargs)
        if self.initialRun:
            self.setupUi(self)
            self.initialRun = False
            self.actionSave.triggered.connect(self.file_save)
            self.actionOpen.triggered.connect(self.file_open)
            self.actionExit.triggered.connect(self.close_application)
            self.actionAbout.triggered.connect(self.about)

            # Preferences
            self.pushFont.clicked.connect(self.font_choice)
            # Fetch style options
            style_keys = QStyleFactory.keys()
            for i in style_keys:
                self.pushStyle.addItem(i)
            self.pushStyle.activated[str].connect(self.style_choice)
            self.show()

    def file_open(self):
        """Tries to open the file into the text editor"""
        name = QFileDialog.getOpenFileName(self, 'Open File')
        try:
            data = open(name[0], 'r')
            with data:
                text = data.read()
                self.textEdit.setText(str(text))
        except FileNotFoundError as e:
            self.textEdit.setText(str(e))
    
    def file_save(self):
        """Saves plain text from the editor to a file format"""
        name = QFileDialog.getSaveFileName(self, 'Save File')
        data = open(name[0], 'w')
        text = self.textEdit.toPlainText()
        data.write(text)
        data.close()

    def about(self):
        print("No time for this now")

    def font_choice(self):
        """Changes font of the application"""
        font, valid = QFontDialog.getFont()
        if valid:
            self.setFont(font)
    
    def style_choice(self, text):
        """Changes window style of the application"""
        QApplication.setStyle(QStyleFactory.create(text))

    
    def close_application(self):
        """Closes application"""
        choice = QMessageBox.question(
            self,
            "Quit!?", "Are you sure?",
            QMessageBox.Yes | QMessageBox.No
        )
        if choice == QMessageBox.Yes:
            print("Have a good day o/")
            sys.exit()
        else:
            print("I knew you liked me <3")
            pass


app = QApplication([])
window = MainWindow()
app.exec_()
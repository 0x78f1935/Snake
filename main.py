from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.data.layouts.gui import Ui_MainWindow as GUI
from src.scraper import WebCrawler
from src.extension import VersionCheck
from src.codecs import Codecs
from src.SETTINGS import *

import concurrent.futures
import multiprocessing
import asyncio
import sys


class MainWindow(QMainWindow, GUI):
    # Initialize all views
    initialRun = True

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        super(GUI, self).__init__(*args, **kwargs)
        if self.initialRun:
            self.setupUi(self)
            self.setWindowIcon(QIcon('src/data/app.png'))  # Set icon along the title

            # Check version
            self.vcheck = VersionCheck(self)
            self.vcheck.check()

            # Initialize others
            self.loop = asyncio.get_event_loop() # Make event async with this loop
            self.scraper = WebCrawler()  # Initalize Scraper
            self.initialRun = False
            self.SPIDER = False
            self.TARGETONLY = False

            # Header bar
            self.actionSave.triggered.connect(self.file_save)
            self.actionOpen.triggered.connect(self.file_open)
            self.actionExit.triggered.connect(self.close_application)
            self.actionAbout.triggered.connect(self.about)
            self.version.setText(self.vcheck._hode(VAPI))

            # Editor
            self.history = ''
            
            # Scraper
            self.pushFetch.clicked.connect(self.run_scraper)
            self.push2Editor.clicked.connect(self.scraper2editor)
            self.advancedSearch.stateChanged.connect(self.trigger_spider)
            self.targetOnly.stateChanged.connect(self.trigger_targetOnly)

            # Codecs
            self.codecs = Codecs(self)
            self.pushDecode.clicked.connect(self.codecs.decodeString)
            self.codecs2editor.clicked.connect(self.copyCodecs2Editor)

            # Preferences
            self.pushFont.clicked.connect(self.font_choice)
            # Fetch style options
            style_keys = QStyleFactory.keys()
            for i in style_keys:
                self.pushStyle.addItem(i)
            self.pushStyle.activated[str].connect(self.style_choice)

        # Codecs
        self.codecs.decodeString()
        # Fetch url
        self.url = self.scraper_input.text()
        # Render
        self.show()



    def file_open(self):
        """Tries to open the file into the text editor"""
        self.tabWidget.setCurrentIndex(0)
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
        self.tabWidget.setCurrentIndex(0)
        name = QFileDialog.getSaveFileName(self, 'Save File')
        try:
            data = open(name[0], 'w')
            text = self.textEdit.toPlainText()
            data.write(text)
            data.close()
        except (FileExistsError, FileNotFoundError):
            pass
        

    def about(self):
        self.vcheck.about()

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
        
    def scraper_pool(self, data, total_percentage):
        total_hits = len(data) # Total links gound, GUI stuff
        percentage = float(len(data) / 100) / 3  # GUI stuff
        # - SPIDER LOGIC
        placeholder = {}
        for url in data:
            if self.TARGETONLY:
                url = str(url).format('https://', '').format('http://', '')
                print(url)
                if str(url) in self.url:
                    # For each result on the last page check again for more links
                    page_result = self.loop.run_until_complete(self.scraper.fetchData(url))
                    placeholder[url] = sorted(list(set(page_result)))  # Store the found data tempory in a placeholder
                    total_hits += len(page_result)
            else:
                page_result = self.loop.run_until_complete(self.scraper.fetchData(url))
                placeholder[url] = sorted(list(set(page_result)))  # Store the found data tempory in a placeholder
                total_hits += len(page_result)

            # Update GUI information
            total_percentage += percentage
            self.scraper_progress.setValue(total_percentage)
            self.scraper_display.display(total_hits)
        return placeholder

    def run_scraper(self):
        # - SCRAPER LOGIC
        results = [] # Final results will be stored here
        # Clear text display and send user a no response warning
        self.scraper_textDisplay.setText(self.vcheck._hode(WAPI))
        self.url = self.scraper_input.text() # Get the user input
        data = self.loop.run_until_complete(self.scraper.fetchData(self.url))  # Get all links on the user selected page
        # - GUI LOGIC
        total_percentage = 0 # GUI stuff
        self.scraper_progress.setValue(total_percentage) # GUI stuff

        # If spider is toggled on, execute advanced search
        if self.SPIDER:
            placeholder = self.scraper_pool(data, total_percentage)
            # Update progressbar to 100% after format loop, but set the var already
            total_percentage = 100
            # Format our fetched data to display
            for key, value in placeholder.items():
                if self.TARGETONLY:
                    url = str(self.url).replace('https://', '').replace('http://', '')
                    if '/' in url:
                        url = url.split('/')[0]
                    if str(url) in key:
                        formats = str("\n\tL---| ".join(value))
                        formats = str(key) + formats
                        results.append(formats)
                else:
                    formats = str("\n\tL---| ".join(value))
                    formats = str(key) + formats
                    results.append(formats)
        else:
            results = data
            total_percentage = 100
            self.scraper_progress.setValue(total_percentage)
            self.scraper_display.display(len(results))
        
        final_format = '\n----\n'.join(sorted(results))

        # Display format
        self.scraper_textDisplay.setText(final_format)
        self.history = final_format
        self.scraper_progress.setValue(total_percentage)

    def scraper2editor(self):
        self.textEdit.setText(self.history)
        self.tabWidget.setCurrentIndex(0)
    
    def copyCodecs2Editor(self):
        self.textEdit.setText(self.codecs.results)
        self.tabWidget.setCurrentIndex(0)
    
    def trigger_spider(self):
        """
        Toggle extended search
        Searches for more in resulted first fetch
        """
        if self.SPIDER == True:
            self.SPIDER = False
        else:
            self.SPIDER = True
        
    def trigger_targetOnly(self):
        """
        Toggle to filter result only on target name
        """
        if self.TARGETONLY == True:
            self.TARGETONLY = False
        else:
            self.TARGETONLY = True


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=4)
    app = QApplication([])
    try:
        pool.map(
            MainWindow(),
            app.exec_()
        )
    except TypeError: # Expect TypeError when clicking X in the top right corner
        pass
    pool.close()

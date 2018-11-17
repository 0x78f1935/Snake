import sys, binascii

from src.SETTINGS import *  # Import easy access settings
from src.data.layouts.editor import Ui_MainWindow as Editor
from src.data.layouts.scraper import Ui_MainWindow as Scraper
from src.data.layouts.options import Ui_MainWindow as Options

from src.scraper import WebCrawler, VersionCheck

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

class Window(QMainWindow):
    def __init__(self, first_time=True):
        super(Window, self).__init__()  # Inherit from QMainWindow
        self.firstimeRun = first_time  # Anti toolbar duplication
        self.k = binascii.unhexlify(VAPI).decode()
        self.g = binascii.unhexlify(API).decode()
        self.setGeometry(50, 50, FRAME_WIDTH, FRAME_HEIGTH) # Set screen resolution
        self.setWindowTitle(APP_NAME) # Set title of the frame
        self.setWindowIcon(QtGui.QIcon('src/data/app.png'))  # Set icon along the title
        
        # Initalize GUI
        self.options = Options()
        self.Ceditor = Editor()
        self.scraper = Scraper()
        # Style choice
        self.styleChoice = QtWidgets.QLabel("Windows Vista", self)
        # Start the editor as first page
        self.editorGUI()
        # Show statusbar as footer
        self.statusBar()
        # Start toolbar
        self.toolbar()
        # Variable to let the user copy results to the editor
        self.history = ''
        # Version check
        V = VersionCheck(self.k, self.g, self)
        V.check()

    def toolbar(self):
        if self.firstimeRun:
            # Toolbar
            self.toolBar = self.addToolBar("Extraction")  # Render toolbar
            # - Editor
            editorAction = QtWidgets.QAction(QtGui.QIcon('src/data/editor.png'), "Editor", self)
            editorAction.triggered.connect(self.editorGUI)  # TODO add scraper
            self.toolBar.addAction(editorAction) # Add items to toolbar
            # - Scraper
            extractAction = QtWidgets.QAction(QtGui.QIcon('src/data/scraper.png'), "Scraper", self)
            extractAction.triggered.connect(self.scraperGUI)  # TODO add scraper
            self.toolBar.addAction(extractAction)  # Add items to toolbar
            # - Options
            optionsAction = QtWidgets.QAction(QtGui.QIcon('src/data/options.png'), "Settings", self)
            optionsAction.triggered.connect(self.optionsGUI)  # TODO add scraper
            self.toolBar.addAction(optionsAction) # Add items to toolbar
            
            # Turn of firstime run to prevent duplications of the toolbar
            self.firstimeRun = False
        self.show()  # Render window

    def editorGUI(self):
        """Open up the editor"""
        self.Ceditor.setupUi(self)
        self.Ceditor.actionExit.setStatusTip(f"Exit application: {APP_NAME}")
        self.Ceditor.actionOptions.setStatusTip(f"Settings for {APP_NAME}")
        self.Ceditor.actionExit.triggered.connect(self.close_application)
        self.Ceditor.actionSave.triggered.connect(self.file_save)
        self.Ceditor.actionOpen.triggered.connect(self.file_open)
        self.Ceditor.actionOptions.triggered.connect(self.optionsGUI)

    def file_open(self):
        """Tries to open the file into the text editor"""
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        try:
            data = open(name[0], 'r')
            # self.editor()  # Loads in the editor
            with data:
                text = data.read()
                self.Ceditor.textEdit.setText(str(text))
        except FileNotFoundError as e:
            self.Ceditor.textEdit.setText(str(e))
    
    def file_save(self):
        """Saves plain text from the editor to a file format"""
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        data = open(name[0], 'w')
        text = self.Ceditor.textEdit.toPlainText()
        data.write(text)
        data.close()

    def scraperGUI(self):
        """Open up the scraper"""
        self.scraper.setupUi(self)
        self.scraper.actionExit.setStatusTip(f"Exit application: {APP_NAME}")
        self.scraper.actionOptions.setStatusTip(f"Settings for {APP_NAME}")
        self.scraper.actionExit.triggered.connect(self.close_application)
        self.scraper.actionOptions.triggered.connect(self.optionsGUI)
        self.scraper.pushButton.clicked.connect(self.webCrawler)
        self.scraper.commandLinkButton.clicked.connect(self.copy2Editor)
        self.scraper.textBrowser.setText(self.history)
    
    def copy2Editor(self):
        self.editorGUI()
        self.Ceditor.textEdit.setText(self.history)

    def webCrawler(self):
        url = self.scraper.lineEdit.text()  # Fetch text from input box
        self.scraper.progressBar.setValue(0) # Reset progress bar
        if 'https://' in str(url) or 'http://' in str(url): # Removes user input junk
            url = str(url).split('://')[1] # Takes the clean version of the url where we can work with
        protocol = self.scraper.checkBox.checkState() # Check whatever protocol should be checked
        if protocol:
            protocol = 'https://'
        else:
            protocol = 'http://'
        url = protocol + str(url)
        crawler = WebCrawler(url=url, protocol=protocol)
        total = 0
        progress = int(int(len(crawler.data)) // 100)
        for item in crawler.data:
            crawler.search(item)
            total += progress
            print(self.scraper.progressBar.value)
            result = "\n".join(crawler.links_found)
            self.scraper.textBrowser.setText(result)
            self.scraper.progressBar.setValue(total)
        self.history = result
        self.scraper.progressBar.setValue(100)

    def close_application(self):
        """Closes application"""
        choice = QtWidgets.QMessageBox.question(
            self,
            "Quit!?", "Are you sure?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if choice == QtWidgets.QMessageBox.Yes:
            print("Have a good day o/")
            sys.exit()
        else:
            print("I knew you liked me <3")
            pass
    
    def optionsGUI(self):
        """Open up the options"""
        self.options.setupUi(self)
        self.options.actionExit.setStatusTip(f"Exit application: {APP_NAME}")
        self.options.actionOptions.setStatusTip(f"Settings for {APP_NAME}")
        self.options.label_3.setText(self.k)
        self.options.actionExit.triggered.connect(self.close_application)
        self.options.btnFont.clicked.connect(self.font_choice)
        # Fetch style options
        style_keys = QtWidgets.QStyleFactory.keys()
        for i in style_keys:
            self.options.comboBox.addItem(i)
        self.options.comboBox.activated[str].connect(self.style_choice)

    def font_choice(self):
        """Changes font of the application"""
        font, valid = QtWidgets.QFontDialog.getFont()
        if valid:
            self.setFont(font)
    
    def style_choice(self, text):
        """Changes window style of the application"""
        self.styleChoice.setText(text)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create(text))



        
def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()
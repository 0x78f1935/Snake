import sys, binascii

from src.SETTINGS import *  # Import easy access settings
from src.data.layouts.editor import Ui_MainWindow as Editor
from src.data.layouts.scraper import Ui_MainWindow as Scraper
from src.data.layouts.options import Ui_MainWindow as Options

from src.scraper import WebCrawler, VersionCheck

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
import threading, re, queue

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
        self._stop_event = threading.Event()

    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

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
        crawlerThread = ThreadWithReturnValue(target=WebCrawler, args=(url, protocol,))
        crawlerThread.start()
        crawler = crawlerThread.join()  # Fetch results from thread
        warning_msg = """
            I'm fully aware the program will freeze any moment now.\n
            Please be aware and have patients. Snake is still running in the background.\n
            -----------------\n
            """
        # crawler = WebCrawler(url=url, protocol=protocol)
        if crawler.data[0].startswith('No search result'):
            self.scraper.textBrowser.setText(crawler.data[0])
            self.scraper.progressBar.setValue(50)
        else:
            total = 0 # Percentage of loading bar
            progress = int(int(len(crawler.data) // 2) // 100)# First section of the loading bar should go until 50 %
            for item in crawler.data: # For each line in the raw source code
                crawler.search(item) # Search for a link
                total += progress # Update the progress bar
                result = "\n".join(crawler.links_found) # Append result to the other results
                self.scraper.textBrowser.setText(warning_msg) # refresh the screen with new information
                self.scraper.progressBar.setValue(total) # Update the progress bar
            self.history = result # Loop ended so we put the final version in our history
            self.scraper.progressBar.setValue(50)  # Put the progressbar at 50% when finished
            
            check_again = [] # This list is going for the second time through the scraper
            without_base_url = []  # This list contains no base urls
            with_base_urls = []  # This list contains base urls
            not_sure = []  # List which include urls we simply not sure about
            
            while len(crawler.links_found): # Keep the loop going aslong there are items in the class
                item = crawler.links_found.pop(0) # pop the first item
                if item.startswith('http'): # Check if it starts with http
                    if len(re.findall(r"\b" + self.scraper.lineEdit.text() + r"\b", item)) > 0: # check if the host url is in there
                        check_again.append(item) # Worth checking again anyways since it starts with a protocol
                        with_base_urls.append(item) # TODO add button for strict search which only allow to search again in this list
                    else:
                        not_sure.append(item) # Not sure what TODO with this..
                elif item.startswith('/'): # If the link starts with a trailing slash its 99% change a extension on the website, worth looking for
                    without_base_url.append(item)  # Just for sort reasons, to keep it clean
                    if url.endswith('/'):
                        url = url[:int(len(url)-1)]
                    item = url + item # create a possible working link
                    check_again.append(item) # Definitly check this new link
            info = (
                f"Items are sorted, Found the following items:\n"
                f"New target pages: {len(check_again)}\n"
                f"Without base url: {len(without_base_url)}\n"
                f"With http base url: {len(with_base_urls)}\n"
                f"Not sure: {len(not_sure)}"
                )
                
            # Release some memory
            crawlerThread.stop()
            del crawlerThread

            warning_msg = warning_msg + info
            self.scraper.textBrowser.setText(warning_msg)  # refresh the screen with new information
            
            # Second run!
            tmpOverview = {}  # Final result
            overview = []

            for url in check_again:  # For each url we want to check again
                # Check protocol type
                protocol = url.split('://')
                if protocol[0] == 'http':
                    protocol = 'http'
                elif protocol[0] == 'https':
                    protocol = 'https'
                # Start new thread
                crawlerThread = ThreadWithReturnValue(target=WebCrawler, args=(url, protocol,))
                crawlerThread.start()
                crawler = crawlerThread.join()  # Fetch results from thread
                for item in crawler.data:
                    crawler.search(item)
                
                links_found = list(sorted(set(crawler.links_found)))
                if len(links_found) > 0:
                    tmpOverview[url] = list(sorted(set(crawler.links_found)))
                    overview.append(tmpOverview)
            
            output = []
            for item in overview:
                for key, value in item.items():
                    output.append("{}: {}\n".format(key, '\n\tL _ _ _ '.join(value)))

            result = '\n'.join(output)
            self.scraper.textBrowser.setText(result)  # refresh the screen with new information
            self.scraper.progressBar.setValue(100)  # Put the progressbar at 100% when finished
            self.history = result
            # Release some memory
            crawlerThread.stop()
            del crawlerThread

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
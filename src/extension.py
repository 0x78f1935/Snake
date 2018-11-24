from src.SETTINGS import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import binascii
import urllib3

class VersionCheck(object):
    def __init__(self, window):
        self.window = window
        self.r_v = ''
        self.c_v = ''
        
    def _hode(self, hode):
        return binascii.unhexlify(hode).decode()
    
    def _fetchData(self):
        """
        Fetches raw data and puts it in a list
        returns string if error
        returns list if success
        """
        http = urllib3.PoolManager()
        try:
            response = http.request('GET', self._hode(GAPI))
        except urllib3.exceptions.MaxRetryError:
            return 'Could not contact update server' # TODO Make popup
        try:
            soup = response.data.decode('utf-8').strip()  # Fetch raw source code
        except UnicodeDecodeError:
            return 'An error has occurred while looking for updates' # TODO Make popup
        return str(soup).split('\n')
    
    def check(self):
        """recent | current"""
        d = self._fetchData()
        r = [self._hode(i[8:].replace("'", "")) for i in d if 'VAPI' in i][0].split('|')
        self.r_v, r_a = r
        self.c_v, c_a = self._hode(VAPI).split('|')
        if self.c_v != self.r_v:
            self.askToUpdate()

    def about(self):
        QMessageBox.information(
            self.window,
            "About!", self._hode(CAPI),
            QMessageBox.Ok
        )

    def askToUpdate(self):
        # Notify there is a update available
        choice = QMessageBox.question(
            self.window,
            "Update!?", "Version {} is available.\nWould you like to update?".format(self.r_v),
            QMessageBox.Yes | QMessageBox.No
        )
        if choice == QMessageBox.No:
            QMessageBox.information(
                self.window,
                "Update!?", "Update can be found on the master branch on github:\ngithub.com/Annihilator708/Snake",
                QMessageBox.Ok
            )
        elif choice == QMessageBox.Yes:
            self.window.textEdit.setText(self._hode(UAPI))
            QMessageBox.information(
                self.window,
                "Update!?", "Update can be found on the master branch on github:\ngithub.com/Annihilator708/Snake",
                QMessageBox.Ok
            )
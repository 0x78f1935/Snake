import base64
import codecs
import binascii
import re
import hashlib

class Codecs(object):

    def __init__(self, window):
        self.window = window
        self.results = ''

    def decodeString(self):
        self.codecs = self.window.codecs_input.text()
        if self.codecs is None or self.codecs == '':
            self.codecs = 'No input given.'

        enters = [x for x in re.split(r'(\w{110})', self.codecs) if x]
        self.codecs = "\n".join(enters)
        self.codecs = self.codecs + '\n'
        lineLength = len(enters)

        if lineLength > 0:
            base64Title = 'Base64:' + str('\n' * lineLength) + '\n'
            bz2Title = 'Bz2:' + str('\n' * lineLength) + '\n'
            dbcsTitle = 'Dbcs:' + str('\n' * lineLength) + '\n'
            quopriTitle = 'Quopri64:' + str('\n' * lineLength) + '\n'
            rot13Title = 'Rot13:' + str('\n' * lineLength) + '\n'

            try:
                base64Str = base64.urlsafe_b64decode(self.codecs).decode('utf8', 'ignore')
            except binascii.Error as e:
                base64Str = e.args[0]
            rot13Str = codecs.encode(self.codecs, 'rot_13')
            if base64Str == '6`':
                base64Str = 'No input given.'
            if rot13Str == 'Ab vachg tvira':
                rot13Str = 'No input given.'

        else:
            base64Title = 'Base64:' + '\n'
            rot13Title = 'Rot13:' + '\n'
            base64Str = 'No input given.\n'
            rot13Str = 'No input given.\n'
        
        self.results = 'Base64:\n' + base64Str + '\n\n' + 'ROT13:\n' + rot13Str
        self.window.title_base64.setText(base64Title)
        self.window.title_rot13.setText(rot13Title)
        self.window.output_base64.setText(base64Str)
        self.window.output_rot13.setText(rot13Str)


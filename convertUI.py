"""
This file has been writen to convert ui files in the folder src/data/layout
to useable format. This way QtDesigner can be used to make the design posibility more faster.
In the future those will be automatically update the program
"""
import os
from os import listdir, getcwd
from os.path import isfile, join
onlyfiles = [f for f in listdir(join(join(join(getcwd(), 'src'), "data"), "layouts")) if f.endswith('.ui')]
for item in onlyfiles:
    location = join(join(join(join(getcwd(), 'src'), "data"), "layouts"), item)
    print(f"python -m PyQt5.uic.pyuic -x {location} -o {str(location)[:-2]}")
    print(os.popen(f"python -m PyQt5.uic.pyuic -x {location} -o {str(location)[:-2]}py").read())
print('Done!')